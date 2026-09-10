"""Local browser acceptance: pip install playwright; playwright install chromium."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parents[1]
URL='http://localhost:8000'
EXPECTED={'tactile':33.58,'vision':25.05,'perturbation':43.71,'bulb':18.33,'nut':96.36,'teleop':105.26}

def main():
 with sync_playwright() as p:
  browser=p.chromium.launch(channel='chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':1440,'height':1000})
  errors=[]; requests=[]
  page.on('pageerror',lambda e: errors.append(str(e)))
  page.on('request',lambda r: requests.append(r.url))
  assert page.goto(URL).status==200
  page.wait_for_load_state('networkidle')
  assert not any('.mp4' in url for url in requests), 'Videos loaded before interaction'
  assert all(url.startswith(URL) for url in requests), 'External dependency'
  assert page.locator('video').count()==6
  assert page.locator('video').first.bounding_box()['y'] < 750
  page.keyboard.press('Tab'); assert page.locator('.skip').evaluate('(e)=>e===document.activeElement')
  page.keyboard.press('Enter'); assert page.url.endswith('#main')
  page.locator('#compare-play').click()
  page.wait_for_function("[...document.querySelectorAll('.comparison video')].every(v => !v.paused && v.currentTime > .2)")
  page.locator('#compare-play').click()
  assert page.locator('.comparison video').evaluate_all('(vs)=>vs.every(v=>v.paused)')
  page.locator('#compare-restart').click()
  page.wait_for_function("[...document.querySelectorAll('.comparison video')].every(v => !v.paused && v.currentTime < 3)")
  page.locator('video').nth(2).evaluate('(v)=>v.play()')
  page.wait_for_function("[...document.querySelectorAll('.comparison video')].every(v=>v.paused)")
  metadata=[]
  for video in page.locator('video').all():
   video.evaluate('(v)=>v.play()')
   page.wait_for_function('(src)=>{const v=[...document.querySelectorAll("video")].find(v=>v.getAttribute("src")===src);return v.readyState>=2 && v.currentTime>0}',arg=video.get_attribute('src'))
   data=video.evaluate('(v)=>({src:v.getAttribute("src"),duration:v.duration,width:v.videoWidth,height:v.videoHeight,muted:v.muted,rate:v.playbackRate,cues:v.textTracks[0].cues.length})')
   slug=Path(data['src']).stem
   assert abs(data['duration']-EXPECTED[slug])<.12,data
   assert data['muted'] and data['rate']==1 and data['cues']>0
   video.evaluate('(v)=>{v.pause();v.currentTime=v.duration*.7}')
   video.evaluate('(v)=>new Promise(resolve=>{if(!v.seeking)resolve();else v.addEventListener("seeked",resolve,{once:true})})')
   # Decode through the actual end, not just metadata or posters.
   video.evaluate('(v)=>{v.currentTime=v.duration-.6;return v.play()}')
   video.evaluate('(v)=>new Promise(resolve=>{if(v.ended)resolve();else v.addEventListener("ended",resolve,{once:true})})')
   assert video.evaluate('(v)=>v.error===null && v.ended')
   metadata.append(data)
  page.locator('video').first.evaluate('(v)=>v.requestFullscreen()')
  assert page.evaluate('document.fullscreenElement!==null')
  page.evaluate('document.exitFullscreen()')
  for anchor in ['tactile','dexterity','teleoperation']:
   page.locator(f'nav a[href="#{anchor}"]').click(); assert page.url.endswith('#'+anchor)
  page.goto(URL);page.screenshot(path=str(ROOT/'review/desktop.png'),full_page=True)
  for width in [390,320,768]:
   page.set_viewport_size({'width':width,'height':844})
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   if width==390: page.screenshot(path=str(ROOT/'review/mobile.png'),full_page=True)
  page.set_viewport_size({'width':1280,'height':900})
  page.add_style_tag(content='html{font-size:200%} body{font-size:32px} h1{font-size:72px} h2{font-size:48px} .caption,.intro,.contribution li{font-size:30px}')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  # Simulate a project URL by forwarding its relative assets to the same server.
  sub=browser.new_page()
  sub.route(URL+'/project/**',lambda route:route.fulfill(response=route.fetch(url=route.request.url.replace('/project/','/'))))
  assert sub.goto(URL+'/project/').status==200
  sub.locator('video').last.evaluate('(v)=>v.play()')
  sub.wait_for_function('document.querySelector("video[src*=teleop]").currentTime>0')
  sub.unroute_all(behavior="ignoreErrors")
  sub.close()
  # A missing video should leave the page and other controls usable.
  fail=browser.new_page();fail.route('**/tactile.mp4',lambda route:route.abort())
  fail.goto(URL);fail.locator('#tactile-video').evaluate('(v)=>v.play().catch(()=>{})')
  fail.locator('.media-error').wait_for();assert fail.locator('.media-error a').get_attribute('href')=='assets/tactile.mp4';fail.close()
  nojs=browser.new_context(java_script_enabled=False);plain=nojs.new_page();plain.goto(URL)
  assert not plain.locator('.comparison-controls').is_visible()
  assert plain.locator('video[controls]').count()==6
  nojs.close()
  browser.close()
  (ROOT/'review/browser-results.json').write_text(json.dumps({'passed':True,'videos':metadata,'checks':['no initial video requests','no external requests','keyboard skip link','comparison play/pause/restart','exclusive playback','all six videos seek and end','captions','fullscreen','anchors','320/390/768 widths','200% text','project subpath','media error','no-JS fallback']},ensure_ascii=False,indent=2))
  print('PASS: 6 full-duration videos; playback, seek, captions, fullscreen, comparison, responsive layout and fallbacks.')
if __name__=='__main__':main()
