import hashlib
import io
import json
import tempfile
import unittest
import zipfile
import subprocess
import sys
import socket
import time
import urllib.request
from pathlib import Path
from unittest.mock import patch
import updater


class UpdateTests(unittest.TestCase):
    def package(self, extra=None, internal='2026.10.31.1'):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            for name in updater.FILES:
                body = 'pass' if name.endswith('.py') else 'test'
                if name == 'version.json': body = json.dumps({'version': internal, 'tag': 'offline-v' + internal})
                archive.writestr('Shopify页面生成器/' + name, body)
            if extra: archive.writestr(extra, 'bad')
        return buffer.getvalue()

    def release(self, data):
        return {'available': True, 'latest': '2026.10.31.1', 'tag': 'offline-v2026.10.31.1', 'asset': {
            'size': len(data), 'digest': 'sha256:' + hashlib.sha256(data).hexdigest(),
            'browser_download_url': 'https://github.com/1644ye/pages/releases/download/offline-v2026.10.31.1/app.zip'}}

    def test_success_stages_and_retains_previous_version(self):
        data = self.package()
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder, patch.object(updater, 'check', return_value=self.release(data)), patch.object(updater, 'github_download', return_value=data):
            root = Path(folder)
            (root / 'keep.txt').write_text('original')
            updater.install(root, '2026.10.30.2', 'offline-v2026.10.31.1')
            self.assertTrue((updater.active_directory(root) / '双击打开.html').exists())
            self.assertEqual((root / 'keep.txt').read_text(), 'original')
            self.assertEqual((root / '.previous-version').read_text(), '')

    def test_corrupt_archive_traversal_and_wrong_version_leave_original(self):
        for data, corrupt in [(self.package(), True), (self.package('../outside'), False), (self.package(internal='2026.10.30.2'), False)]:
            with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder, patch.object(updater, 'check', return_value=self.release(data)), patch.object(updater, 'github_download', return_value=data + b'corrupt' if corrupt else data):
                with self.assertRaises(ValueError): updater.install(folder, '2026.10.30.2', 'offline-v2026.10.31.1')
                self.assertFalse((Path(folder) / '.active-version').exists())

    def test_changed_release_does_not_install(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder, patch.object(updater, 'check', return_value=self.release(self.package())):
            with self.assertRaises(ValueError): updater.install(folder, '2026.10.30.2', 'offline-v2026.10.31.2')

    def test_no_downgrade_or_repeat(self):
        response = json.dumps({'tag_name': 'offline-v2026.10.29', 'assets': []}).encode()
        with patch.object(updater, 'github_download', return_value=response):
            self.assertFalse(updater.check('2026.10.30.2')['available'])
            self.assertFalse(updater.check('2026.10.29')['available'])
        self.assertGreater(updater.version_key('2026.10.30.20'), updater.version_key('2026.10.30.2'))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows launcher integration')
    def test_service_restarts_and_rolls_back_failed_start(self):
        source = Path(__file__).resolve().parent
        for broken in (False, True):
            with tempfile.TemporaryDirectory(dir=source) as folder:
                root = Path(folder)
                for name in updater.FILES:
                    path = source / name
                    body = path.read_bytes() if path.exists() else b'<!doctype html>test'
                    (root / name).write_bytes(body)
                package = io.BytesIO()
                with zipfile.ZipFile(package, 'w') as archive:
                    for name in updater.FILES:
                        body = (root / name).read_bytes()
                        if name == 'version.json': body = json.dumps({'version': '2026.10.31.1', 'tag': 'offline-v2026.10.31.1'}).encode()
                        if name == 'icon-server.py' and broken: body = b'raise RuntimeError("Simulated startup failure")'
                        archive.writestr('Shopify页面生成器/' + name, body)
                (root / 'test.zip').write_bytes(package.getvalue())
                (root / 'release.json').write_text(json.dumps(self.release(package.getvalue())))
                with socket.socket() as listener:
                    listener.bind(('127.0.0.1', 0)); port = listener.getsockname()[1]
                bootstrap = "import updater,json,runpy;from pathlib import Path;updater.check=lambda current:json.loads(Path('release.json').read_text());updater.github_download=lambda url,limit:Path('test.zip').read_bytes();runpy.run_path('icon-server.py',run_name='__main__')"
                process = subprocess.Popen([sys.executable, '-c', bootstrap, '--no-browser', '--port', str(port)], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                address = f'http://127.0.0.1:{port}'
                def current():
                    try:
                        with urllib.request.urlopen(address + '/api/version', timeout=.5) as response: return json.load(response)['version']
                    except OSError: return None
                try:
                    for _ in range(60):
                        if current(): break
                        time.sleep(.1)
                    self.assertEqual(current(), '2026.10.30.2')
                    request = urllib.request.Request(address + '/api/update-install', data=b'{"tag":"offline-v2026.10.31.1"}', headers={'Origin': address, 'Content-Type': 'application/json'})
                    with urllib.request.urlopen(request, timeout=10) as response: self.assertTrue(json.load(response)['restarting'])
                    for _ in range(100):
                        value = current()
                        if (not broken and value == '2026.10.31.1') or (broken and not (root / '.active-version').exists() and value == '2026.10.30.2'): break
                        time.sleep(.1)
                    self.assertEqual(current(), '2026.10.30.2' if broken else '2026.10.31.1')
                    self.assertEqual((root / '.active-version').exists(), not broken)
                finally:
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
                    process.wait(timeout=10)


if __name__ == '__main__': unittest.main()

