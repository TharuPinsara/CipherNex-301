#!/usr/bin/env python3
"""
CipherNex-301 // Member 4: Integration, Testing & Documentation
Script: run_test_suite.py
Purpose: Master execution script that runs all integration, security, and recovery
         test modules and compiles the official test_results.log evidence file.
"""

import os
import sys
import datetime
import subprocess

# Dynamically resolve root project directory (CipherNex-301)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Resolve targets dynamically (checks both solutions/ and tests/ folders)
def find_script(rel_subpath):
    primary = os.path.join(PROJECT_ROOT, rel_subpath)
    if os.path.exists(primary):
        return primary
    # Fallback if placed inside tests/
    filename = os.path.basename(rel_subpath)
    fallback = os.path.join(PROJECT_ROOT, "tests", filename)
    return fallback if os.path.exists(fallback) else primary

TEST_SCRIPTS = [
    (find_script("solutions/test_integration.py"), "End-to-End Progression & API Verification"),
    (find_script("tests/test_unintended_solutions.py"), "Anti-Bypass & Security Hardening Verification"),
    (find_script("tests/test_reset_recovery.py"), "Platform Reset & Sandbox Recovery Verification")
]

LOG_OUTPUT = os.path.join(PROJECT_ROOT, "tests", "test_results.log")

def main():
    os.makedirs(os.path.join(PROJECT_ROOT, "tests"), exist_ok=True)
    separator = "=" * 70
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    with open(LOG_OUTPUT, "w", encoding="utf-8") as log_file:
        header = (
            f"{separator}\n"
            f"CIPHERNEX-301 CTF PLAY BOX // AUTOMATED TESTING AUDIT REPORT\n"
            f"Execution Timestamp: {timestamp}\n"
            f"Auditor: Member 4 (Integration, Testing & Documentation)\n"
            f"{separator}\n"
        )
        print(header, end="")
        log_file.write(header)

        all_passed = True

        for script_path, description in TEST_SCRIPTS:
            script_name = os.path.basename(script_path)
            print(f"\n[*] Running: {description} ({script_name})...")
            log_file.write(f"\n--- EXECUTING: {description} ({script_name}) ---\n")

            if not os.path.exists(script_path):
                err_msg = f"[ERROR] Target script file does not exist: {script_path}\n"
                print(f"\033[91m{err_msg}\033[0m")
                log_file.write(err_msg)
                all_passed = False
                continue

            # Execute with cwd set to PROJECT_ROOT so relative asset paths resolve correctly
            res = subprocess.run(
                [sys.executable, script_path],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            if res.stdout:
                print(res.stdout, end="")
                log_file.write(res.stdout)

            if res.stderr:
                print(res.stderr, end="")
                log_file.write("\nSTDERR:\n" + res.stderr)

            if res.returncode != 0:
                all_passed = False
                log_file.write(f"\n[FAIL] Test module {script_name} exited with error code {res.returncode}\n")
            else:
                log_file.write(f"\n[SUCCESS] Test module {script_name} completed cleanly.\n")

        summary = (
            f"\n{separator}\n"
            f"FINAL AUDIT RESULT: {'ALL MODULES PASSED (0 DEFECTS)' if all_passed else 'FAILURES DETECTED'}\n"
            f"{separator}\n"
        )
        print(summary, end="")
        log_file.write(summary)

    print(f"\n[+] Test execution log saved to: {LOG_OUTPUT}")

if __name__ == "__main__":
    main()