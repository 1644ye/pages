"""Local icon extraction service. Python standard library only; no AI or third-party proxy."""
import argparse
import ipaddress
import json
import socket
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import sys
import threading
import subprocess
import time
import zipfile
import updater
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INSTALL_ROOT = ROOT
MAX_BYTES = 5 * 1024 * 1024


def public_url(value):
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Please enter a public http:// or https:// website URL.')
    if parsed.port not in (None, 80, 443):
        raise ValueError('Only standard website ports 80 and 443 are supported.')
    addresses = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == 'https' else 80), type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError('Local and private network addresses are not supported.')
    return urllib.parse.urlunsplit(parsed._replace(fragment=''))


class CheckedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def read_remote(url):
    url = public_url(url)
    # No cookies, credentials, browser profile or third-party proxy is sent.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), CheckedRedirect())
    with opener.open(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 PageStudioIconExtractor/1.0', 'Accept-Encoding': 'identity'}), timeout=15) as response:
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError('Response exceeds the 5 MB limit.')
        return body, response.headers, response.url


class IconParser(HTMLParser):
    def __init__(self, url):
        super().__init__(convert_charrefs=True)
        self.url, self.base, self.links = url, None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'base' and self.base is None and attrs.get('href'):
            self.base = urllib.parse.urljoin(self.url, attrs['href'])
        if tag == 'link':
            rel = (attrs.get('rel') or '').lower().split()
            if any(x in rel for x in ('icon', 'apple-touch-icon', 'apple-touch-icon-precomposed', 'mask-icon')) and attrs.get('href'):
                self.links.append(attrs)

    def results(self):
        results, seen = [], set()
        for attrs in self.links:
            url = urllib.parse.urljoin(self.base or self.url, attrs['href'])
            if urllib.parse.urlsplit(url).scheme not in ('http', 'https') or url in seen:
                continue
            seen.add(url)
            results.append({'url': url, 'kind': attrs.get('rel', 'icon'), 'sizes': attrs.get('sizes', '未标注'), 'type': attrs.get('type', '')})
        if not results:
            results.append({'url': urllib.parse.urljoin(self.url, '/favicon.ico'), 'kind': '默认路径候选（未验证）', 'sizes': '未知', 'type': ''})
        return results[:40]


def image_type(body):
    if body.startswith(b'\x89PNG\r\n\x1a\n'): return 'image/png', 'png'
    if body.startswith(b'\x00\x00\x01\x00'): return 'image/x-icon', 'ico'
    if body.startswith(b'\xff\xd8\xff'): return 'image/jpeg', 'jpg'
    if body.startswith((b'GIF87a', b'GIF89a')): return 'image/gif', 'gif'
    if body.startswith(b'RIFF') and body[8:12] == b'WEBP': return 'image/webp', 'webp'
    # SVG is downloaded as a file and previewed only as an img (never inserted into HTML).
    import xml.etree.ElementTree as ET
    try:
        if ET.fromstring(body).tag in ('svg', '{http://www.w3.org/2000/svg}svg'): return 'image/svg+xml', 'svg'
    except ET.ParseError:
        pass
    raise ValueError('The address did not return a supported image (PNG, ICO, JPG, GIF, WebP or SVG).')


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'dist' if (ROOT / 'dist').exists() else ROOT), **kwargs)

    def do_GET(self):
        if self.path == '/api/version':
            payload = (ROOT / 'version.json').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == '/':
            self.path = '/index.html' if (ROOT / 'dist').exists() else '/' + urllib.parse.quote('双击打开.html')
        return super().do_GET()

    def do_POST(self):
        origin = f'http://127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host') != origin.split('//')[1] or self.headers.get('Origin') != origin or self.headers.get_content_type() != 'application/json':
            self.send_error(403)
            return
        try:
            if self.path not in ('/api/icons', '/api/icon-file', '/api/update-check', '/api/update-install'):
                self.send_error(404)
                return
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192: raise ValueError('Invalid request size.')
            request = json.loads(self.rfile.read(length))
            if self.path.startswith('/api/update-'):
                current = json.loads((ROOT / 'version.json').read_text(encoding='utf-8'))['version']
                if self.path == '/api/update-check':
                    result = updater.check(current)
                    result.pop('asset', None)
                else:
                    result = updater.install(INSTALL_ROOT, current, request['tag'])
                payload = json.dumps(result).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                if self.path == '/api/update-install':
                    self.server.restart_requested = True
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            url = request['url']
            body, headers, final_url = read_remote(url)
            if self.path == '/api/icons':
                if headers.get_content_type() not in ('text/html', 'application/xhtml+xml'):
                    raise ValueError('The website did not return an HTML page.')
                parser = IconParser(final_url)
                parser.feed(body.decode(headers.get_content_charset() or 'utf-8', errors='replace'))
                payload = json.dumps({'page': final_url, 'icons': parser.results()}).encode()
                mime = 'application/json'
            else:
                mime, ext = image_type(body)
                payload = body
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            if self.path == '/api/icon-file': self.send_header('X-Icon-Extension', ext)
            self.end_headers()
            self.wfile.write(payload)
        except (ValueError, KeyError, OSError, urllib.error.URLError, LookupError, zipfile.BadZipFile, SyntaxError) as error:
            payload = json.dumps({'error': str(error)}).encode()
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--install-root', default=str(ROOT))
    args = parser.parse_args()
    INSTALL_ROOT = Path(args.install_root).resolve()
    active = updater.active_directory(INSTALL_ROOT)
    if active != ROOT:
        sys.exit(subprocess.call([sys.executable, str(active / 'icon-server.py'), '--install-root', str(INSTALL_ROOT), '--port', str(args.port)] + (['--no-browser'] if args.no_browser else [])))
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        server.restart_requested = False
        address = f'http://127.0.0.1:{server.server_port}/'
        print('Page Studio: ' + address + '\nKeep this window open. Ctrl+C to stop.', flush=True)
        if not args.no_browser: webbrowser.open(address)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
    if server.restart_requested:
        active = updater.active_directory(INSTALL_ROOT)
        child = subprocess.Popen([sys.executable, str(active / 'icon-server.py'), '--install-root', str(INSTALL_ROOT), '--port', str(server.server_port), '--no-browser'])
        healthy = False
        for _ in range(30):
            if child.poll() is not None: break
            try:
                with urllib.request.urlopen(address + 'api/version', timeout=1) as response:
                    healthy = json.load(response) == json.loads((active / 'version.json').read_text(encoding='utf-8'))
                if healthy: break
            except (OSError, ValueError): pass
            time.sleep(.5)
        if healthy:
            child.wait()
        else:
            child.terminate()
            child.wait()
            previous = (INSTALL_ROOT / '.previous-version').read_text(encoding='utf-8')
            pointer = INSTALL_ROOT / '.active-version'
            if previous: pointer.write_text(previous, encoding='utf-8')
            else: pointer.unlink(missing_ok=True)
            sys.exit(subprocess.call([sys.executable, str(ROOT / 'icon-server.py'), '--install-root', str(INSTALL_ROOT), '--port', str(server.server_port), '--no-browser']))
