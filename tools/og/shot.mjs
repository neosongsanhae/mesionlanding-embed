// 사용: 저장소 맨 위에서 python3 -m http.server 8900 을 띄운 뒤
//   node tools/og/shot.mjs og-index og-general ...   (이름 없으면 tools/og/*.html 전부)
// playwright-core와 크롬(Chromium) 경로는 각자 환경에 맞게 CHROME 값을 바꿔 쓰세요.
import { chromium } from "/Users/uneedcomms/.argus/mesion_crm/node_modules/playwright-core/index.mjs";
import { readdirSync } from "node:fs";
import { join } from "node:path";
const CHROME = process.env.CHROME || join(process.env.HOME,"Library/Caches/ms-playwright/chromium-1134/chrome-mac/Chromium.app/Contents/MacOS/Chromium");
const names = process.argv.slice(2).length ? process.argv.slice(2) : readdirSync('tools/og').filter(f=>f.endsWith('.html')).map(f=>f.replace('.html',''));
const b = await chromium.launch({ executablePath: CHROME });
const p = await (await b.newContext({ viewport:{width:1200,height:630} })).newPage();
for (const n of names){
  await p.goto(`http://localhost:8900/tools/og/${n}.html`,{waitUntil:'networkidle'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  await p.screenshot({path:`creatives/${n}.png`}); console.log('saved creatives/'+n+'.png');
}
await b.close();
