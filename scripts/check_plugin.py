#!/usr/bin/env python3
"""Validate the package; --live exercises the public, read-only MCP service."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads((ROOT / path).read_text())


def check_package():
    manifest = load('.codex-plugin/plugin.json')
    require(manifest['name'] == 'codex-plugin', 'Unexpected plugin identity')
    require(manifest['version'] == '0.1.1', 'Unexpected version')
    require(manifest['interface']['displayName'] == 'Bot Creator', 'Missing display name')
    for key in ('skills', 'mcpServers'):
        relative = manifest[key]
        require(relative.startswith('./'), f'{key} must be root-relative')
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT) and path.exists(), f'Invalid {key} path')
    portable = load('plugin.json')
    require(portable['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', 'Invalid portable schema')
    for key in ('name', 'version', 'description', 'repository', 'homepage'):
        require(portable[key] == manifest[key], f'Portable/Codex mismatch: {key}')
    require(portable['extensions']['com.openai']['interface'] == manifest['interface'], 'Interface mismatch')
    remote = load('mcp.json')
    require(remote['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json', 'Invalid portable MCP schema')
    require(remote['mcpServers'] == {'bot-creator-docs': {
        'type': 'streamable-http', 'url': 'https://bot-creator.fr/api/mcp'
    }}, 'Unexpected portable transport or authentication')
    skills = list((ROOT / manifest['skills']).glob('*/SKILL.md'))
    require(len(skills) == 1, 'Expected one discoverable skill')
    skill = skills[0].read_text()
    require(skill.startswith('---\n') and '\n---\n' in skill[4:], 'Missing skill frontmatter')
    servers = load(manifest['mcpServers'])['mcpServers']
    require(list(servers) == ['bot-creator-docs'], 'Unexpected bundled servers')
    server = servers['bot-creator-docs']
    require(server == {'url': 'https://bot-creator.fr/api/mcp'}, 'Unexpected endpoint or credentials')
    market = load('.agents/plugins/marketplace.json')
    entry = market['plugins'][0]
    require(entry['name'] == manifest['name'], 'Marketplace identity mismatch')
    require(entry['source']['source'] == 'local', 'Expected a local marketplace')
    require((ROOT / entry['source']['path']).resolve() == ROOT, 'Marketplace must resolve plugin root')
    print('PASS: manifests, paths, skill discovery, public endpoint, local marketplace')
    return server['url']


class MCP:
    def __init__(self, url):
        self.url = url
        self.sequence = 0

    def rpc(self, method, params):
        self.sequence += 1
        request = {'jsonrpc': '2.0', 'id': self.sequence, 'method': method, 'params': params}
        # curl follows the same public HTTP route used by Codex, without credentials.
        output = subprocess.run([
            'curl', '--fail-with-body', '--silent', '--show-error', '--max-time', '20',
            self.url, '-H', 'Content-Type: application/json',
            '-H', 'Accept: application/json, text/event-stream',
            '--data-binary', json.dumps(request),
        ], capture_output=True, text=True, check=True)
        data = json.loads(output.stdout)
        require(data.get('id') == self.sequence, 'Unexpected JSON-RPC response id')
        require('error' not in data, f'JSON-RPC error: {data.get("error")}')
        result = data['result']
        require(not result.get('isError'), f'MCP tool error: {result}')
        return result

    def tool(self, name, arguments):
        result = self.rpc('tools/call', {'name': name, 'arguments': arguments})
        text = '\n'.join(c['text'] for c in result.get('content', []) if c['type'] == 'text')
        require(bool(text), f'Empty result from {name}')
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


def check_live(url):
    mcp = MCP(url)
    init = mcp.rpc('initialize', {
        'protocolVersion': '2025-11-25', 'capabilities': {},
        'clientInfo': {'name': 'bot-creator-plugin-check', 'version': '0.1.0'},
    })
    require(init['serverInfo']['name'] == 'bot-creator', 'Unexpected MCP server')
    # This endpoint is stateless; initialized notifications have no response body.
    subprocess.run(['curl', '-fsS', '--max-time', '20', url,
                    '-H', 'Content-Type: application/json',
                    '-H', 'Accept: application/json, text/event-stream', '--data-binary',
                    json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'})],
                   capture_output=True, text=True, check=True)
    names = {t['name'] for t in mcp.rpc('tools/list', {})['tools']}
    expected = {'get_schema_manifest', 'plan_solution', 'list_actions', 'validate_actions',
                'search_docs', 'get_doc', 'list_posts', 'search_posts', 'get_post'}
    require(expected <= names, 'Missing documentary tools')
    print(f'PASS: initialize and tools/list ({len(names)} tools)')

    docs = mcp.tool('search_docs', {'query': 'sendMessage', 'api_type': 'bdfd', 'limit': 3})
    require(docs.get('count', 0) > 0, 'Function search returned no results')
    doc = mcp.tool('get_doc', {'slug': docs['results'][0]['slug'], 'full_markdown': True})
    require(isinstance(doc, str) and 'Source: https://' in doc, 'Missing full reference/source')
    model = mcp.tool('get_doc', {'slug': 'execution-model', 'full_markdown': True})
    require(isinstance(model, str) and 'Source: https://' in model, 'Missing execution model')
    posts = mcp.tool('list_posts', {'limit': 1})
    require(posts.get('count', 0) > 0, 'No public guides')
    post = mcp.tool('get_post', {'slug': posts['results'][0]['slug']})
    require(isinstance(post, str) and len(post) > 100, 'Empty guide')
    print('PASS: function search, sourced references, execution model, guide reading')

    for mode in ('bdfd', 'blocks'):
        plan = mcp.tool('plan_solution', {'intent': 'Répondre Bonjour à une commande slash', 'mode': mode})
        require(plan.get('decision') in ('auto', 'review', 'ask_user'), 'Invalid planner decision')
        print(f'PASS: French command planning ({mode}, decision={plan["decision"]})')
    schemas = mcp.tool('get_schema_manifest', {'mode': 'blocks', 'names': ['respondWithMessage']})
    require('respondWithMessage' in schemas, 'Missing Blocks response action')
    actions = [{'type': 'respondWithMessage', 'payload': {'content': 'Bonjour !', 'ephemeral': True}}]
    valid = mcp.tool('validate_actions', {'actions': actions})
    require(valid.get('valid') is True and not valid.get('errors'), 'Blocks example failed validation')
    invalid = mcp.tool('validate_actions', {'actions': [{'type': '__nonexistent_action__', 'payload': {}}]})
    require(invalid.get('valid') is False and invalid.get('errors'), 'Validator accepted unknown action')
    print('PASS: Blocks example validation and rejection of an unknown action')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Query the public MCP endpoint (requires curl/network)')
    args = parser.parse_args()
    try:
        endpoint = check_package()
        if args.live:
            check_live(endpoint)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
