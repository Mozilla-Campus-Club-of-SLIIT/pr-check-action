import os

print("hello world")

pr_description = os.getenv("PR_DESCRIPTION", "")

print(pr_description)