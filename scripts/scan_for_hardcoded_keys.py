#!/usr/bin/env python3
"""Simple scanner for hardcoded API keys and private keys.

Usage: pre-commit will call this with a list of staged filenames.
If no filenames are provided the script will scan the repository files.
"""
import sys
import re
import os

KEY_PATTERN = re.compile(
    r"\b(?:sk_live_|sk_test_|sk-|api[_-]?key|secret[_-]?key|OPENAI_API_KEY|OPENROUTER_API_KEY|POLLINATION_API_KEY|aws_secret_access_key|AKIA[0-9A-Z]{16}|ghp_[0-9A-Za-z_]{36}|ya29\.)",
    re.IGNORECASE,
)

PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----")

TEXT_EXTS = (".py", ".env", ".sh", ".yaml", ".yml", ".json", ".txt", ".cfg", ".ini")


def scan_file(path):
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for n, line in enumerate(fh, start=1):
                if KEY_PATTERN.search(line) or PRIVATE_KEY_PATTERN.search(line):
                    findings.append((n, line.rstrip()))
    except Exception:
        # skip binary or unreadable files silently
        return []
    return findings


def iter_files(paths=None):
    if paths:
        for p in paths:
            if os.path.isdir(p):
                for root, _, files in os.walk(p):
                    for f in files:
                        fp = os.path.join(root, f)
                        if fp.endswith(TEXT_EXTS):
                            yield fp
            else:
                if p.endswith(TEXT_EXTS):
                    yield p
    else:
        for root, _, files in os.walk('.'):
            for f in files:
                fp = os.path.join(root, f)
                if fp.startswith('./.git'):
                    continue
                if fp.endswith(TEXT_EXTS):
                    yield fp


def main(argv):
    paths = argv[1:]
    bad = False
    scanned = set()
    for path in iter_files(paths or None):
        if path in scanned:
            continue
        scanned.add(path)
        findings = scan_file(path)
        if findings:
            bad = True
            print(f"[POTENTIAL SECRET] {path}")
            for lineno, snippet in findings:
                print(f"  L{lineno}: {snippet}")
            print("")

    if bad:
        print("\nHardcoded secrets detected. Aborting commit. Review and remove secrets or add them to env vars.")
        return 1

    print("No obvious hardcoded secrets found.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
