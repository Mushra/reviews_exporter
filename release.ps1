$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

if (-not $Version.StartsWith('v')) {
    $Version = 'v' + $Version
}

Write-Host "Creating tag $Version"
git tag $Version
git push origin $Version
