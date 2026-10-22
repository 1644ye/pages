> 2026-10-22 更正：后续 UI 验收发现 0.1.4 的健康标记写在用户目录，而恢复助手读取 updates/health.json。此前正向升级只观察了短时激活，未确认助手退出；因此不能将下面历史记录当作完整正向升级通过。0.1.7 修正该问题并重新验证。负向故障恢复与模型/导出记录不受此更正影响。

# 0.1.4 发布验收记录

环境：Windows；已安装 DeepSeek Harness CLI 与桌面运行时均为 0.2.0-rc.2。仅声明该精确宿主版本兼容。测试使用独立 Profile，不修改或重启日常 desktop。

## 已实际验证

- 真实 CLI 安装 0.1.4 并加载，宿主认证后的插件接口返回 0.1.4；入口、静态工作区及导出健康检查成功。
- 使用宿主 `deepseek-official / deepseek-flash / low` 完整生成七个页面，成功结束同一次请求与 turn；无模拟结果或模板兜底。
- 真实任务 `6d7c540f-d6ed-47d9-b3c3-e95cb9454d61` 完成并自动导出。下载 XLSX 64,476 bytes，经 openpyxl 重新打开，Pages/Menus 均为表头加八条记录，页面全部 Published TRUE。
- 全新 `page-studio-install-check` Profile 中安装、`--dump-config` 检查 bundle 层和 CLI 卸载均成功；卸载后 Profile 不再声明该 bundle。
- 十项单元测试及前端 JS 语法检查通过。与真实宿主测试分别记录，不将其作为模型或升级成功证据。
- GitHub 仓库描述、topic 已更新，含 `dsh-plugin`。生产更新器实际访问固定仓库 GitHub API 成功。

已确认同名本地候选归档可能被包管理器缓存复用。最终归档改用唯一文件名重装，并将实际安装目录重新打包与发布 TGZ 比较 SHA-256；一致值为 `9c03ca54190470f18ce29101b692e878f562f9c9aace1b8d03557215185bee48`。宿主真实 bundle 元数据显示中英文名称正确；认证后的编辑器资源和重启提示 HTML 均返回成功。

高推理档精确候选测试持续思考后已真实取消，未产生导出；最终成功生成使用低推理档，不改变日常宿主默认设置。

## 最终归档恢复通过

通过真实更新器安装仅本地的损坏 0.1.6，重启独立宿主后无法加载。独立助手等待健康超时，使用原生 CLI 恢复精确 0.1.4（exitCode 0）。重启后版本正确，保存的提示词和本次结果 revision 均保留，0.1.6 被阻止再安装，pending 清除。损坏夹具没有发布。

## 发布后验证

正式 Release `dsh-v0.1.4` 已公开。匿名下载 TGZ、更新元数据、SHA256SUMS 与 Windows ZIP 成功；TGZ 36,947 bytes，SHA-256 为 `9c03ca54190470f18ce29101b692e878f562f9c9aace1b8d03557215185bee48`，ZIP 内归档一致且完整性校验通过。

将专用测试宿主安装为旧 0.1.2 后，启动检查直接从正式公开 GitHub Release 发现、下载、校验并在空闲时自动安装 0.1.4，返回 pending-restart。仅重启该测试宿主后实际运行 0.1.4，activated 健康确认成功，pending 清除，提示词和本次生成 revision 均保留。安装目录重打包哈希再次与公开 TGZ 一致。该升级没有使用测试 staging 接口或模拟 Release。

正式匿名下载包已通过原生 CLI 安装到日常 desktop Profile，bundle 已启用，安装哈希一致；没有结束日常 DSH，需用户保存工作并手动重启以加载。

远程干净环境 CI 已通过：https://github.com/1644ye/pages/actions/runs/39717314021 。包括 Node 24 构建、十项测试、打包、实际 npm DSH 0.2.0-rc.2 干净 Profile 安装和认证接口健康检查、交付 ZIP 生成及上传构建附件。CI 不调用付费模型，真实模型生成由上述本机独立宿主验证。

早期 CI 因缺少 pnpm 失败，补齐 pnpm 11.7.0 后重新运行成功；未把失败或取消的运行报告为成功。最初同名本地归档缓存导致 locale 未进入安装目录，已通过唯一文件名重装及安装目录哈希比较排除，最终验收对应精确归档。

安装 ZIP 内附验证记录是首次发布前的快照；这里及 Release 独立附加的最终验证记录包含发布后的真实升级结果，安装归档未被替换。

## 边界与市场

GUI 视觉验收仍需要用户安装后确认左下角入口；此前电脑操作工具因不能可靠识别浏览器 URL 停止，未绕过该限制。后端安装/真实模型/实际文件验证不等于点击 UI 的端到端验证。

官方市场协议是第三方 format-1 JSON 索引，本机 0.2.0-rc.2 不包含官方 Custom plugin markets，所以不能声称在本机通过 Discover 安装。提供自有静态索引及不可变 Git 源作为接入材料。

选定社区目录 Awesome DSH Plugin 的投稿要求：一份独立 YAML、真实 `dsh.bundle`、真实功能描述、`dsh-plugin` topic，仓库满一天。投稿文件按 monorepo 子包规则准备，分类 workflow。仓库创建时间为 2026-10-22 02:51:24 UTC；最早满足年龄门槛时间是北京时间 2026-10-23 10:51:24。当前待提交，未收录；不会绕过门槛提交或声称已获维护者审核。

规则来源：

- https://deepseek-harness.github.io/deepseek-harness/en/guide/plugin-market
- https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/blob/main/contributing.md

独立 npm clean-CI 运行时下载曾在本机无输出等待，已停止；不把它写成通过。真实安装使用本机已安装且版本确认的官方桌面 CLI。
