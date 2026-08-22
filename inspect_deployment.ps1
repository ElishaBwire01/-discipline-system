$ErrorActionPreference = "Continue"

$Root = (Get-Location).Path
$Report = Join-Path $Root "deployment_full_audit.txt"

"============================================================" | Set-Content $Report
" DISCIPLINE SYSTEM - FULL DEPLOYMENT AUDIT" | Add-Content $Report
" READ-ONLY - NO FILES WILL BE MODIFIED" | Add-Content $Report
"============================================================" | Add-Content $Report
"" | Add-Content $Report

function Section($Title) {
    "" | Add-Content $Report
    "============================================================" | Add-Content $Report
    $Title | Add-Content $Report
    "============================================================" | Add-Content $Report
}

function CheckFile($Path) {
    if (Test-Path $Path) {
        "[FOUND]   $Path" | Add-Content $Report
    }
    else {
        "[MISSING] $Path" | Add-Content $Report
    }
}

# ------------------------------------------------------------
# PROJECT
# ------------------------------------------------------------

Section "1. PROJECT LOCATION"

$Root | Add-Content $Report

Section "2. GIT STATUS"

git status --short 2>&1 | Add-Content $Report
git branch --show-current 2>&1 | Add-Content $Report
git remote -v 2>&1 | Add-Content $Report

# ------------------------------------------------------------
# CRITICAL FILES
# ------------------------------------------------------------

Section "3. CRITICAL FILES"

$CriticalFiles = @(
    "manage.py",
    "requirements.txt",
    "vercel.json",
    "pyproject.toml",
    "runtime.txt",
    ".gitignore",
    ".env",
    ".env.example",
    "disciplinary_program/settings.py",
    "disciplinary_program/wsgi.py",
    "disciplinary_program/urls.py",
    "core/apps.py",
    "core/models.py",
    "core/views.py",
    "core/middleware.py",
    "core/urls.py"
)

foreach ($File in $CriticalFiles) {
    CheckFile $File
}

# ------------------------------------------------------------
# PYTHON / DJANGO
# ------------------------------------------------------------

Section "4. PYTHON / DJANGO"

python --version 2>&1 | Add-Content $Report

python -c "import django; print('Django:', django.get_version())" 2>&1 |
    Add-Content $Report

python -c "import sys; print('Python executable:', sys.executable)" 2>&1 |
    Add-Content $Report

# ------------------------------------------------------------
# DJANGO CHECK
# ------------------------------------------------------------

Section "5. DJANGO CHECK"

python manage.py check 2>&1 | Add-Content $Report

# ------------------------------------------------------------
# MIGRATIONS
# ------------------------------------------------------------

Section "6. MIGRATION STATUS"

python manage.py showmigrations 2>&1 | Add-Content $Report

# ------------------------------------------------------------
# STATIC FILES
# ------------------------------------------------------------

Section "7. STATIC FILES"

python manage.py collectstatic --noinput --dry-run 2>&1 |
    Add-Content $Report

# ------------------------------------------------------------
# REQUIREMENTS
# ------------------------------------------------------------

Section "8. REQUIREMENTS.TXT"

Get-Content requirements.txt 2>&1 | Add-Content $Report

# ------------------------------------------------------------
# INSTALLED PACKAGES
# ------------------------------------------------------------

Section "9. IMPORTANT PYTHON PACKAGES"

$Packages = @(
    "django",
    "dj_database_url",
    "dotenv",
    "psycopg2",
    "storages",
    "boto3",
    "groq",
    "google.generativeai",
    "requests",
    "PIL",
    "pandas",
    "openpyxl"
)

foreach ($Package in $Packages) {

    $Result = python -c "import $Package; print('INSTALLED')" 2>&1

    if ($LASTEXITCODE -eq 0) {
        "[OK]       $Package" | Add-Content $Report
    }
    else {
        "[MISSING]  $Package" | Add-Content $Report
    }
}

# ------------------------------------------------------------
# GITIGNORE
# ------------------------------------------------------------

Section "10. GITIGNORE - FULL CONTENT"

Get-Content .gitignore 2>&1 | Add-Content $Report

Section "11. GITIGNORE - MERGE CONFLICT SCAN"

$GitIgnoreText = ""

