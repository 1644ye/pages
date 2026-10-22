$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$installRoot=Join-Path $env:LOCALAPPDATA 'Programs/DeepSeek Harness'
$exe=Join-Path $installRoot 'DeepSeek Harness.exe'
$cli=Join-Path $installRoot 'resources/app.asar/dsh/node_modules/@deepseek-ai/dsh-desktop-host/lib/cli.js'
$patch=Join-Path $projectRoot '.dsh-test/test-profile.patch.yml'
$env:ELECTRON_RUN_AS_NODE='1'
$env:PAGE_STUDIO_FIXTURES=Join-Path $projectRoot '.dsh-test/fixtures'
$arguments=@('--expose-internals',('"'+$cli+'"'),'--profile','page-studio-test','--patch',('"'+$patch+'"'),'--port','9186','--no-open')
$process=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot '.dsh-test/host.log') -RedirectStandardError (Join-Path $projectRoot '.dsh-test/host-error.log') -PassThru
@{pid=$process.Id;exe=$exe} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $projectRoot '.dsh-test/host-process.json') -Encoding utf8
Write-Output ('Started isolated test host PID '+$process.Id)
