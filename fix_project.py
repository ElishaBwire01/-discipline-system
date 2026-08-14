#!/usr/bin/env python3
"""
Django Discipline Management System - Complete Debug & Fix Script
Fixed Version - Handles encoding errors and Windows paths
"""

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import chardet

try:
    import libcst as cst
    import libcst.matchers as m
    LIBCST_AVAILABLE = True
except ImportError:
    LIBCST_AVAILABLE = False

try:
    import black
    import isort
    RUFF_AVAILABLE = True
except ImportError:
    RUFF_AVAILABLE = False

try:
    import django
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Issue:
    """Represents a code issue found during scanning"""
    file_path: str
    line_number: int
    severity: str  # ERROR, WARNING, INFO, SUGGESTION
    category: str  # import, syntax, style, security, performance, django
    message: str
    fix: Optional[str] = None
    auto_fixable: bool = False
    suggestion: Optional[str] = None

@dataclass
class Fix:
    """Represents a fix applied to a file"""
    file_path: str
    line_number: int
    original: str
    fixed: str
    category: str
    description: str

@dataclass
class FileInfo:
    """Information about a Python file"""
    path: Path
    size: int
    lines: int
    imports: Set[str]
    classes: Set[str]
    functions: Set[str]
    has_syntax_error: bool = False
    syntax_error: Optional[str] = None
    issues: List[Issue] = field(default_factory=list)
    fixes: List[Fix] = field(default_factory=list)
    hash: str = ""
    modified: bool = False

@dataclass
class ProjectReport:
    """Complete project analysis report"""
    timestamp: datetime
    total_files: int
    analyzed_files: int
    total_issues: int
    critical_issues: int
    warnings: int
    info: int
    suggestions: int
    auto_fixes_applied: int
    manual_fixes_needed: int
    files: List[FileInfo] = field(default_factory=list)
    issues: List[Issue] = field(default_factory=list)  # Added this field
    issues_by_category: Dict[str, int] = field(default_factory=dict)
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    test_results: Dict[str, Any] = field(default_factory=dict)
    coverage_info: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# PROJECT SCANNER
# ============================================================================

