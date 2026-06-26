$ErrorActionPreference = 'Stop'

$Repo = 'salarzudfekr/reality-sni-smart-scanner'
$Branch = 'main'
$InstallDir = if ($env:INSTALL_DIR) { $env:INSTALL_DIR } else { Join-Path $HOME 'reality-sni-smart-scanner' }
$RawBase = "https://raw.githubusercontent.com/$Repo/$Branch"

Write-Host 'Installing Reality SNI Smart Scanner...'
Write-Host "Install dir: $InstallDir"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

$Files = @('reality_sni_smart.py', 'README.md', 'CHANGELOG.md', 'LICENSE', 'VERSION')
foreach ($File in $Files) {
    Invoke-WebRequest -Uri "$RawBase/$File" -OutFile (Join-Path $InstallDir $File) -UseBasicParsing
}

$CmdPath = Join-Path $InstallDir 'reality-sni-smart.cmd'
$PyPath = Join-Path $InstallDir 'reality_sni_smart.py'
Set-Content -Path $CmdPath -Encoding ASCII -Value "@echo off`r`npython `"$PyPath`" %*`r`n"

python -m py_compile $PyPath

Write-Host ''
Write-Host 'Installed successfully.'
Write-Host 'Run:'
Write-Host "  python `"$PyPath`""
Write-Host 'Or from install directory:'
Write-Host "  `"$CmdPath`""
Write-Host ''
Write-Host 'Optional: add the install directory to PATH to run reality-sni-smart.cmd from anywhere.'
