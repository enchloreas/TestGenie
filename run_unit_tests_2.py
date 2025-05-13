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
    """
    Resolve test files or aliases from the provided arguments.
    """
    # Remove the '--test' flag if present
    args = [arg for arg in args if arg != "--test"]

    if not args:
        print("No parameters provided. Running all tests in the 'tests' folder...")
        return ["tests"]  # Default to running all tests

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

def run_pytest(test_files, is_test_mode):
    """
    Run pytest with the specified test files and flags.
    """
    if not test_files:
        print("No test files resolved. Exiting...")
        sys.exit(1)

    pytest_args = ["-s", "-v"] + test_files  # Add the '-s' flag to disable output capturing
    if is_test_mode:
        pytest_args.append("--test")  # Pass the '--test' flag to pytest

    print(f"Running pytest with arguments: {pytest_args}")  # Debugging: Print pytest arguments

    result = subprocess.run(
        ["pytest"] + pytest_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Print pytest output to the console
    print(result.stdout)  # Output pytest stdout to the console
    if result.stderr:
        print(result.stderr)  # Output pytest stderr to the console (if any)

    return result

def extract_summary(output):
    match = re.search(r"(?:(\d+) failed.*?,\s*)?(?:(\d+) passed).*?in (\d+\.\d+)s", output)
    if match:
        failed = int(match.group(1)) if match.group(1) else 0
        passed = int(match.group(2)) if match.group(2) else 0
        duration = float(match.group(3))
        return passed, failed, duration
    return 0, 0, 0.0

def write_logs(output):
    print("Raw pytest output:")
    print(output)

    if not output.strip():
        print("No output from pytest. Exiting...")
        return

    session_start = ""
    full_summary = []
    detailed_results = []
    domain_sections = {}
    failures = []
    short_summary = ""
    final_summary_line = ""

    capture_full_summary = False
    in_failures = False

    for line in output.splitlines():
        print(f"Processing line: {line}")  # Debugging
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
        elif re.search(r"tests[\\/].*::[a-zA-Z_][a-zA-Z0-9_]*.*\s+(PASSED|FAILED)", line):
            print(f"Matched detailed result line: {line}")  # Debugging
            detailed_results.append(line)
            match = re.match(r"(tests[\\/](test_\w+)\.py)::(\w+)", line)
            if match:
                domain = match.group(2).replace("test_", "").upper()
                domain_sections.setdefault(domain, []).append(line)
        else:
            print(f"Line did not match: {line} (length: {len(line)})")  # Debugging

    print("Captured detailed results:")
    for line in detailed_results:
        print(line)

    # Extract summary values
    passed, failed, duration = extract_summary(output)

    # Write .log file
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(session_start + "\n\n")

        f.write("======== FULL SUMMARY ========\n")
        for line in full_summary:
            f.write(line + "\n")
        f.write("\n")

        f.write("======== DETAILED RESULTS ========\n")
        for line in detailed_results:
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

        f.write("<div class='section'><h3>TEST DATABASE</h3><pre>\n")
        for line in detailed_results:
            color = "pass" if "PASSED" in line else "fail"
            print(f"Writing line to HTML: {line}")  # Debugging
            f.write(f"<span class='{color}'>{escape(line)}</span>\n")
        f.write("</pre></div>")

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
    # Check if the '--test' flag is present
    is_test_mode = "--test" in sys.argv

    # Remove the '--test' flag from sys.argv to avoid passing it to pytest
    if is_test_mode:
        sys.argv.remove("--test")

    # Resolve test files
    test_files = resolve_test_files(sys.argv[1:])

    # Run pytest
    result = run_pytest(test_files, is_test_mode)

    # Write logs and generate the report
    write_logs(result.stdout)

    # Print and open the report
    print(f"Tests finished.\n- HTML report saved to: {HTML_FILE}")
    
    webbrowser.open(f"file://{os.path.abspath(HTML_FILE)}")
    
if __name__ == "__main__":
    main()