class ProjectScanner:
    """Scans the Django project for issues"""

    def __init__(self, project_root: str, exclude_dirs: List[str] = None):
        self.project_root = Path(project_root).resolve()
        self.exclude_dirs = exclude_dirs or [
            'venv', 'env', '.venv', '__pycache__', '.git', 'node_modules',
            'migrations', 'static', 'media', '.pytest_cache', '.mypy_cache',
            'backup', 'backups', '.fix_backup'
        ]
        self.files: Dict[str, FileInfo] = {}
        self.issues: List[Issue] = []
        self.fixes: List[Fix] = []
        self.report = ProjectReport(
            timestamp=datetime.now(),
            total_files=0,
            analyzed_files=0,
            total_issues=0,
            critical_issues=0,
            warnings=0,
            info=0,
            suggestions=0,
            auto_fixes_applied=0,
            manual_fixes_needed=0,
            issues=[],  # Initialize empty list
            issues_by_category=defaultdict(int),
            issues_by_severity=defaultdict(int)
        )

    def read_file_safe(self, file_path: Path) -> Optional[str]:
        """Read file with automatic encoding detection"""
        try:
            # Try UTF-8 first
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try Latin-1
                return file_path.read_text(encoding='latin-1')
            except UnicodeDecodeError:
                try:
                    # Auto-detect encoding
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                        detected = chardet.detect(raw_data)
                        encoding = detected.get('encoding', 'utf-8')
                        return raw_data.decode(encoding, errors='ignore')
                except:
                    # Last resort: ignore errors
                    return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
            return None

    def scan(self):
        """Scan the entire project"""
        print("🔍 Scanning Django project...")
        print(f"📁 Project root: {self.project_root}")

        python_files = self._get_python_files()
        self.report.total_files = len(python_files)

        for py_file in python_files:
            self._analyze_file(py_file)

        self.report.analyzed_files = len(self.files)
        self._compile_report()

        print(f"✅ Scan complete! Found {len(self.issues)} issues")
        return self.report

    def _get_python_files(self) -> List[Path]:
        """Get all Python files in the project"""
        python_files = []
        for py_file in self.project_root.rglob("*.py"):
            # Skip excluded directories
            should_exclude = False
            for exclude in self.exclude_dirs:
                if exclude in str(py_file.parts):
                    should_exclude = True
                    break
            if should_exclude:
                continue
            python_files.append(py_file)
        return python_files

    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            content = self.read_file_safe(file_path)
            if content is None:
                return

            lines = content.split('\n')

            # Calculate file hash
            file_hash = hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

            # Parse with AST
            try:
                tree = ast.parse(content, filename=str(file_path))
                imports = self._extract_imports(tree)
                classes = self._extract_classes(tree)
                functions = self._extract_functions(tree)
                has_syntax_error = False
                syntax_error = None
            except SyntaxError as e:
                has_syntax_error = True
                syntax_error = str(e)
                imports = set()
                classes = set()
                functions = set()
                self.issues.append(Issue(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    severity='ERROR',
                    category='syntax',
                    message=f"Syntax error: {e.msg}",
                    auto_fixable=True,
                    suggestion="Fix the syntax error"
                ))

            # Create FileInfo
            file_info = FileInfo(
                path=file_path,
                size=file_path.stat().st_size,
                lines=len(lines),
                imports=imports,
                classes=classes,
                functions=functions,
                has_syntax_error=has_syntax_error,
                syntax_error=syntax_error,
                hash=file_hash
            )

            # Analyze for Django-specific issues
            django_issues = self._analyze_django_file(content, str(file_path), lines)
            file_info.issues.extend(django_issues)
            self.issues.extend(django_issues)

            # Analyze style and structure
            style_issues = self._analyze_style(content, str(file_path), lines)
            file_info.issues.extend(style_issues)
            self.issues.extend(style_issues)

            # Analyze imports
            import_issues = self._analyze_imports(content, str(file_path), lines)
            file_info.issues.extend(import_issues)
            self.issues.extend(import_issues)

            # Analyze security
            security_issues = self._analyze_security(content, str(file_path), lines)
            file_info.issues.extend(security_issues)
            self.issues.extend(security_issues)

            self.files[str(file_path)] = file_info

        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
            traceback.print_exc()

    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extract imports from AST"""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        return imports

    def _extract_classes(self, tree: ast.AST) -> Set[str]:
        """Extract class names from AST"""
        classes = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)
        return classes

    def _extract_functions(self, tree: ast.AST) -> Set[str]:
        """Extract function names from AST"""
        functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.add(node.name)
        return functions

    def _analyze_django_file(self, content: str, file_path: str, lines: List[str]) -> List[Issue]:
        """Analyze Django-specific issues"""
        issues = []

        # Check for common Django mistakes
        django_patterns = [
            (r'Paginator\([^)]*,\s*(\d+)\)', 'Paginator with hardcoded per_page, consider using request.GET.get("per_page", 20)', 'WARNING'),
            (r'HttpResponse\(.*\)', 'Consider using render() or JsonResponse for better response handling', 'INFO'),
            (r'@login_required', 'Good: Using login_required decorator', 'INFO'),
            (r'@user_passes_test', 'Good: Using user_passes_test decorator', 'INFO'),
            (r'from django.contrib.auth.models import User', 'Consider using settings.AUTH_USER_MODEL for better flexibility', 'SUGGESTION'),
            (r'\.objects\.all\(\)', 'Consider using .objects.all() with pagination for large querysets', 'INFO'),
            (r'\.save\(\)', 'Consider using .update() for batch operations', 'SUGGESTION'),
        ]

        for pattern, message, severity in django_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                issues.append(Issue(
                    file_path=file_path,
                    line_number=line_no,
                    severity=severity,
                    category='django',
                    message=message,
                    auto_fixable=False
                ))

        return issues

    def _analyze_style(self, content: str, file_path: str, lines: List[str]) -> List[Issue]:
        """Analyze code style issues"""
        issues = []

        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > 120 and not line.strip().startswith('#'):
                issues.append(Issue(
                    file_path=file_path,
                    line_number=i,
                    severity='WARNING',
                    category='style',
                    message=f"Line too long ({len(line)} > 120 characters)",
                    auto_fixable=True,
                    suggestion="Break the line into multiple lines"
                ))

            # Check trailing whitespace
            if line.rstrip('\n') != line.rstrip():
                issues.append(Issue(
                    file_path=file_path,
                    line_number=i,
                    severity='WARNING',
                    category='style',
                    message="Trailing whitespace detected",
                    auto_fixable=True,
                    suggestion="Remove trailing whitespace"
                ))

        # Check for TODO comments
        for i, line in enumerate(lines, 1):
            if 'TODO' in line or 'FIXME' in line:
                issues.append(Issue(
                    file_path=file_path,
                    line_number=i,
                    severity='INFO',
                    category='style',
                    message=f"TODO/FIXME comment: {line.strip()}",
                    auto_fixable=False
                ))

        return issues

    def _analyze_imports(self, content: str, file_path: str, lines: List[str]) -> List[Issue]:
        """Analyze import issues"""
        issues = []

        # Check for unused imports (simplified)
        import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
        found_imports = re.findall(import_pattern, content, re.MULTILINE)

        for match in found_imports:
            imported = match[0] or match[1]
            # Simple check: if the imported module name doesn't appear elsewhere
            if imported and imported not in content:
                issues.append(Issue(
                    file_path=file_path,
                    line_number=1,
                    severity='WARNING',
                    category='import',
                    message=f"Possible unused import: {imported}",
                    auto_fixable=True,
                    suggestion="Remove unused import"
                ))

        return issues

    def _analyze_security(self, content: str, file_path: str, lines: List[str]) -> List[Issue]:
        """Analyze security issues"""
        issues = []

        # Check for hardcoded secrets
        secrets_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password detected', 'CRITICAL'),
            (r'secret_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded SECRET_KEY detected', 'CRITICAL'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key detected', 'CRITICAL'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token detected', 'CRITICAL'),
        ]

        for pattern, message, severity in secrets_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                issues.append(Issue(
                    file_path=file_path,
                    line_number=line_no,
                    severity=severity,
                    category='security',
                    message=message,
                    auto_fixable=False,
                    suggestion="Use environment variables instead"
                ))

        # Check for dangerous functions
        dangerous = ['eval(', 'exec(', 'subprocess.run', '__import__']
        for func in dangerous:
            if func in content:
                line_no = content.find(func) and content[:content.find(func)].count('\n') + 1
                issues.append(Issue(
                    file_path=file_path,
                    line_number=line_no or 1,
                    severity='WARNING',
                    category='security',
                    message=f"Potentially dangerous function: {func}",
                    auto_fixable=False,
                    suggestion="Ensure proper input sanitization"
                ))

        return issues

    def _compile_report(self):
        """Compile the final report"""
        # Count issues by severity
        for issue in self.issues:
            if issue.severity == 'ERROR' or issue.severity == 'CRITICAL':
                self.report.critical_issues += 1
            elif issue.severity == 'WARNING':
                self.report.warnings += 1
            elif issue.severity == 'INFO':
                self.report.info += 1
            elif issue.severity == 'SUGGESTION':
                self.report.suggestions += 1

            self.report.issues_by_category[issue.category] += 1
            self.report.issues_by_severity[issue.severity] += 1

        # Add all issues to report
        self.report.issues = self.issues
        self.report.total_issues = len(self.issues)

# ============================================================================
# PROJECT FIXER
# ============================================================================

class ProjectFixer:
    """Fixes issues found during scanning"""

    def __init__(self, project_root: str, backup: bool = True):
        self.project_root = Path(project_root).resolve()
        self.backup = backup
        self.backup_dir = self.project_root / ".fix_backup"
        self.fixes: List[Fix] = []
        self.fixed_files: Set[str] = set()

        if backup:
            try:
                self.backup_dir.mkdir(exist_ok=True, parents=True)
            except Exception as e:
                print(f"⚠️ Could not create backup directory: {e}")

    def fix_imports(self, file_path: str) -> bool:
        """Fix import issues"""
        try:
            path = Path(file_path)
            content = self._read_file_safe(path)
            if content is None:
                return False

            original = content

            # Use isort if available
            if RUFF_AVAILABLE:
                try:
                    content = isort.code(content, profile='black')
                except:
                    pass

            # Manual import cleanup
            lines = content.split('\n')
            fixed_lines = []
            imports_seen = set()
            in_imports = False

            for line in lines:
                if line.strip().startswith(('import ', 'from ')):
                    if not in_imports:
                        in_imports = True
                    # Check for duplicate imports
                    import_key = re.sub(r'\s+', ' ', line.strip())
                    if import_key not in imports_seen:
                        imports_seen.add(import_key)
                        fixed_lines.append(line)
                else:
                    if in_imports:
                        in_imports = False
                    fixed_lines.append(line)

            content = '\n'.join(fixed_lines)

            if content != original:
                if self.backup:
                    self._backup_file(file_path)
                self._write_file_safe(path, content)
                self.fixed_files.add(file_path)
                return True

            return False

        except Exception as e:
            print(f"❌ Error fixing imports in {file_path}: {e}")
            return False

    def fix_trailing_whitespace(self, file_path: str) -> bool:
        """Remove trailing whitespace"""
        try:
            path = Path(file_path)
            content = self._read_file_safe(path)
            if content is None:
                return False

            original = content

            lines = content.split('\n')
            fixed_lines = [line.rstrip() for line in lines]
            content = '\n'.join(fixed_lines)

            if content != original:
                if self.backup:
                    self._backup_file(file_path)
                self._write_file_safe(path, content)
                self.fixed_files.add(file_path)
                return True

            return False

        except Exception as e:
            print(f"❌ Error fixing trailing whitespace in {file_path}: {e}")
            return False

    def _read_file_safe(self, file_path: Path) -> Optional[str]:
        """Read file with encoding detection"""
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return file_path.read_text(encoding='latin-1')
            except:
                return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None

    def _write_file_safe(self, file_path: Path, content: str):
        """Write file safely"""
        try:
            file_path.write_text(content, encoding='utf-8')
        except:
            file_path.write_text(content, encoding='latin-1')

    def _backup_file(self, file_path: str):
        """Backup a file before modification"""
        if not self.backup:
            return

        try:
            src = Path(file_path)
            rel_path = src.relative_to(self.project_root)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, backup_path)
        except Exception as e:
            print(f"⚠️ Backup failed for {file_path}: {e}")

    def run_black(self) -> bool:
        """Run Black code formatter"""
        try:
            if not RUFF_AVAILABLE:
                print("⚠️ Black not available, skipping...")
                return False

            py_files = list(self.project_root.rglob("*.py"))
            success = True

            for py_file in py_files:
                # Skip excluded directories
                if any(excl in str(py_file) for excl in ['venv', '__pycache__', '.git', '.fix_backup']):
                    continue

                try:
                    if self.backup:
                        self._backup_file(str(py_file))

                    content = self._read_file_safe(py_file)
                    if content is None:
                        continue

                    mode = black.Mode()
                    formatted = black.format_str(content, mode=mode)

                    self._write_file_safe(py_file, formatted)
                    self.fixed_files.add(str(py_file))

                except Exception as e:
                    print(f"⚠️ Black failed for {py_file}: {e}")
                    success = False

            return success

        except Exception as e:
            print(f"❌ Black error: {e}")
            return False

# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
    """Runs tests and generates coverage reports"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.results = {}

    def run_tests(self) -> Dict[str, Any]:
        """Run Django tests"""
        print("🧪 Running Django tests...")

        results = {
            'tests_run': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'details': []
        }

        # Try to run manage.py test
        manage_py = self.project_root / "manage.py"
        if not manage_py.exists():
            print("⚠️ manage.py not found, skipping tests")
            return results

        try:
            # Set Django settings module
            os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

            # Run tests
            result = subprocess.run(
                [sys.executable, str(manage_py), 'test', '--verbosity=2'],
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )

            # Parse output
            output = result.stdout + result.stderr
            results['details'].append(output)

            # Parse results
            for line in output.split('\n'):
                if 'Ran' in line:
                    match = re.search(r'Ran (\d+) tests?', line)
                    if match:
                        results['tests_run'] = int(match.group(1))
                elif 'FAILED' in line:
                    results['failed'] = 1
                elif 'OK' in line:
                    results['passed'] = results['tests_run']

        except Exception as e:
            print(f"❌ Error running tests: {e}")
            results['errors'] = 1

        return results

