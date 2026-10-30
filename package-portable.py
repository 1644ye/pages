from pathlib import Path
from html import escape
from html.parser import HTMLParser
import re
import zipfile
import sys
import json

# Windows CI and non-Chinese terminals may default to an encoding without CJK.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

root = Path(__file__).resolve().parent
dist = root / 'dist'
version = json.loads((root / 'version.json').read_text(encoding='utf-8'))
assert version['tag'] == 'offline-v' + version['version']
assert "const APP_VERSION='" + version['version'] + "';" in (dist / 'update.js').read_text(encoding='utf-8')
output = root / 'portable'
output.mkdir(exist_ok=True)
page = (dist / 'index.html').read_text(encoding='utf-8')
page = re.sub(r'<link rel="stylesheet" href="style\.css[^\"]*">', lambda _: '<style>' + (dist / 'style.css').read_text(encoding='utf-8') + '</style>', page)
contact = (dist / 'contact.html').read_text(encoding='utf-8')
page = page.replace('src="contact.html"', 'srcdoc="' + escape(contact, quote=True) + '"')
for name in ['contact-template.js', 'generator.js', 'xlsx.js', 'app.js', 'prompt.js', 'icons.js', 'update.js', 'doubao.js']:
    script = (dist / name).read_text(encoding='utf-8')
    # HTML parsers close script elements even when the closing tag occurs in a JS string.
    script = re.sub(r'</script', lambda _: r'<\/script', script, flags=re.I)
    page = re.sub(r'<script src="' + re.escape(name) + r'[^\"]*"></script>', lambda _: '<script>\n' + script + '\n</script>', page)
assert not re.search(r'<(?:script|iframe)\b[^>]*\bsrc=|<link\b', page, re.I)
assert 'XMLHttpRequest' not in page
assert 'C:/Users/' not in page and 'api.openai.com' not in page
html_path = output / '双击打开.html'
html_path.write_text(page, encoding='utf-8', newline='')
instructions = '''Shopify 页面生成器 · 免安装离线版

使用方法
1. 先把压缩包完整解压到一个文件夹。
2. 双击“ 双击打开.html ”，使用 Chrome、Edge、Firefox 或 Safari 等现代桌面浏览器打开。
   如果被文本编辑器打开，请右键文件 → 打开方式 → 选择浏览器。
3. 填写参考描述的标题和内容、最高折扣（品牌名称选填，仅用于 SEO 和提示词）。
   联系邮箱和文案日期默认空白，均为选填。
4. 点击“本地生成页面”，检查内容后下载 Pages-and-Menus.xlsx。
5. 在 Shopify 使用 Matrixify 导入整个 Excel，其中包含 Pages 和 Menus 两张表。

无需安装 Python、Node.js 或其他运行环境，无需 API Key。
全部资源已嵌入 HTML，断网也能生成和导出；可以单独转发这个 HTML 文件。
生成使用内置英文模板与关键词匹配，不调用 AI，不会自动理解或翻译任意文字。
日期为空时使用通用公告；邮箱为空时使用 Contact Us 帮助入口。

首页与 SEO 提示词
- 页面下方可多选 12 个内容项目（包含尺码表），展开下拉框后顶部可全选或取消全选。
- 可选填写 SEO 信息和源网址，可勾选折扣、免运费、产品特色等重点。
- 点击“生成提示词并复制”，自动带入当前品牌、描述和折扣并复制到剪贴板。
- 全程本地拼接，不调用 AI，不抓取网址。如浏览器拒绝复制，可手动复制显示的文本。

豆包对话
- 一键生成并复制提示词仍保留，旁边点击“打开豆包对话”展开官网面板，默认收起且不联网加载。
- 在豆包输入框按 Ctrl+V（Mac：Command+V）粘贴，自行发送；应用不会自动发送提示词。
- 收起面板不会销毁当前会话。登录由浏览器和豆包保存，应用不读取或存储账号密码。
- 如果面板空白或第三方 Cookie 限制登录，点击“独立窗口打开”，用同一浏览器的普通窗口登录。
- 登录过期、清除 Cookie 或使用隐私窗口时，可能需要重新登录。

版本更新
- 点击“前往 GitHub 查看版本”或“检查更新”。只有手动点击时才联网检查。
- 自动更新需要用 start-icon-tool.cmd 启动；发现新版后点击“更新到最新版本”。
- 新版来自 1644ye/pages 的正式 Release，校验后安装到 .updates，自动重启并恢复当前内容。
- 原版文件保留；新版启动失败时自动恢复旧版。以后继续使用启动脚本打开最新版本。
- 直接双击 HTML 仍打开原文件，可检查更新或手动下载，不会覆盖本地文件。

网站 Icon 提取
- 需要联网访问目标网站，不调用 AI，不使用第三方图标代理。
- 此扩展功能需要 Python 3.10 或更高版本。Windows 双击 start-icon-tool.cmd；
  Mac / Linux 在解压目录执行 python3 icon-server.py。
- 浏览器会自动打开本地工具，保持启动窗口开启。填写网址，点击提取，再预览并下载图标。
- 原有双击 HTML 生成功能仍无需安装环境。图标功能不支持需登录或阻止自动访问的网站。

内容与导出
- 共 8 个页面：About Us、Customer Service Policy、Privacy Policy、Refund Policy、
  Shipping Policy、Terms of Purchase、Terms of Use、Contact Us。
- Pages 表保持模板的 11 列；Menus 表保持样例的 18 列，包含 8 个页面目录项。
- About 菜单包含 Contact Us、About Us；Information 菜单包含其余六个政策页面。
- 菜单通过页面 handle 关联，不使用样例商店的 ID。默认页面可见并发布，可取消勾选改为草稿。
- 导入后请在主题的页脚或导航区域选择 About / Information 菜单。
- MERGE 按 handle 新建或更新页面；导入前请留意商店内已有的同名 handle。
- 首页公告栏、首页布局建议和 SEO 文案通过另一个按钮单独下载，不会自动写入主题。
- 如需继续编辑，请点击“保存生成结果 JSON”。下次通过“恢复已保存的 JSON”载入。
  关闭或刷新网页不会自动保留输入和结果。

Contact Us 使用提供的固定模板。表单点击 Send Message 只跳转首页，
不会发送邮件或保存留言。请核对模板里的客服时间及业务描述后使用。

导出文件通常保存在浏览器的“下载”文件夹。若浏览器拦截下载，请允许本次下载。
'''
readme_path = output / '使用说明.txt'
readme_path.write_text(instructions, encoding='utf-8-sig')
archive = root.parent / 'Shopify页面生成器_免安装离线版.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in [html_path, readme_path, root / 'icon-server.py', root / 'start-icon-tool.cmd', root / 'updater.py', root / 'version.json']:
        z.write(p, 'Shopify页面生成器/' + p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == 6
    assert z.read('Shopify页面生成器/双击打开.html').decode('utf-8') == page

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(); self.inside=False; self.scripts=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'script': self.inside=True; self.scripts.append('')
    def handle_endtag(self, tag):
        if tag == 'script': self.inside=False
    def handle_data(self, value):
        if self.inside: self.scripts[-1] += value
parser=Scripts(); parser.feed(page)
assert len(parser.scripts) == 8
(output / 'verify-bundle.js').write_text('\n'.join(parser.scripts), encoding='utf-8')
print(f'Created: {archive}\nZIP size: {archive.stat().st_size:,} bytes\nStandalone HTML: {len(page.encode("utf-8")):,} bytes\nVerified: 6 entries, ZIP integrity, embedded resources, 8 intact scripts')
