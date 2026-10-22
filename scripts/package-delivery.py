from pathlib import Path
import json,zipfile
root=Path(__file__).resolve().parents[1]
meta=json.loads((root/'dsh-plugin/package.json').read_text(encoding='utf8'))
version=meta['version'];asset=meta['name']+'-'+version+'.tgz'
expected=json.loads((root/'release/page-studio-update.json').read_text(encoding='utf8'))['sha256']
archive=root/'release'/f'PageStudio-DSH-{version}-Windows.zip'
installer=fr'''@echo off
chcp 65001 >nul
setlocal DisableDelayedExpansion
set "PAGE_STUDIO_ARCHIVE=%~dp0{asset}"
powershell.exe -NoProfile -NonInteractive -Command "try {{ if ((Get-FileHash -LiteralPath $env:PAGE_STUDIO_ARCHIVE -Algorithm SHA256).Hash -ne '{expected}') {{ exit 1 }} }} catch {{ exit 1 }}"
if errorlevel 1 (
  echo 安装包 SHA-256 校验失败，停止安装。请重新下载完整压缩包。
  pause
  exit /b 1
)
set "PAGE_STUDIO_CLI=%LOCALAPPDATA%\Programs\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd"
if not exist "%PAGE_STUDIO_CLI%" (
  echo 未找到标准安装目录中的 DSH CLI。请按安装说明使用实际 CLI 或插件管理器安装。
  pause
  exit /b 1
)
echo 将 Page Studio {version} 安装到 DSH desktop Profile。
echo 不会结束 DSH；成功后请先保存工作，再自行重启 DSH。
call "%PAGE_STUDIO_CLI%" plugin --profile desktop add "%PAGE_STUDIO_ARCHIVE%"
if errorlevel 1 (
  echo 安装失败。请保留上方错误信息，并检查 DSH 版本是否为 0.2.0-rc.2。
  pause
  exit /b 1
)
echo 安装完成。请保存工作后重启 DSH，寻找左下角 Page Studio 按钮。
pause
'''
guide=(root/'docs/DSH安装使用说明.md').read_text(encoding='utf8')
evidence=(root/'docs'/f'release-{version}.md').read_text(encoding='utf8')+'\n\n'+(root/'docs/dsh-migration.md').read_text(encoding='utf8')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(root/'release'/asset,asset)
    z.write(root/'release/SHA256SUMS','SHA256SUMS')
    z.write(root/'release/page-studio-update.json','page-studio-update.json')
    z.writestr('安装到DSH.cmd',installer.replace('\n','\r\n').encode('utf8'))
    z.writestr('安装使用说明.md',guide.encode('utf8'))
    z.writestr('验证记录.md',evidence.encode('utf8'))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==6
print(f'Created {archive.name}: {archive.stat().st_size} bytes; 6 verified entries')
