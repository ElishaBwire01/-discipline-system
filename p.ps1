# ============================================================
# DISCIPLINE SYSTEM - COMPLETE DEPLOYMENT AUDIT
# SAFE READ-ONLY VERSION
# ============================================================

$ErrorActionPreference = "Continue"

$ProjectRoot = (Get-Location).Path
$ReportPath = Join-Path $ProjectRoot "deployment_audit_results.txt"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " DISCIPLINE SYSTEM - COMPLETE DEPLOYMENT AUDIT" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectRoot"
Write-Host ""

# ------------------------------------------------------------
# REPORT INITIALIZATION
# ------------------------------------------------------------

@"
============================================================
DISCIPLINE SYSTEM - COMPLETE DEPLOYMENT AUDIT
============================================================

Project:
$ProjectRoot

Audit time:
$(Get-Date)

This report is READ-ONLY.
No files are deleted.
No Git commit is created.
No Git push is performed.

============================================================

"@ | Set-Content -Path $ReportPath -Encoding UTF8


function Write-Report {
    param(
        [string]$Text
    )

    Write-Host $Text
    Add-Content -Path $ReportPath -Value $Text
}


function Section {
    param(
        [string]$Title
    )

    $Line = "`n============================================================"
    Write-Report $Line
    Write-Report $Title
    Write-Report "============================================================"
}


# ============================================================
# 1. PROJECT ROOT
# ============================================================

Section "1. PROJECT ROOT"

Write-Report "Current directory:"
Write-Report $ProjectRoot


# ============================================================
# 2. IMPORTANT FILES
# ============================================================

Section "2. IMPORTANT PROJECT FILES"

$ImportantFiles = @(
    "manage.py",
    "requirements.txt",
    "vercel.json",
    "pyproject.toml",
    ".gitignore",
    ".env",
    ".env.example",
    "disciplinary_program/settings.py",
    "disciplinary_program/wsgi.py",
    "disciplinary_program/urls.py",
    "core/apps.py",
    "core/models.py",
    "core/views.py",
    "core/urls.py"
)

foreach ($File in $ImportantFiles) {

    if (Test-Path $File) {
        Write-Report "[FOUND]   $File"
    }
    else {
        Write-Report "[MISSING] $File"
    }
}


# ============================================================
# 3. PYTHON
# ============================================================

Section "3. PYTHON ENVIRONMENT"

try {
    $PythonVersion = python --version 2>&1
    Write-Report "Python: $PythonVersion"
}
catch {
    Write-Report "[ERROR] Python command unavailable."
}


# ============================================================
# 4. DJANGO VERSION
# ============================================================

Section "4. DJANGO VERSION"

try {
    $DjangoVersion = python -c "import django; print(django.get_version())" 2>&1
    Write-Report "Django: $DjangoVersion"
}
catch {
    Write-Report "[ERROR] Unable to import Django."
}


# ============================================================
# 5. DJANGO CHECK
# ============================================================

Section "5. DJANGO SYSTEM CHECK"

python manage.py check 2>&1 |
    Tee-Object -Variable DjangoCheck |
    ForEach-Object {
        Write-Report "$_"
    }

if ($LASTEXITCODE -eq 0) {
    Write-Report ""
    Write-Report "[PASS] Django system check passed."
}
else {
    Write-Report ""
    Write-Report "[FAIL] Django system check failed."
}


# ============================================================
# 6. MIGRATIONS
# ============================================================

Section "6. MIGRATION STATUS"

python manage.py showmigrations 2>&1 |
    Tee-Object -Variable MigrationOutput |
    ForEach-Object {
        Write-Report "$_"
    }


# ============================================================
# 7. COLLECT STATIC
# ============================================================

Section "7. STATIC FILE COLLECTION"

python manage.py collectstatic --noinput --clear 2>&1 |
    Tee-Object -Variable StaticOutput |
    ForEach-Object {
        Write-Report "$_"
    }

if ($LASTEXITCODE -eq 0) {
    Write-Report ""
    Write-Report "[PASS] collectstatic completed successfully."
}
else {
    Write-Report ""
    Write-Report "[FAIL] collectstatic failed."
}


