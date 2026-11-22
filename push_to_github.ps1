# Push to GitHub automation script for SmartAgri
# Usage in PowerShell: .\push_to_github.ps1 [-RepoUrl "https://github.com/USERNAME/REPO_NAME.git"]

param(
    [string]$RepoUrl = ""
)

$ErrorActionPreference = "Stop"

# 1. Resolve Git executable (Check PATH, then GitHub Desktop path)
$git = (Get-Command git -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
if (-not $git) {
    $ghPath = Get-ChildItem -Path "$env:LOCALAPPDATA\GitHubDesktop" -Filter "git.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($ghPath -and (Test-Path $ghPath)) {
        $git = $ghPath
    }
}

if (-not $git) {
    Write-Error "Git was not found on this computer. Please install Git or GitHub Desktop."
    exit 1
}

Write-Host "==> Using Git from: $git" -ForegroundColor Cyan

# 2. Check if .git exists, initialize if not
if (-not (Test-Path ".git")) {
    Write-Host "==> Initializing new Git repository..." -ForegroundColor Yellow
    & $git init
    & $git branch -M main
}

# 3. Handle remote repository URL
$currentRemote = & $git remote get-url origin 2>$null
if (-not $currentRemote) {
    if ($RepoUrl) {
        Write-Host "==> Setting remote origin to $RepoUrl..." -ForegroundColor Green
        & $git remote add origin $RepoUrl
    } else {
        Write-Host "==> No remote repository set yet." -ForegroundColor Yellow
        $inputUrl = Read-Host "Enter your GitHub Repository URL (e.g. https://github.com/YourUsername/YourRepo.git)"
        if ($inputUrl) {
            & $git remote add origin $inputUrl.Trim()
        }
    }
} else {
    Write-Host "==> Remote origin already set to: $currentRemote" -ForegroundColor Green
}

# 4. Stage and commit changes
Write-Host "==> Staging changed files..." -ForegroundColor Cyan
& $git add data/karnataka_mandi_benchmarks.json
& $git add models/agmarknet_service.py
& $git add app.py
& $git add smartagri-react/
& $git add tests/
& $git add .gitignore
& $git add static/
& $git add requirements.txt

# Also add any other modified source files tracked by git
& $git add -u

Write-Host "==> Committing updates..." -ForegroundColor Cyan
& $git commit -m "Calibrate Karnataka APMC mandi benchmark prices, update wholesale per-kg display, and optimize crop recommendation agronomics"

# 5. Push to GitHub
Write-Host "==> Pushing to GitHub (main branch)..." -ForegroundColor Green
& $git push -u origin main

Write-Host "==> Successfully pushed to GitHub!" -ForegroundColor Green
