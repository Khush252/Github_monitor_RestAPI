import base64
import re
import requests

# Removed get_file_content_at_commit as it is not used


def count_tests_in_diff(diff):
    added_tests = 0
    subtracted_tests = 0

    test_pattern = re.compile(r"^\+.*\btest\s*\(", re.MULTILINE)
    subtract_pattern = re.compile(r"^\-.*\btest\s*\(", re.MULTILINE)

    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added_tests += len(test_pattern.findall(line))
        elif line.startswith("-") and not line.startswith("---"):
            subtracted_tests += len(subtract_pattern.findall(line))

    return added_tests - subtracted_tests
