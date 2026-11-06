import {chromium} from 'playwright-core';
import fs from 'node:fs';
const original=chromium.launch.bind(chromium);
chromium.launch=async function(options){
  if(options?.executablePath!=='/usr/bin/chromium')throw new Error('Unexpected Chromium executable path');
  const browser=await original(options);
  const session=await browser.newBrowserCDPSession();
  const version=await session.send('Browser.getVersion');
  const processes=await session.send('SystemInfo.getProcessInfo');
  const main=processes.processInfo.find(p=>p.type==='browser');
  const exe=main?fs.readlinkSync(`/proc/${main.id}/exe`):null;
  const record={entrypoint:process.argv[1],requested:options.executablePath,version:browser.version(),product:version.product,pid:main?.id,actual_executable:exe};
  fs.appendFileSync(new URL('./chromium-launches.jsonl',import.meta.url),JSON.stringify(record)+'\n');
  await session.detach();
  if(!browser.version().startsWith('155.')){await browser.close();throw new Error('Unexpected Chromium version');}
  if(process.env.LEMO_AUDIT_LAUNCH_ONLY==='1'){await browser.close();process.exit(0);}
  return browser;
};
