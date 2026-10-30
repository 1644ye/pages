"""Manual GitHub Release updates, staged and verified before activation."""
import hashlib
import io
import json
import re
import shutil
import tempfile
import threading
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

REPO = '1644ye/pages'
ASSET = 'Shopify页面生成器_免安装离线版.zip'
FILES = {'双击打开.html', '使用说明.txt', 'icon-server.py', 'start-icon-tool.cmd', 'updater.py', 'version.json'}
LOCK = threading.Lock()


def version_key(value):
    if not re.fullmatch(r'\d{4}\.\d{2}\.\d{2}(?:\.\d+)?', value):
        raise ValueError('不支持的版本号')
    parts = tuple(map(int, value.split('.')))
    return parts + (0,) * (4 - len(parts))


def github_download(url, limit):
    def validate(target):
        parsed = urllib.parse.urlsplit(target)
        if parsed.scheme != 'https' or parsed.hostname not in {'api.github.com', 'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'}:
            raise ValueError('更新下载地址不属于 GitHub')
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            validate(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    validate(url)
    request = urllib.request.Request(url, headers={'User-Agent': 'PageStudio-Updater', 'Accept': 'application/vnd.github+json'})
    with urllib.request.build_opener(Redirect()).open(request, timeout=30) as response:
        data = response.read(limit + 1)
        if len(data) > limit: raise ValueError('更新包超过大小限制')
        return data


def check(current):
    release = json.loads(github_download(f'https://api.github.com/repos/{REPO}/releases/latest', 1024 * 1024))
    tag = release.get('tag_name', '')
    if release.get('draft') or release.get('prerelease') or not tag.startswith('offline-v'):
        raise ValueError('最新发布不是正式离线版，请前往 GitHub 查看')
    latest = tag.removeprefix('offline-v')
    newer = version_key(latest) > version_key(current)
    asset = next((x for x in release.get('assets', []) if x['name'] == ASSET), None)
    if newer and not asset: raise ValueError('新版本尚未上传完整压缩包，请稍后再试')
    return {'current': current, 'latest': latest, 'available': newer,
            'tag': tag, 'releaseUrl': f'https://github.com/{REPO}/releases/tag/{tag}', 'asset': asset}


def install(root, current, expected_tag):
    if not LOCK.acquire(blocking=False): raise ValueError('已有更新正在进行')
    staging = None
    try:
        release = check(current)
        if not release['available'] or release['tag'] != expected_tag:
            raise ValueError('发布版本已变化或无需更新，请重新检查')
        asset = release['asset']
        digest = asset.get('digest', '')
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', digest or ''):
            raise ValueError('GitHub 未提供 SHA-256 校验值，已停止自动更新')
        url = asset['browser_download_url']
        if not url.startswith(f'https://github.com/{REPO}/releases/download/{release["tag"]}/'):
            raise ValueError('更新包来源不匹配')
        data = github_download(url, 30 * 1024 * 1024)
        if len(data) != asset['size'] or 'sha256:' + hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('更新包校验失败，当前版本保持不变')
        versions = Path(root) / '.updates'
        versions.mkdir(exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='stage-', dir=versions))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = ['Shopify页面生成器/' + name for name in FILES]
            if sorted(archive.namelist()) != sorted(names): raise ValueError('更新包文件结构不匹配')
            if sum(item.file_size for item in archive.infolist()) > 40 * 1024 * 1024: raise ValueError('解压内容过大')
            for name in FILES:
                (staging / name).write_bytes(archive.read('Shopify页面生成器/' + name))
        metadata = json.loads((staging / 'version.json').read_text(encoding='utf-8'))
        if metadata != {'version': release['latest'], 'tag': release['tag']}: raise ValueError('更新包内部版本不匹配')
        for name in ('icon-server.py', 'updater.py'):
            compile((staging / name).read_text(encoding='utf-8'), name, 'exec')
        # Activation is one atomic pointer change; original files and previous version remain intact.
        pointer = Path(root) / '.active-version'
        previous = pointer.read_text(encoding='utf-8') if pointer.exists() else ''
        (Path(root) / '.previous-version').write_text(previous, encoding='utf-8')
        temporary = Path(root) / '.active-version.tmp'
        temporary.write_text(staging.name, encoding='utf-8')
        temporary.replace(pointer)
        staging = None
        return {'version': release['latest'], 'restarting': True}
    finally:
        if staging is not None: shutil.rmtree(staging)
        LOCK.release()


def active_directory(root):
    root = Path(root).resolve()
    pointer = root / '.active-version'
    if not pointer.exists(): return root
    name = pointer.read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'stage-[\w-]+', name): raise ValueError('本地更新指针无效')
    target = (root / '.updates' / name).resolve()
    if target.parent != (root / '.updates').resolve() or not (target / 'icon-server.py').is_file():
        raise ValueError('本地更新目录无效')
    return target
