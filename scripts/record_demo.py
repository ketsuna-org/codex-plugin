#!/usr/bin/env python3
"""Create a captioned walkthrough of real public MCP calls (not ChatGPT UI)."""
import argparse
import json
from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from check_plugin import MCP

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
args = parser.parse_args()
mcp = MCP('https://bot-creator.fr/api/mcp')
steps = [
 ('1. Public documentation service', 'initialize', {'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'review-demo','version':'1.0'}}),
 ('2. Discover documentation tools', 'tools/list', {}),
 ('3. Search a BDFD function', 'search_docs', {'query':'sendMessage','api_type':'bdfd','limit':1}),
 ('4. Read the execution model', 'get_doc', {'slug':'execution-model','full_markdown':True}),
 ('5. Plan a command example', 'plan_solution', {'intent':'Reply Bonjour privately','mode':'blocks'}),
 ('6. Validate proposed Blocks actions', 'validate_actions', {'actions':[{'type':'respondWithMessage','payload':{'content':'Bonjour !','ephemeral':True}}]}),
]
args.output.parent.mkdir(parents=True,exist_ok=True)
writer=imageio_ffmpeg.write_frames(str(args.output),(1280,720),fps=10,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',output_params=['-movflags','+faststart'])
writer.send(None)
font=ImageFont.load_default(size=22)
heading=ImageFont.load_default(size=34)
try:
 for title, method, params in steps:
  result=mcp.rpc(method,params) if method in ('initialize','tools/list') else mcp.tool(method,params)
  if method=='tools/list': result={'tools':[t['name'] for t in result['tools']]}
  request=json.dumps({'method':method,'arguments':params},ensure_ascii=False,indent=2)
  response=result if isinstance(result,str) else json.dumps(result,ensure_ascii=False,indent=2)
  image=Image.new('RGB',(1280,720),'#101827'); draw=ImageDraw.Draw(image)
  draw.text((40,25),'Bot Creator | Live MCP walkthrough',font=heading,fill='#8bc5ff')
  draw.text((40,80),'Actual public API responses | no account, no bot mutation, no ChatGPT UI',font=font,fill='white')
  draw.text((40,125),title,font=heading,fill='white')
  for x, label, content in ((40, 'REQUEST', request), (660, 'RESPONSE', response)):
   draw.text((x, 185), label, font=font, fill='#8bc5ff')
   lines=[]
   for line in content.splitlines():
    lines.extend(textwrap.wrap(line,width=45) or [''])
   for i,line in enumerate(lines[:16]):
    draw.text((x,225+i*25),line,font=font,fill='#d2e3f7')
  draw.text((40,657),'Responses captured at generation time. Long output shortened to fit the screen.',font=font,fill='#97a8bd')
  frame=image.tobytes()
  for _ in range(120): writer.send(frame)
finally:
 writer.close()
print(args.output)
