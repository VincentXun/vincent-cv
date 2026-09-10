"""Local-only static preview with byte-range support for video seeking."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1] / 'public'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def send_head(self):
        path = Path(self.translate_path(self.path))
        self.byte_range = None
        if not path.resolve().is_relative_to(ROOT.resolve()):
            self.send_error(403)
            return None
        header = self.headers.get('Range')
        if not header or not path.is_file():
            return super().send_head()
        total = path.stat().st_size
        match = re.fullmatch(r'bytes=(\d+)-(\d*)', header)
        if not match:
            self.send_error(416)
            return None
        start = int(match[1]); end = min(int(match[2]) if match[2] else total - 1, total - 1)
        if start > end:
            self.send_response(416); self.send_header('Content-Range', f'bytes */{total}'); self.end_headers()
            return None
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Content-Range', f'bytes {start}-{end}/{total}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        self.byte_range = (start, end)
        handle = path.open('rb'); handle.seek(start)
        return handle
    def copyfile(self, source, outputfile):
        try:
            if self.byte_range is None:
                return super().copyfile(source, outputfile)
            remaining = self.byte_range[1] - self.byte_range[0] + 1
            while remaining:
                data = source.read(min(65536, remaining))
                if not data: break
                outputfile.write(data); remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    print(f'Preview: http://localhost:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
