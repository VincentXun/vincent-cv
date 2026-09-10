"""Dependency-free publication allowlist, link and media integrity checks."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import struct

ROOT = Path(__file__).resolve().parents[1] / 'public'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=[]; self.videos=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        for key in ('src','href','poster'):
            if key in a: self.links.append(a[key])
        if tag=='video': self.videos.append(a)

def atoms(path):
    result=[]
    with path.open('rb') as f:
        while data:=f.read(8):
            assert len(data)==8
            size,kind=struct.unpack('>I4s',data)
            if size==1: size=struct.unpack('>Q',f.read(8))[0]; header=16
            else: header=8
            result.append(kind)
            if size==0: break
            assert size>=header
            f.seek(size-header,1)
    return result

def main():
    html=(ROOT/'index.html').read_text()
    page=Page();page.feed(html)
    assert len(page.ids)==len(set(page.ids)), 'Duplicate anchors'
    for link in page.links:
        u=urlsplit(link)
        if u.scheme: continue
        assert not u.path.startswith('/'), f'Not subpath-safe: {link}'
        if u.path: assert (ROOT/unquote(u.path)).is_file(), f'Missing asset: {link}'
        if u.fragment: assert u.fragment in page.ids, f'Missing anchor: {link}'
    assert 5 <= len(page.videos) <= 6
    for video in page.videos:
        assert all(key in video for key in ('controls','muted','playsinline','poster'))
        assert video.get('preload')=='none' and 'autoplay' not in video
    allowed={'.html','.css','.js','.jpg','.mp4','.vtt'}
    files=list(ROOT.rglob('*'))
    for file in files:
        assert not file.is_symlink()
        if file.is_file():
            assert file.name=='.nojekyll' or file.suffix in allowed, f'Unexpected public file: {file}'
            if file.suffix=='.mp4':
                types=atoms(file); assert types.index(b'moov')<types.index(b'mdat'), f'Not faststart: {file}'
    assert not any(term in html for term in ('150-1565','2308919367','@qq.com','.pdf','.docx','参与度','checkpoint'))
    total=sum(p.stat().st_size for p in files if p.is_file())
    assert total < 1024**3
    print(f'PASS: {len(page.videos)} players, all links and faststart media valid; public size {total/1048576:.2f} MiB')

if __name__=='__main__': main()
