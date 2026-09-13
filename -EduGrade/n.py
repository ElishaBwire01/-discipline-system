#!/usr/bin/env python3

"""
EduGrade Python Dependency Scanner

Scans the project for Python imports and checks which external
Python libraries are installed in the active virtual environment.
"""

import ast
import importlib.util
import os
import sys
from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

EXCLUDED_DIRS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    "staticfiles",
    "media",
}


# ============================================================
# COMMON IMPORT NAME -> PIP PACKAGE NAME
# ============================================================

PIP_PACKAGE_MAP = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "rest_framework": "djangorestframework",
    "django_filters": "django-filter",
    "dotenv": "python-dotenv",
    "decouple": "python-decouple",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "jwt": "PyJWT",
    "Crypto": "pycryptodome",
    "MySQLdb": "mysqlclient",
    "psycopg2": "psycopg2-binary",
    "reportlab": "reportlab",
    "openpyxl": "openpyxl",
    "pandas": "pandas",
    "numpy": "numpy",
    "requests": "requests",
}


# ============================================================
# PYTHON STANDARD LIBRARY
# ============================================================

try:
    STANDARD_LIBRARY = set(sys.stdlib_module_names)
except AttributeError:
    STANDARD_LIBRARY = set()


# ============================================================
# FIND PYTHON FILES
# ============================================================

def find_python_files():
    """Find all Python files inside the project."""

    python_files = []

    for root, dirs, files in os.walk(PROJECT_ROOT):

        # Do not scan excluded directories
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in EXCLUDED_DIRS
        ]

        for filename in files:

            if filename.endswith(".py"):

                python_files.append(
                    Path(root) / filename
                )

    return python_files


# ============================================================
# EXTRACT IMPORTS
# ============================================================

def extract_imports(file_path):
    """Extract imported top-level Python modules."""

    imports = set()

    try:

        source = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(source)

    except SyntaxError as error:

        print(
            f"⚠️ Syntax error in {file_path}: "
            f"line {error.lineno}"
        )

        return imports

    except Exception as error:

        print(
            f"⚠️ Could not read {file_path}: {error}"
        )

        return imports

    for node in ast.walk(tree):

        # Example:
        #
        # import django
        # import requests
        #
        if isinstance(node, ast.Import):

            for alias in node.names:

                module = alias.name.split(".")[0]

                imports.add(module)

        # Example:
        #
        # from django.conf import settings
        #
        elif isinstance(node, ast.ImportFrom):

            if node.module:

                module = node.module.split(".")[0]

                imports.add(module)

    return imports


# ============================================================
# CHECK WHETHER MODULE IS INSTALLED
# ============================================================

def is_installed(module_name):
    """Check whether a Python module can be imported."""

    try:

        return importlib.util.find_spec(
            module_name
        ) is not None

    except (ModuleNotFoundError, ValueError):

        return False


# ============================================================
# GET PIP PACKAGE NAME
# ============================================================

def get_pip_package(module_name):
    """Convert an import name into its pip package name."""

    return PIP_PACKAGE_MAP.get(
        module_name,
        module_name
    )


# ============================================================
# MAIN SCANNER
# ============================================================

def main():

    print()
    print("=" * 70)
    print("        EduGrade Python Dependency Scanner")
    print("=" * 70)

    print()
    print(f"Project : {PROJECT_ROOT}")
    print(f"Python  : {sys.executable}")
    print(
        f"Version : {sys.version.split()[0]}"
    )

    print()
    print("Scanning Python files...")
    print()

    # --------------------------------------------------------
    # Find Python files
    # --------------------------------------------------------

    python_files = find_python_files()

    print(
        f"Python files found: {len(python_files)}"
    )

    # --------------------------------------------------------
    # Collect imports
    # --------------------------------------------------------

    all_imports = set()

    for file_path in python_files:

        imports = extract_imports(
            file_path
        )

        all_imports.update(imports)

    # --------------------------------------------------------
    # Remove standard-library modules
    # --------------------------------------------------------

    external_modules = {
        module
        for module in all_imports
        if module not in STANDARD_LIBRARY
    }

    # --------------------------------------------------------
    # Check installed/missing
    # --------------------------------------------------------

    installed = []
    missing = []

    for module in sorted(external_modules):

        if is_installed(module):

            installed.append(module)

        else:

            missing.append(module)

    # ========================================================
    # INSTALLED
    # ========================================================

    print()
    print("=" * 70)
    print("INSTALLED EXTERNAL LIBRARIES")
    print("=" * 70)

    if installed:

        for module in installed:

            package = get_pip_package(module)

            if package != module:

                print(
                    f"  ✅ {module:<25} "
                    f"(pip: {package})"
                )

            else:

                print(
                    f"  ✅ {module}"
                )

    else:

        print("  None found.")

    # ========================================================
    # MISSING
    # ========================================================

    print()
    print("=" * 70)
    print("MISSING LIBRARIES")
    print("=" * 70)

    if missing:

        for module in missing:

            package = get_pip_package(module)

            print(
                f"  ❌ {module:<25} "
                f"(pip: {package})"
            )

    else:

        print(
            "  🎉 No missing external libraries detected!"
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Python files scanned : {len(python_files)}"
    )

    print(
        f"External libraries   : "
        f"{len(external_modules)}"
    )

    print(
        f"Installed            : "
        f"{len(installed)}"
    )

    print(
        f"Missing              : "
        f"{len(missing)}"
    )

    # ========================================================
    # INSTALL COMMAND
    # ========================================================

    if missing:

        print()
        print("=" * 70)
        print("INSTALL MISSING LIBRARIES")
        print("=" * 70)

        packages = [
            get_pip_package(module)
            for module in missing
        ]

        print()
        print("Install individually:")
        print()

        for package in packages:

            print(
                f"pip install {package}"
            )

        print()
        print("OR install everything at once:")
        print()

        print(
            "pip install "
            + " ".join(packages)
        )

    # ========================================================
    # REQUIREMENTS CHECK
    # ========================================================

    requirements_file = (
        PROJECT_ROOT / "requirements.txt"
    )

    print()
    print("=" * 70)
    print("REQUIREMENTS.TXT")
    print("=" * 70)

    if requirements_file.exists():

        print(
            "  ✅ requirements.txt found"
        )

    else:

        print(
            "  ⚠️ requirements.txt not found"
        )

    print()
    print("=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
