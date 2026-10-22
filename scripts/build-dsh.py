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
toolbar='''<section class="dsh-controls"><p id="hostVersion"></p><div class="control-grid"><label>生成模型<select id="dshModel"></select></label><label>继续现有会话 <small>选填</small><input id="sessionId" placeholder="留空新建专用会话；或填入已有会话 ID"></label></div><p id="contextInfo">默认只发送当前表单中明确选择的材料。</p><div class="downloads"><button id="previewSend" class="secondary">预览发送内容</button><button id="cancelTask" class="secondary">停止生成</button><a id="fileReady" hidden></a><button id="applyNewResult" hidden>应用已完成的新结果</button></div><p id="taskId"></p><pre id="streamText"></pre><div class="advanced-grid"><details><summary>运行记录与发送预览</summary><label>实际发送内容<textarea id="sendPreview" rows="6" readonly></textarea></label><details><summary>思考内容（不导出）</summary><pre id="thinkingText"></pre></details></details><details><summary>历史结果与继续修改</summary><label>结果版本<select id="historySelect"></select></label><label>继续修改要求<textarea id="changeRequest" rows="2"></textarea></label><button id="continueTask" class="secondary">在当前会话修改</button></details></div></section>'''
s=s.replace('<div class="workspace">',toolbar+'<p id="updateNotice" role="status" hidden></p><div class="workspace">')
prompt='''<details class="prompt-library"><summary>保存与管理提示词 <span>可选</span></summary><label>已保存提示词<select id="savedPrompt"></select></label><div class="two"><label>名称<input id="promptTitle" placeholder="例如：首页营销文案"></label><label>标签<input id="promptTags" placeholder="用逗号分隔"></label></div><details><summary>变量设置 <span>仅自定义模板需要</span></summary><div class="two"><label>变量默认值（JSON）<textarea id="promptDefaults" rows="3">{}</textarea></label><label>本次变量值（JSON）<textarea id="promptVariables" rows="3">{}</textarea></label></div><p class="hint">提示词中使用 {{变量名}}；复制和 DeepSeek 生成都会应用同一组变量。</p></details><div class="downloads"><button id="savePrompt" class="secondary">保存当前提示词</button><button id="deletePrompt">删除选中模板</button></div></details>'''
s=s.replace('<footer>PAGE STUDIO','''<details><summary>更新设置</summary><label>固定发布仓库（owner/repo）<input id="releaseRepository" placeholder="尚未配置发布来源"></label><label><input type="checkbox" id="autoCheck" checked>自动检查（启动及运行时每6小时）</label><label><input type="checkbox" id="autoInstall" checked>自动安装兼容且已验证恢复的稳定版本</label><label>更新通道<select id="updateChannel"><option value="stable">稳定版</option><option value="test">测试版</option></select></label><button id="saveSettings">保存设置</button> <button id="checkUpdate">检查更新</button> <button id="installUpdate">安装已暂存更新</button><pre id="updateState"></pre></details><footer>PAGE STUDIO''')
s=s.replace('<span class="pill">本地拼接 · 一键复制</span>','<span class="pill">复制 / DeepSeek 生成</span>')
s=s.replace('自动带入左侧当前填写的品牌、参考描述及折扣，无需先生成页面。SEO 留空时使用本地生成的 SEO 信息。','选择内容和重点后，可直接复制提示词，或交给 DeepSeek 生成。两种方式共用下方提示词，无需先生成页面。')
s=s.replace('<div class="downloads"><button type="button" class="primary" id="generatePrompt">生成提示词并复制</button><button type="button" class="secondary" id="copyPromptAgain">再次复制</button></div>','<div class="downloads prompt-actions"><button type="button" class="secondary" id="generatePrompt">复制提示词</button><button type="button" class="primary" id="runPrompt">DeepSeek 生成</button></div>')
s=s.replace('选择单个或多个项目后，点击生成即可自动复制。','两种操作会自动拼接最新资料；也可先展开预览，手动编辑提示词。')
s=s.replace('<label>生成的提示词<textarea id="promptOutput" rows="12" placeholder="生成的完整提示词将显示在这里，也可以手动修改后再次复制。"></textarea></label></section>','<details class="prompt-preview"><summary>提示词预览与编辑</summary><label>当前提示词<textarea id="promptOutput" rows="8" placeholder="点击复制或 DeepSeek 生成时自动拼接，也可以在这里输入或修改提示词。"></textarea></label></details>'+prompt+'<div id="promptResult" class="prompt-result" hidden><div class="section-title"><h3>DeepSeek 生成结果</h3><button id="cancelPrompt" type="button">停止生成</button><button id="copyPromptResult" type="button" class="secondary">复制结果</button></div><textarea id="promptAnswer" rows="12" readonly aria-label="DeepSeek 生成结果" placeholder="生成的内容会显示在这里"></textarea></div></section>')
s=s.replace('</body>', '<script src="dsh.js"></script></body>')
s=s.replace('<section style="margin-bottom:24px">','<section class="dsh-controls">').replace('<label>模型<select','<div class="control-grid"><label>生成模型<select').replace('</label><p id="contextInfo">','</label></div><p id="contextInfo">')
s=s.replace('好文案，让品牌更完整','Shopify 页面工作台').replace('YOUR BRAND, BEAUTIFULLY WRITTEN','PAGE STUDIO / DEEPSEEK HARNESS').replace('告诉我们你的品牌','页面资料').replace('<details open><summary>提示词工作台','<details><summary>提示词工作台')
(web/'index.html').write_text(s,encoding='utf8')
with (web/'style.css').open('a',encoding='utf8') as css:css.write('\n'+(package/'theme.css').read_text(encoding='utf8'))
print('Built native DSH plugin web resources; fixed prose generator excluded.')
