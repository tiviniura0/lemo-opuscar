// Per-command preload for the existing project renderers; no tracked edits.
// Usage: node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs ...
import {chromium} from 'playwright-core';
import fs from 'node:fs';
process.env.PLAYWRIGHT_CHROME='/usr/bin/chromium';
process.env.CHROME_PATH='/usr/bin/chromium';
process.env.CHROME='/usr/bin/chromium';
process.env.LEMO_ANGLE='swiftshader';
const original=chromium.launch.bind(chromium);
const forbidden=/^--(?:no-sandbox|disable-setuid-sandbox|disable-seccomp-filter-sandbox|disable-namespace-sandbox)(?:=|$)/;
chromium.launch=async function(options={}) {
  if((options.args||[]).some(arg=>forbidden.test(arg))) throw new Error('Sandbox-disabling argument refused');
  const browser=await original({...options,executablePath:'/usr/bin/chromium',chromiumSandbox:true,timeout:Math.min(options.timeout||15000,15000),args:[...(options.args||[]),'--disable-background-networking']});
  try {
    const cdp=await browser.newBrowserCDPSession();
    const processes=await cdp.send('SystemInfo.getProcessInfo');
    const main=processes.processInfo.find(p=>p.type==='browser');
    const command=fs.readFileSync(`/proc/${main.id}/cmdline`,'utf8').split('\0');
    if(command.some(arg=>forbidden.test(arg))) throw new Error('Unexpected sandbox-disabling argument');
    const record={version:browser.version(),executable:fs.readlinkSync(`/proc/${main.id}/exe`),chromiumSandbox:true};
    if(!record.version.startsWith('155.')) throw new Error('Unexpected Chromium version');
    console.log('CHROMIUM_VALIDATED '+JSON.stringify(record));
    await cdp.detach();
    return browser;
  } catch(error) {await browser.close();throw error;}
};