# ============================================================
# 8. REQUIREMENTS
# ============================================================

Section "8. REQUIREMENTS.TXT"

if (Test-Path "requirements.txt") {

    Get-Content "requirements.txt" |
        ForEach-Object {
            Write-Report $_
        }

}
else {

    Write-Report "[MISSING] requirements.txt"

}


# ============================================================
# 9. REQUIRED PYTHON PACKAGES
# ============================================================

Section "9. REQUIRED PYTHON PACKAGES"

$Packages = @(
    "django",
    "dj_database_url",
    "dotenv",
    "psycopg2",
    "storages",
    "boto3",
    "groq",
    "google.generativeai"
)

foreach ($Package in $Packages) {

    $Result = python -c "import $Package; print('OK')" 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Report "[OK]      $Package"
    }
    else {
        Write-Report "[MISSING] $Package"
    }
}


# ============================================================
# 10. GITIGNORE
# ============================================================

Section "10. GITIGNORE AUDIT"

if (Test-Path ".gitignore") {

    $GitIgnoreContent = Get-Content ".gitignore" -Raw

    if ($GitIgnoreContent -match "<<<<<<<") {
        Write-Report "[CRITICAL] Git merge marker <<<<<<< found."
    }

    if ($GitIgnoreContent -match "=======") {
        Write-Report "[CRITICAL] Git merge marker ======= found."
    }

    if ($GitIgnoreContent -match ">>>>>>>") {
        Write-Report "[CRITICAL] Git merge marker >>>>>>> found."
    }

    if (
        ($GitIgnoreContent -notmatch "<<<<<<<") -and
        ($GitIgnoreContent -notmatch "=======") -and
        ($GitIgnoreContent -notmatch ">>>>>>>")
    ) {
        Write-Report "[PASS] No Git merge conflict markers found."
    }

    $RequiredIgnorePatterns = @(
        ".env",
        "venv/",
        ".venv/",
        "__pycache__/",
        "staticfiles/",
        "media/",
        "*.sqlite3"
    )

    foreach ($Pattern in $RequiredIgnorePatterns) {

        if ($GitIgnoreContent -match [regex]::Escape($Pattern)) {
            Write-Report "[OK] $Pattern"
        }
        else {
            Write-Report "[WARNING] Missing pattern: $Pattern"
        }
    }

}
else {

    Write-Report "[CRITICAL] .gitignore is missing."

}


# ============================================================
# 11. GIT TRACKING AUDIT
# ============================================================

Section "11. GIT TRACKED SECRET / LARGE FILE AUDIT"

$TrackedFiles = git ls-files 2>&1

$RiskPatterns = @(
    "\.env$",
    "env\.ps1$",
    "Untitled.*\.ps1$",
    "\.sqlite3$",
    "venv/",
    "\.venv/",
    "backup",
    "backups",
    "\.fix_backup/",
    "supabase/config\.toml"
)

foreach ($Pattern in $RiskPatterns) {

    $Matches = $TrackedFiles |
        Where-Object {
            $_ -match $Pattern
        }

    if ($Matches) {

        Write-Report ""
        Write-Report "[WARNING] Git-tracked files matching: $Pattern"

        foreach ($Match in $Matches) {
            Write-Report "    $Match"
        }

    }
}


# ============================================================
# 12. SECRET PATTERN SCAN
# ============================================================

Section "12. SECRET PATTERN SCAN"

$SecretExtensions = @(
    "*.py",
    "*.ps1",
    "*.json",
    "*.toml",
    "*.yml",
    "*.yaml",
    "*.ini",
    "*.txt"
)

$SecretRegexes = @(
    "gsk_[A-Za-z0-9_-]{20,}",
    "AIza[A-Za-z0-9_-]{20,}",
    "sk-[A-Za-z0-9_-]{20,}",
    "service_role",
    "SUPABASE_SERVICE_ROLE_KEY\s*=",
    "SECRET_KEY\s*=\s*['""]"
)