if (Test-Path ".gitignore") {
    $GitIgnoreText = Get-Content ".gitignore" -Raw
}

if ($GitIgnoreText -match "<<<<<<<|=======|>>>>>>>") {
    "[CRITICAL] Merge conflict markers detected in .gitignore" |
        Add-Content $Report
}
else {
    "[OK] No Git merge conflict markers detected." |
        Add-Content $Report
}

# ------------------------------------------------------------
# SECRET / ENVIRONMENT SCAN
# ------------------------------------------------------------

Section "12. ENVIRONMENT FILES"

Get-ChildItem -Force -File |
    Where-Object {
        $_.Name -match "^\.env"
    } |
    Select-Object Name, Length, LastWriteTime |
    Format-Table -AutoSize |
    Out-String |
    Add-Content $Report

# ------------------------------------------------------------
# GIT TRACKED SECRET FILES
# ------------------------------------------------------------

Section "13. GIT TRACKED ENVIRONMENT FILES"

git ls-files ".env" ".env.*" 2>&1 | Add-Content $Report

# ------------------------------------------------------------
# SECRET PATTERN SCAN
# ------------------------------------------------------------

Section "14. POSSIBLE SECRET PATTERNS"

$SecretPatterns = @(
    "sk-[A-Za-z0-9]",
    "gsk_[A-Za-z0-9]",
    "AIza[A-Za-z0-9]",
    "SUPABASE_SERVICE_ROLE_KEY\s*=",
    "SECRET_KEY\s*="
)

$FilesToScan = Get-ChildItem -Recurse -File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\venv\\" -and
        $_.FullName -notmatch "\\.venv\\" -and
        $_.Name -notmatch "^\.env$"
    }

foreach ($Pattern in $SecretPatterns) {

    "Pattern: $Pattern" | Add-Content $Report

    $Matches = $FilesToScan |
        Select-String -Pattern $Pattern -ErrorAction SilentlyContinue

    if ($Matches) {
        $Matches |
            Select-Object Path, LineNumber, Line |
            Format-Table -AutoSize |
            Out-String |
            Add-Content $Report
    }
    else {
        "  No matches." | Add-Content $Report
    }
}

# ------------------------------------------------------------
# LARGE DIRECTORIES
# ------------------------------------------------------------

Section "15. LARGE PROJECT DIRECTORIES"

$Dirs = @(
    "venv",
    ".venv",
    ".git",
    "media",
    "static",
    "staticfiles",
    "logs",
    "backups_20260707_194316",
    "backup_before_reset_20260629_213651"
)

foreach ($Dir in $Dirs) {

    if (Test-Path $Dir) {

        $Size = (
            Get-ChildItem $Dir -Recurse -File -ErrorAction SilentlyContinue |
            Measure-Object -Property Length -Sum
        ).Sum

        if ($Size) {
            $MB = [math]::Round($Size / 1MB, 2)
        }
        else {
            $MB = 0
        }

        "{0,-45} {1,10} MB" -f $Dir, $MB |
            Add-Content $Report
    }
}

# ------------------------------------------------------------
# VENV TRACKING
# ------------------------------------------------------------

Section "16. GIT TRACKING OF VIRTUAL ENVIRONMENTS"

git ls-files "venv/*" 2>&1 | Select-Object -First 20 |
    Add-Content $Report

git ls-files ".venv/*" 2>&1 | Select-Object -First 20 |
    Add-Content $Report

# ------------------------------------------------------------
# MEDIA TRACKING
# ------------------------------------------------------------

Section "17. GIT TRACKING OF MEDIA"

git ls-files "media/*" 2>&1 | Select-Object -First 50 |
    Add-Content $Report

# ------------------------------------------------------------
# DATABASE TRACKING
# ------------------------------------------------------------

Section "18. DATABASE FILES"

Get-ChildItem -Recurse -File -Include "*.sqlite3","*.db" |
    Where-Object {
        $_.FullName -notmatch "\\.git\\"
    } |
    Select-Object FullName, Length |
    Format-Table -AutoSize |
    Out-String |
    Add-Content $Report

git ls-files "*.sqlite3" "*.db" 2>&1 |
    Add-Content $Report

# ------------------------------------------------------------
# VERCEL
# ------------------------------------------------------------

Section "19. VERCEL.JSON"

