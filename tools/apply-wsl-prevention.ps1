# Install the reviewed WSL limits without overwriting an existing configuration.
# This script deliberately never runs wsl --shutdown.
$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot '..\config\wslconfig.recommended'
$content = [IO.File]::ReadAllText($source).Replace("`r`n", "`n").Replace("`n", "`r`n")
$target = Join-Path $env:USERPROFILE '.wslconfig'
if (Test-Path $target) {
    if ([IO.File]::ReadAllText($target) -eq $content) {
        Write-Output "Already installed: $target"
        exit 0
    }
    throw "An existing $target differs from the reviewed configuration. It was not overwritten."
}
$bytes = [Text.UTF8Encoding]::new($false).GetBytes($content)
$stream = [IO.File]::Open($target, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush() } finally { $stream.Dispose() }
Write-Output "Installed: $target"
Get-Content $target
Write-Output 'Pending activation at the next WSL restart. No shutdown was performed.'
