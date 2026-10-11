#!/usr/bin/env python3
"""Build a plugin-only ZIP for the ChatGPT/Codex submission workflow."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from check_plugin import check_package

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    check_package()
    manifest = json.loads((ROOT / 'plugin.json').read_text())
    files = [ROOT / name for name in (
        'plugin.json', 'mcp.json', '.codex-plugin/plugin.json', '.mcp.json'
    )]
    files += sorted(path for path in (ROOT / 'skills').rglob('*') if path.is_file())
    files += sorted(path for path in (ROOT / 'assets').rglob('*') if path.is_file())
    output = ROOT / 'dist' / f'{manifest["name"]}-{manifest["version"]}.zip'
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, f'{manifest["name"]}/{path.relative_to(ROOT).as_posix()}')
    print(output)
