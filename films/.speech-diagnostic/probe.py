import asyncio,os,json,ssl,subprocess
from pathlib import Path
import aiohttp,edge_tts
from faster_whisper.utils import download_model
root=Path('films/.speech-diagnostic')
results=[]
async def probe(label,fn):
 try:
  val=await asyncio.wait_for(fn(),20)
  results.append({'test':label,'ok':True,'result':val})
 except Exception as e:
  results.append({'test':label,'ok':False,'error':type(e).__name__,'status':getattr(e,'status',None),'message':getattr(e,'message','')[:180]})
async def main():
 proxy=os.environ['HTTPS_PROXY']
 async def https():
  voices=await edge_tts.list_voices(proxy=proxy)
  return {'voices':len(voices)}
 async def websocket():
  async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as s:
   async with s.ws_connect('wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1',proxy=proxy,ssl=ssl.create_default_context()) as ws:
    return {'handshake':101}
 async def synthesis():
  async for chunk in edge_tts.Communicate('Bonjour, ceci est un test de synthèse vocale.','fr-FR-DeniseNeural',proxy=proxy).stream():
   if chunk['type']=='audio':return {'audio_bytes':len(chunk['data'])}
 await probe('edge_https_library_explicit_proxy',https)
 await probe('edge_websocket_transport_explicit_proxy',websocket)
 await probe('edge_synthesis_library_explicit_proxy',synthesis)
asyncio.run(main())
try:
 download_model('small',output_dir=str(root/'whisper-small-staging'))
 results.append({'test':'whisper_small_download','ok':True})
except Exception as e:results.append({'test':'whisper_small_download','ok':False,'error':type(e).__name__,'message':str(e).split('?')[0][:180]})
(root/'probes.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
