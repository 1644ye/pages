# Shopify 页面生成器

打开部署地址，或运行 `python -m http.server 8765 --directory dist` 后访问 http://localhost:8765。

填写品牌名、联系邮箱、参考网站标题、参考内容和最高折扣。连接支持 Chat Completions 和浏览器 CORS 的 AI 服务，填写密钥、模型和接口地址，再生成。密钥仅留在当前页面内存，不写入存储。也可以复制完整提示词到自己的 AI 工具，粘贴或上传返回的 JSON。

生成七个英文页面并附加固定的 Contact Us，共八个页面，About Us 至少 3,000 英文单词。可预览、编辑 HTML，下载与原 pages.xlsx 字段一致的 Pages.xlsx。使用 Matrixify 的 Pages 导入，默认草稿；勾选发布则 Published 为 TRUE。MERGE 按 handle 创建或更新；不复用参考商店的 ID、日期及 Contact、Your Privacy Choices 页面。

首页公告栏、位置建议、SEO 和需要确认的事实另行下载。Matrixify Pages 不自动配置主题公告栏或页面 SEO。Privacy Policy 按提供的规则生成，使用者应核对实际数据处理实践。

API 服务按其收费方式计费。应用不内置密钥或免费 AI 额度，不保存输入或生成历史；需要留存时下载 JSON。Excel 单元格限制为 32,767 字符，过长 HTML 会阻止导出。

Contact Us 保留用户提供的双栏布局、客服时间和跳转首页逻辑，固定模板不经 AI 改写。它不会发送邮件或保存留言。
