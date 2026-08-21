"""Test the intent parser logic directly without needing Django running."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")

# Only test the intent parsing — no DB needed
import re

def _parse_user_intent(message):
    message_lower = message.lower()
    intent = {"type": "general", "entities": {}, "action": None}

    school_keywords = [
        "school name", "name of this school", "name of the school",
        "school motto", "school address", "what school", "which school",
    ]
    if any(kw in message_lower for kw in school_keywords):
        intent["type"] = "stats"
        return intent

    student_patterns = [
        r"student\s+(\w+)",
        r"admission\s*[#:]*\s*(\d+)",
        r"pupil\s+(\w+)",
        r"learner\s+(\w+)",
        r"about\s+(\w+)",
    ]
    for pattern in student_patterns:
        match = re.search(pattern, message_lower)
        if match:
            intent["type"] = "student"
            intent["entities"]["query"] = match.group(1)
            break

    admission_match = re.search(r"\b(\d{4,6})\b", message)
    if admission_match:
        intent["type"] = "student"
        intent["entities"]["admission"] = admission_match.group(1)

    if any(word in message_lower for word in ["how many", "total", "count", "statistics", "stats"]):
        intent["type"] = "stats"

    student_list_phrases = [
        "list students", "list all students", "show students",
        "what are their names", "names of students", "students names",
        "list names", "all students",
    ]
    if any(phrase in message_lower for phrase in student_list_phrases):
        intent["type"] = "student_names"

    stream_match = re.search(r"stream\s+(\w+)", message_lower)
    if stream_match:
        intent["type"] = "stream"
        intent["entities"]["stream"] = stream_match.group(1)

    if any(word in message_lower for word in ["report", "case", "offense", "incident"]):
        intent["action"] = "reports"

    return intent

TESTS = [
    # (message, expected_type)
    ("what is the name of this school",           "stats"),
    ("what is the school name",                   "stats"),
    ("what is the school motto",                  "stats"),  # wait - "motto" not in school_keywords...
    ("how many students are in this school",      "stats"),
    ("how many students",                         "stats"),
    ("total students",                            "stats"),
    ("list all students",                         "student_names"),
    ("show students",                             "student_names"),
    ("what are their names",                      "student_names"),
    ("tell me about student john",                "student"),
    ("show me student mary",                      "student"),
    ("who is the top risk student",               "general"),
    ("give me school statistics",                 "stats"),
    ("i their",                                   "general"),   # the garbage message from the screenshot
    ("what is 2 + 2",                             "general"),
]

print("\nIntent parser tests:")
print("=" * 65)
all_ok = True
for msg, expected in TESTS:
    result = _parse_user_intent(msg)
    got    = result["type"]
    ok     = "OK " if got == expected else "FAIL"
    if got != expected:
        all_ok = False
    print(f"  [{ok}] '{msg[:45]:<45}'  => {got}  (expected {expected})")

print("=" * 65)
print(f"\n{'ALL TESTS PASSED' if all_ok else 'SOME TESTS FAILED'}\n")
