# ============================================================
# VERCEL DJANGO LOGGING FIX
# ============================================================

$ErrorActionPreference = "Stop"

$settingsFile = "disciplinary_program/settings.py"
$backupFile = "disciplinary_program/settings.py.backup_before_vercel_fix"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DJANGO VERCEL LOGGING FIX" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# 1. Check settings.py exists
# ------------------------------------------------------------

if (-not (Test-Path $settingsFile)) {
    Write-Host "ERROR: $settingsFile was not found." -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------
# 2. Create backup
# ------------------------------------------------------------

Copy-Item $settingsFile $backupFile -Force

Write-Host "Backup created:" -ForegroundColor Green
Write-Host "  $backupFile"
Write-Host ""

# ------------------------------------------------------------
# 3. Read settings.py
# ------------------------------------------------------------

$settings = Get-Content $settingsFile -Raw

# ------------------------------------------------------------
# 4. Find LOGGING section
# ------------------------------------------------------------

$loggingStart = $settings.IndexOf("LOGGING = {")

if ($loggingStart -lt 0) {
    Write-Host "ERROR: Could not find 'LOGGING = {' in settings.py." -ForegroundColor Red
    Write-Host "Your original file has NOT been changed." -ForegroundColor Yellow
    exit 1
}

# ------------------------------------------------------------
# 5. Find the end of the LOGGING dictionary
# ------------------------------------------------------------

$braceCount = 0
$loggingEnd = -1
$started = $false

for ($i = $loggingStart; $i -lt $settings.Length; $i++) {

    $char = $settings[$i]

    if ($char -eq "{") {
        $braceCount++
        $started = $true
    }
    elseif ($char -eq "}") {
        $braceCount--

        if ($started -and $braceCount -eq 0) {
            $loggingEnd = $i + 1
            break
        }
    }
}

if ($loggingEnd -lt 0) {
    Write-Host "ERROR: Could not determine the end of LOGGING section." -ForegroundColor Red
    Write-Host "Your original file has NOT been changed." -ForegroundColor Yellow
    exit 1
}

# ------------------------------------------------------------
# 6. Find existing LOGS_DIR section before LOGGING
# ------------------------------------------------------------

$logsMarker = "# ============================================================"
$logsSearchStart = $settings.LastIndexOf("LOGS_DIR", $loggingStart)

if ($logsSearchStart -ge 0) {

    $previousSectionStart = $settings.LastIndexOf("LOGGING", $logsSearchStart)

    if ($previousSectionStart -ge 0) {
        $logsStart = $previousSectionStart
    }
    else {
        $logsStart = $logsSearchStart
    }
}
else {
    $logsStart = $loggingStart
}

# ------------------------------------------------------------
# 7. Build Vercel-safe logging configuration
# ------------------------------------------------------------

$newLogging = @'
# ============================================================
# LOGGING - VERCEL SAFE
# ============================================================

if IS_VERCEL:
    # Vercel filesystem is read-only except for /tmp
    LOGS_DIR = Path("/tmp/logs")
else:
    LOGS_DIR = BASE_DIR / "logs"

# Safely create the logging directory
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    LOGS_DIR = None

LOG_FILE = LOGS_DIR / "django.log" if LOGS_DIR else None

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "json": {
            "format": '{"level": "{levelname}", "time": "{asctime}", "module": "{name}", "message": "{message}"}',
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json" if IS_VERCEL else "simple",
        },
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# File logging is optional.
# Vercel should primarily use console logging.
if LOGS_DIR and LOG_FILE:
    try:
        LOGGING["handlers"]["file"] = {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "formatter": "simple",
        }

        LOGGING["root"]["handlers"].append("file")

    except (OSError, PermissionError):
        pass
'@

# ------------------------------------------------------------
# 8. Replace the logging block
# ------------------------------------------------------------

$before = $settings.Substring(0, $logsStart)
$after = $settings.Substring($loggingEnd)

$newSettings = $before + $newLogging + "`r`n`r`n" + $after

# ------------------------------------------------------------
# 9. Write modified settings.py
# ------------------------------------------------------------

Set-Content $settingsFile $newSettings -Encoding UTF8

Write-Host "settings.py updated successfully." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------
# 10. Check Django
# ------------------------------------------------------------

Write-Host "Running Django system check..." -ForegroundColor Cyan
Write-Host ""

python manage.py check

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Django check FAILED." -ForegroundColor Red
    Write-Host "Restoring original settings.py..." -ForegroundColor Yellow

    Copy-Item $backupFile $settingsFile -Force

    Write-Host "Original settings.py restored." -ForegroundColor Green
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       VERCEL FIX COMPLETED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Django system check passed." -ForegroundColor Green
Write-Host ""
Write-Host "Backup:"
Write-Host "  $backupFile"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  git diff -- disciplinary_program/settings.py"
Write-Host "  git add disciplinary_program/settings.py"
Write-Host "  git commit -m `"fix: Vercel read-only filesystem logging`""
Write-Host "  git push origin fix/ai-gemini-groq-sanitize"
Write-Host ""
Write-Host "Then redeploy on Vercel." -ForegroundColor Green
Write-Host ""