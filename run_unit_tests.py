import os
import sys
import subprocess
import re
import webbrowser
from html import escape

LOGS_DIR = os.path.join("tests", "logs")
LOG_FILE = os.path.join(LOGS_DIR, "test_report.log")
HTML_FILE = os.path.join(LOGS_DIR, "test_report.html")

TEST_ALIASES = {
    "tdb": "tests/test_database.py",
    "tmo": "tests/test_models.py",
    "tcr": "tests/test_crud.py",
    "tma": "tests/test_main.py",
    "tsc": "tests/test_schemas.py"
}

os.makedirs(LOGS_DIR, exist_ok=True)

def resolve_test_files(args):
    if not args:
        print("No parameters provided. Running all tests in the 'tests' folder...")
        return ["tests"]
    resolved = []
    for arg in args:
        if arg in TEST_ALIASES:
            resolved.append(TEST_ALIASES[arg])
        elif os.path.exists(arg):
            resolved.append(arg)
        else:
            print(f"Error: Unknown alias or file '{arg}'")
            sys.exit(1)
    return resolved

def run_pytest(test_files):
    return subprocess.run(
        ["pytest", "-v"] + test_files,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def extract_summary(output):
    match = re.search(r"(?:(\d+) failed.*?,\s*)?(?:(\d+) passed).*?in (\d+\.\d+)s", output)
    if match:
        failed = int(match.group(1)) if match.group(1) else 0
        passed = int(match.group(2)) if match.group(2) else 0
        duration = float(match.group(3))
        return passed, failed, duration
    return 0, 0, 0.0

def write_logs(output):
    session_start = ""
    full_summary = []
    domain_sections = {}
    failures = []
    short_summary = ""
    final_summary_line = ""

    capture_full_summary = False
    in_failures = False

    for line in output.splitlines():
        if not session_start and "test session starts" in line:
            session_start = line
        elif line.startswith("platform "):
            full_summary.append(line)
            capture_full_summary = True
        elif capture_full_summary and (
            line.startswith("cachedir") or 
            line.startswith("rootdir") or 
            "plugins:" in line or 
            line.strip().startswith("configfile:")
        ):
            full_summary.append(line)
        elif "::" in line and ("PASSED" in line or "FAILED" in line):
            match = re.match(r"(tests[\\/](test_\w+)\.py)::(\w+)", line)
            if match:
                domain = match.group(2).replace("test_", "").upper()
                domain_sections.setdefault(domain, []).append(line)
        elif line.startswith("short test summary info"):
            short_summary = line
        elif "FAILURES" in line:
            in_failures = True
            failures.append(line)
        elif in_failures:
            failures.append(line)
        elif re.search(r"=+.*?(?:\d+ failed.*?)?(?:\d+ passed).*?in \d+\.\d+s.*?=+", line):
            final_summary_line = line

    passed, failed, duration = extract_summary(output)

    # Write .log file
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(session_start + "\n\n")

        f.write("======== FULL SUMMARY ========\n")
        for line in full_summary:
            f.write(line + "\n")
        f.write("\n")

        for domain, lines in domain_sections.items():
            f.write(f"======== TEST {domain} ========\n")
            f.write("=" * 80 + "\n")
            for l in lines:
                f.write(l + "\n")
            f.write("=" * 80 + "\n")
            f.write(f"======== END OF TEST {domain} ========\n\n")

        if short_summary:
            f.write("======== short test summary info ========\n")
            f.write(short_summary + "\n\n")

        if final_summary_line:
            f.write(final_summary_line + "\n\n")

        if failures:
            f.write("======== FAILURES ========\n")
            f.write("\n".join(failures) + "\n\n")

        f.write("======== TEST SUMMARY ========\n")
        f.write(f"Total tests: {passed + failed}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Execution time: {duration:.2f} seconds\n")
        f.write("=" * 28 + "\n\n")

    # Write HTML version
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'>\n")
        f.write("<style>body { font-family: monospace; background: #121212; color: #eee; padding: 1em; }")
        f.write(".section { margin-top: 2em; }")
        f.write(".domain { color: #9cdcfe; font-weight: bold; }")
        f.write(".fail { color: #f44747; }")
        f.write(".pass { color: #89ca78; }")
        f.write("</style></head><body>\n")

        f.write(f"<h2>UNIT TESTS</h2><p><b>{escape(session_start)}</b></p>")

        f.write("<div class='section'><h3>Tests Setup</h3><pre>\n")
        f.write(escape("\n".join(full_summary)) + "</pre></div>")

        for domain, lines in domain_sections.items():
            f.write(f"<div class='section'><h3 class='domain'>TEST {domain}</h3><pre>\n")
            for l in lines:
                color = "pass" if "PASSED" in l else "fail"
                f.write(f"<span class='{color}'>{escape(l)}</span>\n")
            f.write("</pre></div>")

        if short_summary:
            f.write("<div class='section'><h3>Short Test Summary</h3><pre>\n")
            f.write(escape(short_summary) + "</pre></div>")

        if final_summary_line:
            f.write(escape(final_summary_line) + "</pre></div>")

        if failures:
            f.write("<div class='section'><h3 class='fail'>FAILURES</h3><pre>\n")
            f.write(escape("\n".join(failures)) + "</pre></div>")

        f.write("<div class='section'><h3>SUMMARY</h3><pre>\n")
        f.write(f"Total tests: {passed + failed}\n")
        f.write(f"<em class='pass'>Passed: {passed}\n</em>")
        f.write(f"<em class='fail'>Failed: {failed}\n</em>")
        f.write(f"Execution time: {duration:.2f} seconds\n")
        f.write("</pre></div>")
        f.write("</body></html>")

         # Remove the .log file after creating the HTML
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

def main():
    test_files = resolve_test_files(sys.argv[1:])
    result = run_pytest(test_files)
    write_logs(result.stdout)
    print(f"Tests finished.\n- HTML report saved to: {HTML_FILE}")
    webbrowser.open(f"file://{os.path.abspath(HTML_FILE)}")

if __name__ == "__main__":
    main()
