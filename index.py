import os

print("hello world")

pr_description = os.getenv("PR_DESCRIPTION", "didnt get that one")

print(pr_description)