"""Render app icons (icons/*.png) from the in-game monster art. Usage: python3 tools/make_icons.py"""
import asyncio, base64, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto(ROOT.joinpath('dist', 'test.html').as_uri()); await pg.wait_for_function('window.__t', timeout=20000)
        for size in (512, 192, 180):
            for maskable in (False, True):
                if size == 180 and maskable: continue
                url = await pg.evaluate("""([S,mask])=>{const c=document.createElement('canvas');c.width=c.height=S;const g=c.getContext('2d');g.imageSmoothingEnabled=false;
                  const r=mask?0:S*.18;g.beginPath();g.roundRect(0,0,S,S,r);g.clip();
                  const gr=g.createLinearGradient(0,0,0,S);gr.addColorStop(0,'#9fdcff');gr.addColorStop(.58,'#d8f2ff');gr.addColorStop(.58,'#7cc85a');gr.addColorStop(1,'#4c9a3a');g.fillStyle=gr;g.fillRect(0,0,S,S);
                  g.fillStyle='rgba(0,0,0,.18)';g.beginPath();g.ellipse(S/2,S*.8,S*.3,S*.06,0,0,7);g.fill();
                  const k=mask?.62:.8,w=S*k;g.drawImage(__t.ART.happaru.img,(S-w)/2,S*.86-w,w,w);return c.toDataURL('image/png')}""", [size, maskable])
                name = f"icon-{size}{'-maskable' if maskable else ''}.png" if size != 180 else 'apple-touch-icon.png'
                ROOT.joinpath('icons', name).write_bytes(base64.b64decode(url.split(',')[1]))
        await b.close()
    print('icons written')
asyncio.run(main())
