# Shopify Page Studio 0.1.4

面向 Windows / DeepSeek Harness 0.2.0-rc.2 的原生插件。tag：`dsh-v0.1.4`。

- 通过宿主 DeepSeek 对话生成并编辑七个页面，附加固定 Contact Us；一键导出包含八个页面和导航菜单的 Matrixify XLSX。
- 支持流式结果、真实取消、同会话修改、已保存结果版本和提示词变量工作台。
- 默认更新源接通 `1644ye/pages`，启动及每六小时检查兼容 Release，校验后在空闲且无未保存编辑时安装。
- 使用真实宿主支持的中英文 locale 展示名称，补齐源码位置、关键词及精确兼容声明。
- 显示待重启、恢复、网络失败和需人工检查的更新状态。更新保留用户数据，启动失败恢复旧版并阻止失败版本。

安装：解压 Windows ZIP，双击“安装到DSH.cmd”，保存工作后退出并重开 DSH，点击左下角 Page Studio。也可用 `dsh plugin --profile desktop add <下载的tgz绝对路径>`。仅在 CLI 已加入 PATH 时使用 `dsh` 简写。

模型调用使用 DSH 中配置的 DeepSeek 账号和用量；导出在本地完成。Contact Us 表单只跳转首页，不发送邮件。卸载保留 `%USERPROFILE%\.dsh\page-studio\<Profile>\` 数据。

GUI 视觉验收仍需用户确认；本机版本没有官方 Custom plugin markets。社区目录投稿受仓库满一天门槛限制，当前未提交、未收录。完整实际验证结果见仓库 `docs/release-0.1.4.md`。