if (Test-Path "vercel.json") {
    Get-Content "vercel.json" |
        Add-Content $Report
}
else {
    "[MISSING] vercel.json" | Add-Content $Report
}

# ------------------------------------------------------------
# WSGI
# ------------------------------------------------------------

Section "20. WSGI CONFIGURATION"

if (Test-Path "disciplinary_program/wsgi.py") {

    Get-Content "disciplinary_program/wsgi.py" |
        Add-Content $Report

    $WsgiText = Get-Content "disciplinary_program/wsgi.py" -Raw

    if ($WsgiText -match "app\s*=\s*application") {
        "[OK] app = application detected." | Add-Content $Report
    }
    else {
        "[WARNING] app = application NOT detected." | Add-Content $Report
    }
}

# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

Section "21. SETTINGS DEPLOYMENT CHECK"

$SettingsPath = "disciplinary_program/settings.py"

if (Test-Path $SettingsPath) {

    $Settings = Get-Content $SettingsPath -Raw

    $Checks = [ordered]@{
        "SECRET_KEY environment variable" = "os.environ.get"
        "DEBUG configuration"             = "DEBUG"
        "ALLOWED_HOSTS"                    = "ALLOWED_HOSTS"
        "CSRF_TRUSTED_ORIGINS"             = "CSRF_TRUSTED_ORIGINS"
        "DATABASE_URL"                     = "DATABASE_URL"
        "STATIC_ROOT"                      = "STATIC_ROOT"
        "STATIC_URL"                       = "STATIC_URL"
        "MEDIA_ROOT"                       = "MEDIA_ROOT"
        "TIME_ZONE"                        = "TIME_ZONE"
        "SECURE_PROXY_SSL_HEADER"          = "SECURE_PROXY_SSL_HEADER"
        "SESSION_COOKIE_SECURE"            = "SESSION_COOKIE_SECURE"
        "CSRF_COOKIE_SECURE"               = "CSRF_COOKIE_SECURE"
    }

    foreach ($Check in $Checks.GetEnumerator()) {

        if ($Settings -match [regex]::Escape($Check.Value)) {
            "[FOUND]   $($Check.Key)" | Add-Content $Report
        }
        else {
            "[MISSING] $($Check.Key)" | Add-Content $Report
        }
    }
}

# ------------------------------------------------------------
# URLs
# ------------------------------------------------------------

Section "22. URL CONFIGURATION"

if (Test-Path "disciplinary_program/urls.py") {
    Get-Content "disciplinary_program/urls.py" |
        Add-Content $Report
}

# ------------------------------------------------------------
# FILE COUNTS
# ------------------------------------------------------------

Section "23. PROJECT FILE COUNTS"

$AllFiles = Get-ChildItem -Recurse -File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\venv\\" -and
        $_.FullName -notmatch "\\.venv\\"
    }

"Total project files excluding .git/venv/.venv: $($AllFiles.Count)" |
    Add-Content $Report

$PythonFiles = $AllFiles |
    Where-Object Extension -eq ".py"

"Python files: $($PythonFiles.Count)" |
    Add-Content $Report

$TemplateFiles = $AllFiles |
    Where-Object Extension -in @(".html",".htm")

"HTML/template files: $($TemplateFiles.Count)" |
    Add-Content $Report

$StaticFiles = Get-ChildItem "static" -Recurse -File -ErrorAction SilentlyContinue

"Static files: $($StaticFiles.Count)" |
    Add-Content $Report

# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

Section "24. AUDIT COMPLETE"

"Report generated: $(Get-Date)" | Add-Content $Report
"NO PROJECT FILES WERE MODIFIED." | Add-Content $Report

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " DEPLOYMENT AUDIT COMPLETE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Report:" -ForegroundColor Yellow
Write-Host $Report -ForegroundColor White
Write-Host ""

# Open report in VS Code
if (Get-Command code -ErrorAction SilentlyContinue) {
    code $Report
}
else {
    Write-Host "VS Code command 'code' was not found." -ForegroundColor Yellow
    Write-Host "Open the file manually:" -ForegroundColor Yellow
    Write-Host $Report
}

Write-Host ""
Write-Host "IMPORTANT: This was READ-ONLY. Nothing was changed." -ForegroundColor Green