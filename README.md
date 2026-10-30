# Shopify Page Studio · 免安装离线版

在浏览器本地生成 Shopify 页面、导航菜单和营销提示词，不调用 AI，不需要账号或 API Key。

## 下载与使用

从 [最新 Release](https://github.com/1644ye/pages/releases/latest) 下载离线 ZIP，解压后双击 **双击打开.html**。全部资源内嵌，断网也可以生成和导出。也可以下载仓库后双击 `start.cmd`，或直接用现代桌面浏览器打开 `dist/index.html`，无需安装开发环境。

填写参考描述的标题、内容及最高折扣，点击“本地生成页面”。品牌名称选填，仅用于独立的 SEO 文案和提示词；八个页面正文不依赖品牌名。邮箱与日期默认留空、选填。

## 页面与目录

导出的 `Pages-and-Menus.xlsx` 同时包含：

- `Pages`：About Us、Customer Service Policy、Privacy Policy、Refund Policy、Shipping Policy、Terms of Purchase、Terms of Use，以及固定 Contact Us。
- `Menus`：About（Contact Us、About Us）和 Information（其余六个政策页面），通过页面 handle 对应。

使用 Matrixify 导入整个文件，再在主题导航或页脚选择对应菜单。页面默认发布可见，可取消勾选改为草稿。`MERGE` 按 handle 新建或更新同名页面与菜单项。

支持 HTML 预览和编辑、JSON 保存及恢复。生成内容采用内置英文模板和关键词匹配，不提供自由语义改写或翻译。About Us 至少 3,000 个英文单词；页面 HTML 超过 Excel 单元格限制时会阻止导出。

业务规则：USD，1–3 天发货、预计 6–12 天送达、60 天退货、5–10 天退款、全球免运费并承担相关关税。Shipping Policy 按要求不写免费运输。请核对生成内容是否符合实际经营情况。

Contact Us 保留提供的固定内容与表单，提交仅跳转首页，不发送邮件或保存留言。

## 本地提示词

支持 12 个内容项目的单选、多选、全选，包括首页 Banner、公告栏、品牌理念、产品卖点、情绪文案、首页/单品 SEO 和尺码表。可补充 SEO 信息、源网址，以及折扣、免运费、产品特色等重点。点击生成即拼接并复制到剪贴板；浏览器不允许复制时可手动复制显示的文本。

尺码表提示词要求输出可直接粘贴的纯 HTML，不含 JS、CSS、style 属性或 Markdown 代码围栏。源网址只作为提示词资料，不会自动访问或抓取。

## 开发与验证

### 豆包对话面板

提示词区域保留“生成提示词并复制”，旁边的“打开豆包对话”展开豆包官网 iframe，默认收起，不会提前联网加载。生成后自行粘贴、发送。收起不销毁 iframe，不读取账号密码或聊天内容。浏览器限制第三方 Cookie 或官网拒绝嵌入时，使用“独立窗口打开”；同一普通浏览器配置的登录状态由豆包及浏览器保存，不能保证登录永久有效。

### 检查与安装更新

页面底部提供 GitHub 正式发布链接、“检查更新”和“更新到最新版本”。不会后台自动检查或安装。自动安装需要通过 `start-icon-tool.cmd`（Python 3.10+）启动，直接双击 HTML 时可检查或手动下载。

更新来自本仓库最新正式 `offline-v` Release 的`Shopify-Page-Studio-offline.zip`，验证 GitHub 提供的 SHA-256、包大小、文件列表和内部版本后安装到 `.updates`。保留原文件和上一版本，启动失败自动回退。通过启动脚本继续打开已安装的新版。更新时暂存表单及已生成页面，刷新后恢复；请勿在更新期间继续编辑。

发布新版时同步修改 `version.json` 与 `dist/update.js` 中的版本，打包并上传到对应的 `offline-v年.月.日.序号` 正式 Release；只推送 main 不触发客户端更新。

### 网站 Icon 提取

安装 Python 3.10 或更高版本后，Windows 双击 `start-icon-tool.cmd`，Mac / Linux 运行 `python3 icon-server.py`。浏览器自动打开本地应用，保持服务窗口开启。在“网站 Icon 提取”中填写网址，提取后预览并下载原始图标。压缩包中也包含服务和启动脚本。

此功能联网访问目标网站，不调用 AI，不使用第三方图标代理，不发送浏览器登录信息。支持 favicon、Apple Touch Icon、mask-icon，按网页声明解析相对地址；未声明图标时提供标为“未验证”的 `/favicon.ico` 候选。支持 PNG、ICO、JPG、GIF、WebP、SVG，单个响应上限 5 MB。需登录或限制自动访问的网站可能无法提取。不执行网站脚本，因此动态注入的图标可能无法识别。

原有页面生成、提示词与 Excel 导出仍可断网双击 HTML 使用，无需 Python。

维护源在 `dist/`。测试使用 Node.js 24，打包使用 Python 3.12，均只使用标准库，无需安装依赖：

```sh
node check-export.cjs
node check-doubao.cjs
python check-icons.py
python check-updates.py
python package-portable.py
node check-export.cjs portable/verify-bundle.js
```

打包输出 `portable/双击打开.html`、说明文件，以及仓库上级目录中的 `Shopify页面生成器_免安装离线版.zip`。构建结果不提交到 Git，正式包通过 GitHub Release 分发。CI 会验证源码与打包后的脚本。

仓库只维护此离线版；旧插件和实验版不再包含在 main 中，历史仍可通过 Git 提交查看。
