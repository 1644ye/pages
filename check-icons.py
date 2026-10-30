import importlib.util
import unittest
import json
import threading
import urllib.request
import urllib.error
from email.message import Message
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('icons', 'icon-server.py')
icons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(icons)


class IconTests(unittest.TestCase):
    def test_relative_base_duplicates_and_unsafe_links(self):
        parser = icons.IconParser('https://example.com/shop/page')
        parser.feed('''<base href="https://cdn.example.com/assets/">
            <link rel="shortcut ICON" href="logo.png?a=1&amp;b=2" sizes="32x32">
            <link rel="icon" href="logo.png?a=1&amp;b=2">
            <link rel="apple-touch-icon" href="/touch.png">
            <link rel="mask-icon" href="//cdn.example.com/mask.svg">
            <link rel="icon" href="javascript:alert(1)">''')
        result = parser.results()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['url'], 'https://cdn.example.com/assets/logo.png?a=1&b=2')
        self.assertEqual(result[1]['url'], 'https://cdn.example.com/touch.png')

    def test_fallback_is_marked_unverified(self):
        result = icons.IconParser('https://example.com/sub/page').results()[0]
        self.assertEqual(result['url'], 'https://example.com/favicon.ico')
        self.assertIn('未验证', result['kind'])

    def test_private_addresses_and_protocols_are_rejected(self):
        for url in ['file:///etc/passwd', 'ftp://example.com/a', 'https://user:pass@example.com', 'http://example.com:8080']:
            with self.assertRaises(ValueError): icons.public_url(url)
        with patch.object(icons.socket, 'getaddrinfo', return_value=[(0, 0, 0, '', ('127.0.0.1', 80))]):
            with self.assertRaises(ValueError): icons.public_url('http://localhost/')

    def test_image_response_validation(self):
        self.assertEqual(icons.image_type(b'\x89PNG\r\n\x1a\nabc')[1], 'png')
        self.assertEqual(icons.image_type(b'<svg xmlns="http://www.w3.org/2000/svg"/>')[1], 'svg')
        with self.assertRaises(ValueError): icons.image_type(b'<html>Access denied</html>')

    def test_local_service_api_and_origin_check(self):
        headers = Message()
        headers['Content-Type'] = 'text/html; charset=utf-8'
        server = icons.ThreadingHTTPServer(('127.0.0.1', 0), icons.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f'http://127.0.0.1:{server.server_port}'
        try:
            with patch.object(icons, 'read_remote', return_value=(b'<link rel="icon" href="/logo.png">', headers, 'https://example.com/')):
                request = urllib.request.Request(origin + '/api/icons', data=json.dumps({'url': 'https://example.com'}).encode(), headers={'Content-Type': 'application/json', 'Origin': origin})
                with urllib.request.urlopen(request) as response:
                    self.assertEqual(json.load(response)['icons'][0]['url'], 'https://example.com/logo.png')
                request.add_header('Origin', 'https://unrelated.example')
                with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(request)
                self.assertEqual(error.exception.code, 403)
            with urllib.request.urlopen(origin) as response:
                self.assertIn(b'id="extractIcons"', response.read())
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__': unittest.main()