$SecretMatchesFound = $false

foreach ($Extension in $SecretExtensions) {

    $Files = Get-ChildItem `
        -Path $ProjectRoot `
        -Filter $Extension `
        -Recurse `
        -File `
        -ErrorAction SilentlyContinue

    foreach ($File in $Files) {

        if (
            $File.FullName -match "\\.git\\" -or
            $File.FullName -match "\\venv\\" -or
            $File.FullName -match "\\.venv\\" -or
            $File.FullName -match "\\node_modules\\"
        ) {
            continue
        }

        try {

            $Content = Get-Content $File.FullName -Raw -ErrorAction Stop

            foreach ($Regex in $SecretRegexes) {

                if ($Content -match $Regex) {

                    $SecretMatchesFound = $true

                    $RelativePath = $File.FullName.Replace(
                        "$ProjectRoot\",
                        ""
                    )

                    Write-Report "[WARNING] Possible secret pattern: $RelativePath"
                    Write-Report "          Pattern: $Regex"

                }
            }

        }
        catch {
        }
    }
}

if (-not $SecretMatchesFound) {
    Write-Report "[PASS] No obvious secret patterns found."
}


# ============================================================
# 13. SETTINGS.PY AUDIT
# ============================================================

Section "13. DJANGO SETTINGS AUDIT"

$SettingsPath = "disciplinary_program/settings.py"

if (Test-Path $SettingsPath) {

    $Settings = Get-Content $SettingsPath -Raw

    $SettingsChecks = @(
        "SECRET_KEY",
        "DEBUG",
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "DATABASES",
        "STATIC_URL",
        "STATIC_ROOT",
        "TIME_ZONE",
        "WSGI_APPLICATION"
    )

    foreach ($Check in $SettingsChecks) {

        if ($Settings -match $Check) {
            Write-Report "[FOUND] $Check"
        }
        else {
            Write-Report "[MISSING] $Check"
        }

    }

}
else {

    Write-Report "[CRITICAL] settings.py missing."

}


# ============================================================
# 14. WSGI AUDIT
# ============================================================

Section "14. WSGI AUDIT"

$WsgiPath = "disciplinary_program/wsgi.py"

if (Test-Path $WsgiPath) {

    $Wsgi = Get-Content $WsgiPath -Raw

    if ($Wsgi -match "get_wsgi_application") {
        Write-Report "[OK] get_wsgi_application found."
    }
    else {
        Write-Report "[FAIL] get_wsgi_application missing."
    }

    if ($Wsgi -match "app\s*=\s*application") {
        Write-Report "[OK] Vercel-compatible app export found."
    }
    else {
        Write-Report "[WARNING] app = application not found."
    }

}
else {

    Write-Report "[CRITICAL] WSGI file missing."

}


# ============================================================
# 15. VERCEL.JSON
# ============================================================

Section "15. VERCEL.JSON"

if (Test-Path "vercel.json") {

    try {

        $Vercel = Get-Content "vercel.json" -Raw |
            ConvertFrom-Json

        Write-Report "[PASS] vercel.json is valid JSON."

        if ($Vercel.builds) {
            Write-Report "[FOUND] builds configuration."
        }

        if ($Vercel.routes) {
            Write-Report "[FOUND] routes configuration."
        }

    }
    catch {

        Write-Report "[FAIL] vercel.json contains invalid JSON."

    }

}
else {

    Write-Report "[CRITICAL] vercel.json missing."

}


# ============================================================
# 16. PYPROJECT
# ============================================================

Section "16. PYPROJECT.TOML"

if (Test-Path "pyproject.toml") {

    Write-Report "[FOUND] pyproject.toml"

    Get-Content "pyproject.toml" |
        ForEach-Object {
            Write-Report $_
        }

}
else {

    Write-Report "[WARNING] pyproject.toml missing."

}


# ============================================================
# 17. ENVIRONMENT FILES
# ============================================================

Section "17. ENVIRONMENT FILE AUDIT"

if (Test-Path ".env") {

    Write-Report "[FOUND] .env exists."
    Write-Report "[IMPORTANT] Contents intentionally NOT printed."

}
else {

    Write-Report "[WARNING] .env missing."

}

if (Test-Path ".env.example") {

    Write-Report "[FOUND] .env.example exists."

}
else {

    Write-Report "[WARNING] .env.example missing."

}


# ============================================================
# 18. VIRTUAL ENVIRONMENTS
# ============================================================

Section "18. VIRTUAL ENVIRONMENT SIZE"

$VenvPaths = @(
    "venv",
    ".venv",
    "env",
    "ENV"
)

foreach ($Venv in $VenvPaths) {

    if (Test-Path $Venv) {

        $Size = (
            Get-ChildItem `
                -Path $Venv `
                -Recurse `
                -File `
                -ErrorAction SilentlyContinue |
            Measure-Object -Property Length -Sum
        ).Sum

        $SizeMB = [math]::Round(
            ($Size / 1MB),
            2
        )

        Write-Report "$Venv : $SizeMB MB"

    }

}


# ============================================================
# 19. GIT STATUS
# ============================================================

Section "19. GIT STATUS"

git status --short 2>&1 |
    ForEach-Object {
        Write-Report $_
    }


# ============================================================
# 20. GIT REMOTE
# ============================================================

Section "20. GIT REMOTE"

git remote -v 2>&1 |
    ForEach-Object {
        Write-Report $_
    }


# ============================================================
# 21. CURRENT BRANCH
# ============================================================

Section "21. CURRENT BRANCH"

git branch --show-current 2>&1 |
    ForEach-Object {
        Write-Report $_
    }


# ============================================================
# 22. GIT LARGE FILE CHECK
# ============================================================

Section "22. LARGE TRACKED FILE CHECK"

$LargeTrackedFiles = Get-ChildItem `
    -Path $ProjectRoot `
    -Recurse `
    -File `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Length -gt 10MB
    }

foreach ($File in $LargeTrackedFiles) {

    $Relative = $File.FullName.Replace(
        "$ProjectRoot\",
        ""
    )

    $SizeMB = [math]::Round(
        ($File.Length / 1MB),
        2
    )

    Write-Report "$SizeMB MB`t$Relative"
}


