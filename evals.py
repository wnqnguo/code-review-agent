import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Test cases — known bad code with expected issues
TEST_CASES = [
    {
        "name": "SQL Injection",
        "code": "def get_user(id):\n    return db.query('SELECT * FROM users WHERE id=' + id)",
        "must_catch": ["sql injection", "parameterized", "injection"],
    },
    {
        "name": "Hardcoded Password",
        "code": 'password = "supersecret123"',
        "must_catch": ["password", "secret", "environment variable", "hardcoded"],
    },
    {
        "name": "Division By Zero",
        "code": "def calculate(x, y):\n    return x / y",
        "must_catch": ["division", "zero", "zerodivision", "validate"],
    },
    {
        "name": "Resource Leak",
        "code": "def read_file(filename):\n    f = open(filename)\n    return f.read()",
        "must_catch": ["close", "context manager", "with open"],
    },
]

def run_review(code):
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="You are a senior software engineer doing code review. Be specific, concise, and actionable.",
        messages=[
            {"role": "user", "content": f"Review this code:\n{code}"}
        ]
    )
    return response.content[0].text

def run_evals():
    print("Running evals...\n")
    passed = 0
    failed = 0

    for test in TEST_CASES:
        print(f"Testing: {test['name']}")
        review = run_review(test["code"]).lower()

        # Check if any of the expected terms appear in the review
        caught = any(term in review for term in test["must_catch"])

        if caught:
            print(f"  ✅ PASSED — issue was caught\n")
            passed += 1
        else:
            print(f"  ❌ FAILED — review missed the issue")
            print(f"  Expected one of: {test['must_catch']}\n")
            failed += 1

    print(f"Results: {passed}/{passed + failed} passed")
    if failed == 0:
        print("🎉 All evals passed!")
    else:
        print("⚠️  Some issues were missed — consider improving your system prompt")

if __name__ == "__main__":
    run_evals()