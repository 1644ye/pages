from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1];package=root/'dsh-plugin';web=package/'web';web.mkdir(exist_ok=True)
source=(root/'dist/app.js').read_text(encoding='utf8')
export_code=source[source.index('function escapeXml('):source.index('function rows(')]+source[source.index('function crc32('):source.index("$('export').onclick")]
(package/'shared/export-runtime.js').write_text(export_code,encoding='utf8')
for name in ['app.js','style.css','xlsx.js','contact.html','contact-template.js','prompt.js']:
 shutil.copy2(root/'dist'/name,web/name)
s=(web/'app.js').read_text(encoding='utf8');a=s.index("$('form').onsubmit");b=s.index("$('import').onclick",a);s=s[:a]+s[b:];(web/'app.js').write_text(s,encoding='utf8')
# Keep the editable prompt builder, not fixed body generation or silent local fallback.
s=(web/'prompt.js').read_text(encoding='utf8').replace("generateLocal(values).marketing.seo", "[{title:values.refTitle,description:values.refBody}]");(web/'prompt.js').write_text(s,encoding='utf8')
shutil.copy2(package/'bridge.js',web/'dsh.js')
s=(root/'dist/index.html').read_text(encoding='utf8').replace('<script src="generator.js?v=generic1"></script>','')
assert 'generator.js' not in s
s=s.replace('本地生成页面','DSH 对话生成页面').replace('在本机使用内置英文模板生成，无需 API Key。参考描述用于匹配商品类别和卖点关键词；生成后可编辑。邮箱留空使用 Contact Us 入口，日期留空使用通用公告。','复用 DSH 中配置的 DeepSeek，不复制密钥。生成内容经结构校验后才可导出；不会回退到本地正文模板。')
s=s.replace('</form>', '<button type="button" class="secondary" id="generateExport">生成并导出 XLSX</button></form>',1)
toolbar='''<section style="margin-bottom:24px"><p id="hostVersion"></p><label>模型<select id="dshModel"></select></label><label>在现有会话继续（选填；留空新建专用会话）<input id="sessionId" placeholder="输入明确选择的 DSH session id"></label><p id="contextInfo">默认只发送当前表单中明确选择的材料。</p><button id="previewSend" class="secondary">预览发送内容</button> <button id="cancelTask" class="secondary">停止生成</button><details><summary>实际发送内容与上下文</summary><textarea id="sendPreview" rows="8" readonly></textarea></details><p id="taskId"></p><pre id="streamText" style="white-space:pre-wrap;max-height:250px;overflow:auto"></pre><details><summary>思考内容（不导出）</summary><pre id="thinkingText" style="white-space:pre-wrap"></pre></details><a id="fileReady" hidden></a><button id="applyNewResult" hidden>应用已完成的新结果</button><label>结果版本<select id="historySelect"></select></label><label>继续修改要求<textarea id="changeRequest" rows="2"></textarea></label><button id="continueTask" class="secondary">在当前会话修改</button></section>'''
s=s.replace('<div class="workspace">',toolbar+'<div class="workspace">')
prompt='''<details open><summary>提示词工作台 · 编辑 / 变量 / 预览 / 直接运行</summary><label>已保存提示词<select id="savedPrompt"></select></label><label>标题<input id="promptTitle" placeholder="例如：首页营销文案"></label><label>分类标签（逗号分隔）<input id="promptTags"></label><label>变量默认值（JSON 对象）<textarea id="promptDefaults" rows="2">{}</textarea></label><label>本次变量值（JSON 对象，变量写法 {{变量名}}）<textarea id="promptVariables" rows="2">{}</textarea></label><div class="downloads"><button id="savePrompt" class="secondary">保存提示词</button><button id="deletePrompt" class="secondary">删除选中提示词</button><button id="previewPrompt" class="secondary">预览变量展开</button><button id="runPrompt" class="primary">直接运行 DeepSeek</button></div><label>提示词运行结果<textarea id="promptAnswer" rows="12"></textarea></label></details>'''
s=s.replace('<footer>PAGE STUDIO',prompt+'''<details><summary>更新设置</summary><label>固定发布仓库（owner/repo）<input id="releaseRepository" placeholder="尚未配置发布来源"></label><label><input type="checkbox" id="autoCheck" checked>自动检查（启动及运行时每6小时）</label><label><input type="checkbox" id="autoInstall" checked>自动安装兼容且已验证恢复的稳定版本</label><label>更新通道<select id="updateChannel"><option value="stable">稳定版</option><option value="test">测试版</option></select></label><button id="saveSettings">保存设置</button> <button id="checkUpdate">检查更新</button> <button id="installUpdate">安装已暂存更新</button><pre id="updateState"></pre></details><footer>PAGE STUDIO''')
s=s.replace('</body>', '<script src="dsh.js"></script></body>')
(web/'index.html').write_text(s,encoding='utf8')
print('Built native DSH plugin web resources; fixed prose generator excluded.')