# ============================================================
# 23. DIRECTORY STRUCTURE
# ============================================================

Section "23. TOP-LEVEL DIRECTORY STRUCTURE"

Get-ChildItem -Directory |
    Select-Object Name |
    ForEach-Object {
        Write-Report $_.Name
    }


# ============================================================
# 24. DEPLOYMENT READINESS SUMMARY
# ============================================================

Section "24. DEPLOYMENT READINESS SUMMARY"

Write-Report ""
Write-Report "The audit has finished."
Write-Report ""
Write-Report "IMPORTANT:"
Write-Report "This script intentionally did NOT modify your project."
Write-Report "Review the findings before making deployment changes."
Write-Report ""
Write-Report "Next recommended checks:"
Write-Report "1. Fix any .gitignore conflict markers."
Write-Report "2. Remove secrets from Git tracking/history if detected."
Write-Report "3. Confirm requirements.txt contains every imported production dependency."
Write-Report "4. Confirm Vercel configuration matches the actual Django project."
Write-Report "5. Confirm Supabase DATABASE_URL is configured in Vercel."
Write-Report "6. Run a final Django check."
Write-Report "7. Run a final collectstatic."
Write-Report "8. Commit only after reviewing Git status."
Write-Report ""

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " AUDIT COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Report created:" -ForegroundColor Cyan
Write-Host $ReportPath -ForegroundColor White
Write-Host ""

# ============================================================
# OPEN REPORT IN VS CODE
# ============================================================

if (Get-Command code -ErrorAction SilentlyContinue) {

    Write-Host "Opening report in VS Code..." -ForegroundColor Cyan
    code $ReportPath

}
else {

    Write-Host "VS Code 'code' command was not found." -ForegroundColor Yellow
    Write-Host "Open manually:" -ForegroundColor Yellow
    Write-Host $ReportPath

}

Write-Host ""