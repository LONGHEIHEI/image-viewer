Write-Host "Installing archive Python dependencies..."
pip install py7zr rarfile

$unrar = Get-Command unrar -ErrorAction SilentlyContinue
$sevenZip = Get-Command 7z -ErrorAction SilentlyContinue

if (-not $unrar -and -not $sevenZip) {
  Write-Host "RAR support needs an unrar backend. Install 7-Zip or unrar and ensure it's in PATH."
}

Write-Host "Done. You can now use .7z and .rar archives."
