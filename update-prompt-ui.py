from pathlib import Path
root=Path(__file__).parent
p=root/'dist/index.html';s=p.read_text(encoding='utf8')
s=s.replace('id="published">','id="published" checked>')
s=s.replace('默认页面为草稿，需上线可勾选发布。','默认页面可见并发布，可取消勾选改为草稿。')
panel='''<section class="prompt-builder"><div class="section-title"><span class="step">03</span><h2>首页与 SEO 提示词</h2><span class="pill">本地拼接 · 一键复制</span></div>
<p class="hint">自动带入左侧当前填写的品牌、参考描述及折扣，无需先生成页面。SEO 留空时使用本地生成的 SEO 信息。</p>
<div class="two"><label>SEO 信息 <small>选填</small><textarea id="promptSeoInfo" rows="3" placeholder="可粘贴已有的 SEO 标题、描述或关键词；留空自动带入本地 SEO"></textarea></label><label>源网址 <small>选填</small><input id="promptSourceUrl" type="url" placeholder="https://example.com/products/example"><span class="hint">仅加入提示词，不会在本地访问或抓取网页。</span></label></div>
<details class="prompt-dropdown"><summary>选择需要生成的内容 <span id="promptSelectionCount"></span></summary><label class="check-row select-all"><input type="checkbox" id="promptAll" checked>全选</label><div id="promptOptions" class="prompt-checks"></div></details>
<fieldset class="focus-field"><legend>着重体现 <small>选填，可多选</small></legend><div id="promptFocus" class="prompt-checks focus-checks"></div></fieldset>
<div class="downloads"><button type="button" class="primary" id="generatePrompt">生成提示词并复制</button><button type="button" class="secondary" id="copyPromptAgain">再次复制</button></div>
<p id="promptStatus" class="hint" role="status" aria-live="polite">选择单个或多个项目后，点击生成即可自动复制。</p><label>生成的提示词<textarea id="promptOutput" rows="12" placeholder="生成的完整提示词将显示在这里，也可以手动修改后再次复制。"></textarea></label></section>
'''
s=s.replace('<footer>PAGE STUDIO',panel+'<footer>PAGE STUDIO')
s=s.replace('<script src="app.js?v=menus1"></script>','<script src="app.js?v=prompt1"></script><script src="prompt.js?v=prompt1"></script>')
s=s.replace('style.css?v=local1','style.css?v=prompt1')
p.write_text(s,encoding='utf8')
p=root/'dist/style.css';s=p.read_text(encoding='utf8');s+='''
.prompt-builder{margin-top:24px}.prompt-dropdown{border:1px solid #dfe4da;border-radius:8px;padding:14px}.prompt-dropdown summary{font-size:14px}.prompt-checks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}.prompt-checks label,.check-row{display:flex;align-items:center;gap:9px;margin:0;font-weight:400;line-height:1.6}.prompt-checks input,.check-row input{width:auto;margin:0;flex-shrink:0;accent-color:#314d37}.select-all{padding:12px 0;border-bottom:1px solid #e6eadf;font-weight:600}.focus-field{border:1px solid #dfe4da;border-radius:8px;margin:20px 0;padding:14px}.focus-field legend{font-size:12px}.focus-field small{color:#929a90}.focus-checks{grid-template-columns:repeat(3,minmax(0,1fr));margin:0}#promptOutput{font-weight:400}#promptStatus{color:#496044}@media(max-width:600px){.prompt-checks{grid-template-columns:1fr}.focus-checks{grid-template-columns:repeat(2,minmax(0,1fr))}.prompt-builder .two{grid-template-columns:1fr}.prompt-builder .section-title{flex-wrap:wrap}}
''';p.write_text(s,encoding='utf8')
p=root/'package-portable.py';s=p.read_text(encoding='utf8').replace("'xlsx.js', 'app.js']","'xlsx.js', 'app.js', 'prompt.js']").replace('len(parser.scripts) == 4','len(parser.scripts) == 5').replace('4 intact scripts','5 intact scripts').replace('默认页面为草稿，可勾选发布。','默认页面可见并发布，可取消勾选改为草稿。');s=s.replace('内容与导出\n','首页与 SEO 提示词\n- 页面下方可多选 12 个内容项目（包含尺码表），展开下拉框后顶部可全选或取消全选。\n- 可选填写 SEO 信息和源网址，可勾选折扣、免运费、产品特色等重点。\n- 点击“生成提示词并复制”，自动带入当前品牌、描述和折扣并复制到剪贴板。\n- 全程本地拼接，不调用 AI，不抓取网址。如浏览器拒绝复制，可手动复制显示的文本。\n\n内容与导出\n');p.write_text(s,encoding='utf8')
p=root/'README.md';s=p.read_text(encoding='utf8').replace('默认草稿，勾选发布则 Published 为 TRUE。','默认发布可见（Published 为 TRUE），取消勾选可改为草稿。');s+='\n首页与 SEO 提示词：支持下拉多选、全选、尺码表、可选源网址和 SEO 信息，以及折扣/免运费/产品特色等重点。点击生成自动拼接当前品牌、描述和折扣，并复制到剪贴板。浏览器拒绝复制时显示可手动复制的完整文本。\n';p.write_text(s,encoding='utf8')
