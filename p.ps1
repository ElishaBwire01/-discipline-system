# ============================================================
# DISCIPLINE SYSTEM - SAFE SECRET DISCOVERY & MIGRATION
# ============================================================

$ErrorActionPreference = "Continue"

$ProjectRoot = (Get-Location).Path
$EnvFile = Join-Path $ProjectRoot ".env"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path $ProjectRoot "secret_migration_backup_$Timestamp"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " DISCIPLINE SYSTEM - SECRET MIGRATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 1. BACKUP
# ============================================================

Write-Host "[1] Creating safety backup..." -ForegroundColor Yellow

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null

if (Test-Path $EnvFile) {
    Copy-Item $EnvFile (Join-Path $BackupRoot ".env") -Force
}

Write-Host "  Backup created." -ForegroundColor Green
Write-Host ""

# ============================================================
# 2. READ EXISTING .ENV
# ============================================================

Write-Host "[2] Reading existing .env..." -ForegroundColor Yellow

$ExistingEnv = @{}

if (Test-Path $EnvFile) {

    foreach ($Line in Get-Content $EnvFile) {

        if ($Line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {

            $Name = $Matches[1]
            $Value = $Matches[2]

            $ExistingEnv[$Name] = $Value
        }
    }
}

Write-Host "  Existing variables: $($ExistingEnv.Count)" -ForegroundColor Green
Write-Host ""

# ============================================================
# 3. DIRECTORIES TO SKIP
# ============================================================

$ExcludedDirectories = @(
    ".git",
    ".venv",
    "venv",
    "env",
    "ENV",
    ".kilo",
    ".fix_backup",
    "backups",
    "backup",
    "staticfiles",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode"
)

# ============================================================
# 4. FILES TO SCAN
# ============================================================

Write-Host "[3] Finding configuration files..." -ForegroundColor Yellow

$Extensions = @(
    "*.py",
    "*.ps1",
    "*.env",
    "*.toml",
    "*.ini",
    "*.cfg",
    "*.conf",
    "*.json",
    "*.yaml",
    "*.yml"
)

$Files = @()

foreach ($Extension in $Extensions) {

    $FoundFiles = Get-ChildItem `
        -Path $ProjectRoot `
        -Filter $Extension `
        -File `
        -Recurse `
        -ErrorAction SilentlyContinue

    foreach ($File in $FoundFiles) {

        $RelativePath = $File.FullName.Substring($ProjectRoot.Length).TrimStart("\")
        $Parts = $RelativePath.Split("\")
        $Skip = $false

        foreach ($Excluded in $ExcludedDirectories) {

            if ($Parts -contains $Excluded) {
                $Skip = $true
                break
            }
        }

        if (-not $Skip) {
            $Files += $File
        }
    }
}

$Files = $Files | Sort-Object FullName -Unique

Write-Host "  Files selected for scanning: $($Files.Count)" -ForegroundColor Green
Write-Host ""

# ============================================================
# 5. SECRET PATTERNS
# ============================================================

Write-Host "[4] Searching for possible secrets..." -ForegroundColor Yellow

$SecretPatterns = @{}

$SecretPatterns["GROQ_API_KEY"] = "(?i)(?:GROQ_API_KEY|GROQ_KEY)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["GEMINI_API_KEY"] = "(?i)(?:GEMINI_API_KEY|GOOGLE_API_KEY|GOOGLE_GENERATIVE_AI_KEY)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["OPENAI_API_KEY"] = "(?i)(?:OPENAI_API_KEY)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["SUPABASE_SERVICE_ROLE_KEY"] = "(?i)(?:SUPABASE_SERVICE_ROLE_KEY)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["SUPABASE_ANON_KEY"] = "(?i)(?:SUPABASE_ANON_KEY)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["SUPABASE_JWT_SECRET"] = "(?i)(?:SUPABASE_JWT_SECRET)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["SUPABASE_URL"] = "(?i)(?:SUPABASE_URL)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["DATABASE_URL"] = "(?i)(?:DATABASE_URL)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["SECRET_KEY"] = "(?i)(?:SECRET_KEY|DJANGO_SECRET_KEY)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["AWS_ACCESS_KEY_ID"] = "(?i)(?:AWS_ACCESS_KEY_ID)\s*=\s*['""]([^'""]+)['""]"

$SecretPatterns["AWS_SECRET_ACCESS_KEY"] = "(?i)(?:AWS_SECRET_ACCESS_KEY)\s*=\s*['""]([^'""]+)['""]"

$Discovered = @{}

foreach ($File in $Files) {

    try {
        $Content = Get-Content $File.FullName -Raw -ErrorAction Stop
    }
    catch {
        continue
    }

    foreach ($Name in $SecretPatterns.Keys) {

        $Pattern = $SecretPatterns[$Name]

        try {
            $MatchesFound = [regex]::Matches($Content, $Pattern)
        }
        catch {
            continue
        }

        foreach ($Match in $MatchesFound) {

            if ($Match.Groups.Count -lt 2) {
                continue
            }

            $Value = $Match.Groups[1].Value.Trim()

            if ([string]::IsNullOrWhiteSpace($Value)) {
                continue
            }

            if ($Value -match '^(your_|change_me|replace_|example|xxx|\.\.\.)') {
                continue
            }

            if (-not $Discovered.ContainsKey($Name)) {

                $Discovered[$Name] = @{
                    Value = $Value
                    Files = @()
                }
            }

            $Discovered[$Name].Files += $File.FullName
        }
    }
}

Write-Host ""
Write-Host "  Possible secret variables found: $($Discovered.Count)" -ForegroundColor Green
Write-Host ""

# ============================================================
# 6. WRITE DISCOVERED VALUES TO .ENV
# ============================================================

Write-Host "[5] Moving discovered values into .env..." -ForegroundColor Yellow

$EnvLines = @()

if (Test-Path $EnvFile) {
    $EnvLines = @(Get-Content $EnvFile)
}

$Added = 0

foreach ($Name in ($Discovered.Keys | Sort-Object)) {

    $Value = $Discovered[$Name].Value

    if ($ExistingEnv.ContainsKey($Name)) {

        Write-Host "  [KEEP] $Name already exists" -ForegroundColor Gray

    }
    else {

        $EnvLines += "$Name=$Value"

        $ExistingEnv[$Name] = $Value

        $Added++

        Write-Host "  [ADD]  $Name" -ForegroundColor Green
    }
}

Set-Content `
    -Path $EnvFile `
    -Value $EnvLines `
    -Encoding UTF8

Write-Host ""
Write-Host "  Added: $Added variable(s)" -ForegroundColor Green
Write-Host ""

# ============================================================
# 7. ENSURE .ENV IS IGNORED
# ============================================================

Write-Host "[6] Protecting .env from Git..." -ForegroundColor Yellow

$GitIgnore = Join-Path $ProjectRoot ".gitignore"

if (Test-Path $GitIgnore) {

    $GitIgnoreContent = Get-Content $GitIgnore -Raw

    if ($GitIgnoreContent -notmatch '(?m)^\.env\s*$') {

        Add-Content `
            -Path $GitIgnore `
            -Value "`r`n# Environment secrets`r`n.env`r`n.env.*`r`n!.env.example"

        Write-Host "  .env added to .gitignore." -ForegroundColor Green
    }
    else {

        Write-Host "  .env is already ignored." -ForegroundColor Green
    }
}
else {

    Set-Content `
        -Path $GitIgnore `
        -Value ".env`r`n.env.*`r`n!.env.example" `
        -Encoding UTF8

    Write-Host "  Created .gitignore protection." -ForegroundColor Green
}

Write-Host ""

# ============================================================
# 8. SUMMARY
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " SECRET DISCOVERY COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Variables detected:" -ForegroundColor Yellow

if ($Discovered.Count -eq 0) {

    Write-Host "  No matching secret assignments were found." -ForegroundColor Gray
}
else {

    foreach ($Name in ($Discovered.Keys | Sort-Object)) {

        Write-Host "  [FOUND] $Name" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Red
Write-Host "  Secret values were NOT displayed."
Write-Host "  .env was updated where appropriate."
Write-Host "  Backup location:"
Write-Host "  $BackupRoot"
Write-Host ""

Write-Host "NEXT CHECK:" -ForegroundColor Yellow
Write-Host "  git status --short"
Write-Host ""

Write-Host "DO NOT commit .env." -ForegroundColor Red
Write-Host ""