$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$record=Get-Content -Raw -LiteralPath (Join-Path $projectRoot '.dsh-test/host-process.json') | ConvertFrom-Json
$process=Get-Process -Id $record.pid -ErrorAction SilentlyContinue
if($process){
  if($process.Path -ne $record.exe){throw 'PID identity changed; refusing to stop it'}
  Stop-Process -Id $process.Id
  Write-Output ('Stopped only isolated test host PID '+$process.Id)
}