# ============================================================================
# PROJECT VALIDATOR
# ============================================================================

class ProjectValidator:
    """Validates project structure and settings"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.issues = []

    def validate(self) -> List[Issue]:
        """Validate the entire project"""
        print("✅ Validating project...")

        # Check for required Django files
        required_files = [
            'manage.py',
            'requirements.txt',
            'core/settings.py',
            'core/urls.py',
            'core/wsgi.py'
        ]

        for req_file in required_files:
            if not (self.project_root / req_file).exists():
                self.issues.append(Issue(
                    file_path=req_file,
                    line_number=1,
                    severity='ERROR',
                    category='validation',
                    message=f"Required file missing: {req_file}",
                    auto_fixable=False
                ))

        # Check for apps in INSTALLED_APPS
        settings_py = self.project_root / 'core' / 'settings.py'
        if settings_py.exists():
            try:
                content = settings_py.read_text(encoding='utf-8', errors='ignore')
                if 'INSTALLED_APPS' not in content:
                    self.issues.append(Issue(
                        file_path=str(settings_py),
                        line_number=1,
                        severity='ERROR',
                        category='validation',
                        message="INSTALLED_APPS not found in settings.py",
                        auto_fixable=False
                    ))

                if 'DATABASES' not in content:
                    self.issues.append(Issue(
                        file_path=str(settings_py),
                        line_number=1,
                        severity='ERROR',
                        category='validation',
                        message="DATABASES not found in settings.py",
                        auto_fixable=False
                    ))
            except:
                pass

        return self.issues

# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generates HTML and JSON reports"""

    def __init__(self, report: ProjectReport):
        self.report = report

    def generate_html(self, output_path: str = "fix_report.html"):
        """Generate HTML report"""
        timestamp = self.report.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Django Project Fix Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f2f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #4a90d9; padding-bottom: 15px; margin-bottom: 25px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 25px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card .number {{ font-size: 32px; font-weight: bold; color: #2c3e50; }}
        .summary-card .label {{ font-size: 14px; color: #7f8c8d; margin-top: 5px; }}
        .summary-card.critical .number {{ color: #e74c3c; }}
        .summary-card.warning .number {{ color: #f39c12; }}
        .summary-card.info .number {{ color: #3498db; }}
        .summary-card.success .number {{ color: #2ecc71; }}
        .issue-list {{ margin: 20px 0; }}
        .issue-item {{
            border-left: 4px solid #3498db;
            padding: 10px 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .issue-item.ERROR {{ border-color: #e74c3c; background: #fdf0ee; }}
        .issue-item.CRITICAL {{ border-color: #e74c3c; background: #fdf0ee; }}
        .issue-item.WARNING {{ border-color: #f39c12; background: #fef9e7; }}
        .issue-item.INFO {{ border-color: #3498db; background: #ebf5fb; }}
        .issue-item.SUGGESTION {{ border-color: #2ecc71; background: #eafaf1; }}
        .issue-item .file {{ font-weight: bold; color: #2c3e50; }}
        .issue-item .message {{ margin: 5px 0; }}
        .issue-item .fix {{ color: #27ae60; font-size: 12px; }}
        .severity-badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}
        .severity-badge.ERROR {{ background: #e74c3c; color: white; }}
        .severity-badge.CRITICAL {{ background: #e74c3c; color: white; }}
        .severity-badge.WARNING {{ background: #f39c12; color: white; }}
        .severity-badge.INFO {{ background: #3498db; color: white; }}
        .severity-badge.SUGGESTION {{ background: #2ecc71; color: white; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; text-align: center; color: #95a5a6; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Django Project Fix Report</h1>
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Project Root:</strong> {self.report.total_files} files analyzed</p>

        <div class="summary">
            <div class="summary-card success">
                <div class="number">{self.report.total_files}</div>
                <div class="label">Total Files</div>
            </div>
            <div class="summary-card critical">
                <div class="number">{self.report.critical_issues}</div>
                <div class="label">Critical Issues</div>
            </div>
            <div class="summary-card warning">
                <div class="number">{self.report.warnings}</div>
                <div class="label">Warnings</div>
            </div>
            <div class="summary-card info">
                <div class="number">{self.report.info + self.report.suggestions}</div>
                <div class="label">Info & Suggestions</div>
            </div>
            <div class="summary-card success">
                <div class="number">{self.report.auto_fixes_applied}</div>
                <div class="label">Auto-fixes Applied</div>
            </div>
        </div>

        <h2>📋 Issues by Category</h2>
        <ul>
"""

        for category, count in self.report.issues_by_category.items():
            html += f"<li><strong>{category}:</strong> {count}</li>"

        html += """
        </ul>

        <h2>⚠️ Issues Found</h2>
        <div class="issue-list">
"""

        if self.report.total_issues == 0:
            html += '<p style="color: green; font-size: 18px;">🎉 No issues found! Your project is clean!</p>'
        else:
            for issue in self.report.issues[:100]:  # Limit to 100 for display
                html += f"""
            <div class="issue-item {issue.severity}">
                <span class="severity-badge {issue.severity}">{issue.severity}</span>
                <span class="file">{issue.file_path}</span>
                <span style="color: #7f8c8d;">line {issue.line_number}</span>
                <div class="message">{issue.message}</div>
                <div class="fix">Category: {issue.category}</div>
"""
                if issue.suggestion:
                    html += f'<div class="fix">💡 {issue.suggestion}</div>'
                if issue.auto_fixable:
                    html += '<div class="fix">✅ Auto-fixable</div>'
                html += """
            </div>
"""

        html += """
        </div>

        <div class="footer">
            <p>Django Discipline Management System - Automated Fix Report</p>
            <p>Powered by Python AST & AI Analysis</p>
        </div>
    </div>
</body>
</html>
"""

        Path(output_path).write_text(html, encoding='utf-8')
        print(f"📄 HTML report saved to {output_path}")

    def generate_json(self, output_path: str = "fix_report.json"):
        """Generate JSON report"""

        report_dict = {
            'timestamp': self.report.timestamp.isoformat(),
            'total_files': self.report.total_files,
            'analyzed_files': self.report.analyzed_files,
            'total_issues': self.report.total_issues,
            'critical_issues': self.report.critical_issues,
            'warnings': self.report.warnings,
            'info': self.report.info,
            'suggestions': self.report.suggestions,
            'auto_fixes_applied': self.report.auto_fixes_applied,
            'manual_fixes_needed': self.report.manual_fixes_needed,
            'issues_by_category': dict(self.report.issues_by_category),
            'issues_by_severity': dict(self.report.issues_by_severity),
            'issues': [
                {
                    'file': i.file_path,
                    'line': i.line_number,
                    'severity': i.severity,
                    'category': i.category,
                    'message': i.message,
                    'auto_fixable': i.auto_fixable,
                    'suggestion': i.suggestion
                }
                for i in self.report.issues[:500]
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        print(f"📄 JSON report saved to {output_path}")

# ============================================================================
# MAIN FIX SCRIPT
# ============================================================================

class DjangoProjectFixer:
    """Main class that orchestrates the entire fix process"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.scanner = ProjectScanner(str(self.project_root))
        self.fixer = ProjectFixer(str(self.project_root))
        self.validator = ProjectValidator(str(self.project_root))
        self.report = None
        self.test_results = None

    def run(self, fix_auto: bool = True, run_tests: bool = True):
        """Run the complete fix workflow"""
        print("\n" + "="*70)
        print("  🚀 DJANGO PROJECT FIXER")
        print("  Discipline Management System - Automated Debug & Fix")
        print("="*70 + "\n")

        # Step 1: Scan the project
        print("📂 STEP 1: Scanning Project...")
        self.report = self.scanner.scan()

        # Step 2: Validate project structure
        print("\n✅ STEP 2: Validating Project...")
        validation_issues = self.validator.validate()
        self.report.issues.extend(validation_issues)
        self.report.total_issues = len(self.report.issues)

        # Step 3: Apply automatic fixes
        if fix_auto:
            print("\n🔧 STEP 3: Applying Automatic Fixes...")
            self._apply_fixes()

        # Step 4: Run tests
        if run_tests:
            print("\n🧪 STEP 4: Running Tests...")
            test_runner = TestRunner(str(self.project_root))
            self.test_results = test_runner.run_tests()
            self.report.test_results = self.test_results

        # Step 5: Generate report
        print("\n📄 STEP 5: Generating Report...")
        self._generate_report()

        # Step 6: Summary
        self._print_summary()

        return self.report

    def _apply_fixes(self):
        """Apply automatic fixes to the project"""
        fixes_applied = 0

        print("  📦 Fixing imports...")
        for file_path, file_info in self.scanner.files.items():
            if self.fixer.fix_imports(file_path):
                fixes_applied += 1

        print("  ✨ Fixing trailing whitespace...")
        for file_path in self.scanner.files.keys():
            if self.fixer.fix_trailing_whitespace(file_path):
                fixes_applied += 1

        print("  ⚫ Running Black formatter...")
        if self.fixer.run_black():
            fixes_applied += 1

        self.report.auto_fixes_applied = fixes_applied
        print(f"\n✅ Applied {fixes_applied} fixes")

    def _generate_report(self):
        """Generate HTML and JSON reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        html_path = f"fix_report_{timestamp}.html"
        json_path = f"fix_report_{timestamp}.json"

        generator = ReportGenerator(self.report)
        generator.generate_html(html_path)
        generator.generate_json(json_path)

        print(f"\n📄 Reports saved:")
        print(f"   HTML: {html_path}")
        print(f"   JSON: {json_path}")

    def _print_summary(self):
        """Print summary of the fix process"""
        print("\n" + "="*70)
        print("  📊 SUMMARY")
        print("="*70)

        print(f"  📁 Files Analyzed: {self.report.analyzed_files}")
        print(f"  🐛 Total Issues Found: {self.report.total_issues}")
        print(f"  🔥 Critical Issues: {self.report.critical_issues}")
        print(f"  ⚠️  Warnings: {self.report.warnings}")
        print(f"  ℹ️  Info: {self.report.info}")
        print(f"  💡 Suggestions: {self.report.suggestions}")
        print(f"  ✅ Auto-fixes Applied: {self.report.auto_fixes_applied}")

        if self.test_results:
            print(f"\n  🧪 Test Results:")
            print(f"     Run: {self.test_results.get('tests_run', 0)}")
            print(f"     Passed: {self.test_results.get('passed', 0)}")
            print(f"     Failed: {self.test_results.get('failed', 0)}")

        print("\n" + "="*70)

        if self.report.total_issues == 0:
            print("🎉 No issues found! Your project is clean!")
        else:
            print("📋 Open the HTML report for detailed information")
            print("💡 Some issues may require manual fixes")

        print("="*70 + "\n")

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point for the script"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Django Discipline Management System - Complete Debug & Fix Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full fix on current directory
  python fix_project.py

  # Run fix on specific directory
  python fix_project.py --path /path/to/project

  # Skip automatic fixes (only scan and report)
  python fix_project.py --no-fix

  # Skip tests
  python fix_project.py --no-tests

  # Generate report only
  python fix_project.py --report-only

  # With verbose output
  python fix_project.py --verbose
        """
    )

    parser.add_argument(
        '--path',
        default='.',
        help='Path to Django project root (default: current directory)'
    )

    parser.add_argument(
        '--no-fix',
        action='store_true',
        help='Skip automatic fixes (only scan and report)'
    )

    parser.add_argument(
        '--no-tests',
        action='store_true',
        help='Skip running tests'
    )

    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Only generate report from existing scan'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Install chardet if not available
    try:
    except ImportError:
        print("📦 Installing chardet for encoding detection...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"])

    # Run the fixer
    try:
        fixer = DjangoProjectFixer(args.path)
        fixer.run(
            fix_auto=not args.no_fix,
            run_tests=not args.no_tests
        )
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
