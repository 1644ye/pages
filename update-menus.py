from pathlib import Path
root=Path(__file__).parent
p=root/'dist/app.js'
s=p.read_text(encoding='utf8')
a=s.index('function workbook(');b=s.index('function crc32(',a)
s=s[:a]+s[b:]
s=s.replace("!/^(https?:|mailto:|#)/i.test(a.value)","!/^(https?:|mailto:|#|\\/(?!\\/))/i.test(a.value)")
s=s.replace("download('Pages.xlsx'", "download('Pages-and-Menus.xlsx'")
s=s.replace('已导出 Pages.xlsx。使用 Matrixify 导入；首页公告栏与 SEO 文案请另行下载并填写到主题或页面 SEO 设置。','已导出 Pages-and-Menus.xlsx，内含 Pages 和 Menus 两张表。目录按 About / Information 分组；导入后可在主题中选择这两个菜单。')
p.write_text(s,encoding='utf8')
p=root/'dist/index.html'
s=p.read_text(encoding='utf8').replace('下载 Pages.xlsx ↓','下载页面与目录 XLSX ↓')
s=s.replace('Excel 用于 Matrixify → Import → Pages。默认导入为草稿；MERGE 按 handle 新建或更新页面。','同一个 XLSX 包含 Pages（8 个页面）和 Menus（8 个目录项）。About：Contact Us、About Us；Information：其余六个政策页面。默认页面为草稿，需上线可勾选发布。导入后在主题页脚选择 About / Information 菜单。')
s=s.replace('<script src="app.js?v=local1"></script>','<script src="xlsx.js?v=menus1"></script><script src="app.js?v=menus1"></script>')
p.write_text(s,encoding='utf8')
p=root/'package-portable.py'
s=p.read_text(encoding='utf8').replace("['contact-template.js', 'generator.js', 'app.js']","['contact-template.js', 'generator.js', 'xlsx.js', 'app.js']")
s=s.replace('len(parser.scripts) == 3','len(parser.scripts) == 4').replace('3 intact scripts','4 intact scripts')
s=s.replace('下载 Pages.xlsx','下载 Pages-and-Menus.xlsx').replace('使用 Matrixify 的 Pages 导入功能导入 Excel。','使用 Matrixify 导入整个 Excel，其中包含 Pages 和 Menus 两张表。')
s=s.replace('- Excel 与提供的模板保持相同的 11 列字段。默认导入草稿，可勾选“导入时发布页面”。','- Pages 表保持模板的 11 列；Menus 表保持样例的 18 列，包含 8 个页面目录项。\n- About 菜单包含 Contact Us、About Us；Information 菜单包含其余六个政策页面。\n- 菜单通过页面 handle 关联，不使用样例商店的 ID。默认页面为草稿，可勾选发布。\n- 导入后请在主题的页脚或导航区域选择 About / Information 菜单。')
p.write_text(s,encoding='utf8')
p=root/'README.md'
s=p.read_text(encoding='utf8').replace('导出的 Pages.xlsx 与原模板的 11 列字段一致，使用 Matrixify 的 Pages 导入。','导出的 Pages-and-Menus.xlsx 包含 Pages 和 Menus 两张表，分别匹配样例的 11 列和 18 列字段，使用 Matrixify 导入整个文件。About 菜单包含 Contact Us、About Us；Information 菜单包含其余六个政策页面。菜单通过页面 handle 关联，导入后在主题导航或页脚选择对应菜单。')
p.write_text(s,encoding='utf8')
