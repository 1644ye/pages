# Shopify Page Studio · DSH 插件与离线版

DSH 插件通过宿主的 DeepSeek 对话生成七个页面，并附加固定 Contact Us，导出包含八个页面及导航菜单的 Matrixify XLSX。支持流式结果、真实取消、同会话修改、提示词变量、结果编辑和版本历史。分类为工作流与自动化，不是 Shopify 主题或邮件服务。

## 下载、安装与启用

支持 **Windows / DeepSeek Harness 0.2.0-rc.2 / Node 24 运行时**。不声明兼容其他 DSH 版本。

- [正式 Release](https://github.com/1644ye/pages/releases/tag/dsh-v0.1.4)
- [Windows 安装 ZIP](https://github.com/1644ye/pages/releases/download/dsh-v0.1.4/PageStudio-DSH-0.1.4-Windows.zip)
- [原生插件 TGZ](https://github.com/1644ye/pages/releases/download/dsh-v0.1.4/dsh-shopify-page-studio-0.1.4.tgz)
- [SHA-256 校验文件](https://github.com/1644ye/pages/releases/download/dsh-v0.1.4/SHA256SUMS)

解压 ZIP，双击“安装到DSH.cmd”，安装到 desktop Profile。保存工作后完全退出并重新打开 DSH，点击左下角 **Page Studio · 页面生成**。插件默认启用；若曾关闭，请在 DSH 插件管理器启用 `dsh-shopify-page-studio`。

已用本机真实 CLI 验证以下安装形式；将路径换为你下载文件的绝对路径：

```powershell
& "$env:LOCALAPPDATA\Programs\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd" --version
& "$env:LOCALAPPDATA\Programs\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd" plugin --profile desktop add "C:\Downloads\dsh-shopify-page-studio-0.1.4.tgz"
```

配置好 DSH 的 DeepSeek 模型后填写参考标题、内容和折扣，点击“生成并导出”。模型使用宿主账号和用量，导出本身在本地完成。保存编辑后再次导出会使用对应的已保存版本。浏览器阻止自动下载时使用结果中的下载链接。Contact Us 表单仅跳转首页，不发送邮件。

## 更新、数据和卸载

默认固定更新仓库为 `1644ye/pages`，启动后及每六小时检查 Release，下载后检查版本、兼容性、包身份、长度和 SHA-256。只有发布元数据声明已验证恢复、没有新权限及不可逆迁移的版本才自动安装；生成、导出或未保存编辑会推迟安装。界面明确提示需要重启，不会强制结束 DSH。网络失败会显示错误。

用户数据在 `%USERPROFILE%\.dsh\page-studio\<Profile>\`，更新/卸载不会删除；失败更新会恢复已备份的旧插件，保留兼容的最新数据并阻止失败版本。SHA-256 用于检测下载损坏，不能防止发布账号被攻破。需要回退时可重新安装此目录 `updates\rollback-<版本>.tgz`，保存工作后重启。

```powershell
& "$env:LOCALAPPDATA\Programs\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd" plugin --profile desktop remove dsh-shopify-page-studio
```

卸载后保存工作并重启 DSH，使当前进程卸载插件。

## 插件市场与验证

仓库已使用 `dsh-plugin` topic，投稿分类为 `workflow`。官方提供第三方市场索引协议，不存在统一官方收录状态。Awesome DSH Plugin 要求仓库创建满一天；本仓库创建于 2026-10-22 02:51:24 UTC，2026-10-23 10:51:24（北京时间）后才满足年龄门槛。投稿文件是 `market/submission.yml`，目前为**待提交，未收录**。

另提供[自有 format-1 索引](https://raw.githubusercontent.com/1644ye/pages/main/market/index.json)，安装源固定到不可变 Git commit。当前本机 0.2.0-rc.2 未包含官方 Custom plugin markets，不能宣称在该版本中已验证 Discover；本机请使用 Release 安装包。较新宿主即使支持索引，也需先满足插件的精确兼容声明。

真实宿主验证与未验证范围记录在 [发布验收记录](docs/release-0.1.4.md)。完整中文步骤见 [安装使用说明](docs/DSH安装使用说明.md)。

## 开发与打包

```powershell
npm ci --prefix dsh-plugin --ignore-scripts --omit=peer
python scripts/build-dsh.py
node --test dsh-plugin/test/*.test.mjs
node scripts/package-dsh.mjs
python scripts/package-delivery.py
```

使用 Node 24。源码、依赖清单、锁文件及预构建入口均已提供；`dist/` 是离线版维护源和插件构建输入，保留在 Git 中；`release/`、`portable/` 和运行数据不提交。

## 原离线版说明

# Shopify 页面生成器

项目同时提供离线版和 DSH 原生插件。DSH 插件使用宿主模型生成页面，与下方纯本地模板模式不同；安装和用法见 [DSH 安装使用说明](docs/DSH安装使用说明.md)，实际验证范围见 [验证记录](docs/dsh-migration.md)。插件源码位于 `dsh-plugin/`，依赖清单和锁文件一并保留；`scripts/build-dsh.py` 构建插件界面，`scripts/package-dsh.mjs` 生成安装归档。发布安装包不提交到 Git 历史，由发布流程构建。

`dist/` 是离线版的直接维护源文件，也是插件界面构建的必要输入，因此保留；生成的 `portable/`、`release/`、宿主审计和测试数据均忽略。

双击 start.cmd，或直接打开 dist/index.html。也可以运行本地静态服务器并访问 http://127.0.0.1:8765/。

填写参考网站描述的标题和内容、最高折扣（品牌名称选填，仅用于 SEO 和提示词），点击“本地生成页面”。联系邮箱、文案日期默认空白且为选填。日期为空时使用通用公告文案；邮箱为空时使用 Contact Us 页面作为帮助入口。

生成过程完全在浏览器本地执行，不调用 AI，不需要 API Key，也不请求外部字体或资源。内置英文模板根据参考描述中的商品类别和卖点关键词进行组合，不提供自由语义改写或翻译；结果可预览并编辑。

生成七个英文页面并附加固定 Contact Us，共八个页面。About Us 至少 3,000 英文单词。导出的 Pages-and-Menus.xlsx 包含 Pages 和 Menus 两张表，分别匹配样例的 11 列和 18 列字段，使用 Matrixify 导入整个文件。About 菜单包含 Contact Us、About Us；Information 菜单包含其余六个政策页面。菜单通过页面 handle 关联，导入后在主题导航或页脚选择对应菜单。默认发布可见（Published 为 TRUE），取消勾选可改为草稿。MERGE 按 handle 新建或更新页面，不复用参考商店 ID 和日期。

首页公告栏、位置建议和 SEO 文案单独下载。Pages 导入不会自动配置主题公告栏或页面 SEO。需要留存时下载 JSON，可在下次打开时恢复。

Contact Us 保留用户提供的双栏布局、客服时间和跳转首页逻辑。该表单不发送邮件或保存留言。页面中展示的商品特征和隐私说明应与实际经营情况核对。

首页与 SEO 提示词：支持下拉多选、全选、尺码表、可选源网址和 SEO 信息，以及折扣/免运费/产品特色等重点。点击生成自动拼接当前品牌、描述和折扣，并复制到剪贴板。浏览器拒绝复制时显示可手动复制的完整文本。
