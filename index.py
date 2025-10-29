import os
import re
import sys

pr_description = os.getenv("PR_DESCRIPTION", "")
check_closing = os.getenv("CHECK_CLOSING_STATEMENT", "false") == "true"
check_boxes = os.getenv("CHECK_UNCHECKED_BOXES", "false") == "true"
require_nondefault_branch = os.getenv("REQUIRE_NONDEFAULT_BRANCH", "") == "true"
no_closing_message = os.getenv("NO_CLOSING_MESSAGE", "").strip()
unchecked_boxes_message = os.getenv("UNCHECKED_BOXES_MESSAGE", "").strip()
unchecked_box_group_message = os.getenv("UNCHECKED_BOX_GROUP_MESSAGE", "").strip()
branch_error_message = os.getenv("BRANCH_ERROR_MESSAGE", "").strip()
success_message = os.getenv("SUCCESS_MESSAGE", "").strip()
default_branch_name = os.getenv("DEFAULT_BRANCH", "").strip()
pr_branch_name = os.getenv("PR_BRANCH", "").strip()

print(default_branch_name, pr_branch_name, require_nondefault_branch)

default_no_closing_message = (
    "### ❌ Missing Closing Terms\n"
    "This PR does not reference an issue with `closes`, `fixes`, or `resolves` keywords.\n"
    "Please update the PR description to automatically close the relevant issue when merged.\n"
)

default_unchecked_boxes_message = (
    "### ❌ Unchecked Checkboxes\n"
    "Some required checklist items in the PR description are not checked. "
    "Make sure all mandatory tasks are completed:\n"
)

default_branch_error_message = (
    "### ❌ PR not allowed from default branch\n\n"
    "This pull request originates from the repository default branch '{head}' and targets '{base}', which is not allowed.\n\n"
    "Action required: create a new branch from the default branch, push your changes to that branch, and open (or update) the PR from the new branch.\n"
)

default_unchecked_box_group_message = "- **{group}**: {unchecked} out of {all} checkboxes are unchecked\n"
default_success_message = "✅ All checks passed"

def has_closing_terms(description: str):
    match = re.search(
        r"(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved):?\s#\d+",
        description,
        flags=re.MULTILINE | re.IGNORECASE
    )

    return match is not None

def get_checkbox_errors(checkboxes):
    default_group = "gh_action_default"
    errors = [
        {"group": default_group, "all": c["all"], "checked": c["checked"]}
        for g, c in checkboxes.items()
        if g == default_group and c["checked"] != c["all"]
    ]
    errors += [
        {"group": g, "all": c["all"], "checked": c["checked"]}
        for g, c in checkboxes.items()
        if g != default_group and c["checked"] == 0
    ]
    return errors



def has_unclosed_checkboxes(description: str):
    checkboxes = {
        "gh_action_default": { "all": 0, "checked": 0 }
    }
    active_group = None
    ignore_following = False

    for line in description.splitlines():
        if ignore_following:
            ignore_following = False
            continue

        line = line.strip()
        if (not line.startswith("- [")) and (not line.startswith("<!-- ")): continue
        if line.startswith("- [ ]"):
            checkboxes[active_group or "gh_action_default"]["all"] += 1
        elif line.startswith("- [X]"):
            checkboxes[active_group or "gh_action_default"]["all"] += 1
            checkboxes[active_group or "gh_action_default"]["checked"] += 1
        elif line.startswith("<!-- begin radio"):
            group_name = line[len("<!-- begin radio "):-len(" -->")]
            active_group = group_name
            if active_group not in checkboxes:
                checkboxes[active_group] = { "all": 0, "checked": 0 }
        elif line.startswith("<!-- end radio"):
            group_name = line[len("<!-- end radio "):-len(" -->")]
            active_group = None
        elif line == "<!-- ignore following -->":
            ignore_following = True

    errors = get_checkbox_errors(checkboxes)
    return [ len(errors) != 0, errors ]    
    
def main():
    errors = []

    if check_closing:
        closing_terms = has_closing_terms(pr_description)
        if not closing_terms:
            errors.append(no_closing_message or default_no_closing_message)
  
    if check_boxes:
        [ is_not_closed, unclosed_boxes ] = has_unclosed_checkboxes(pr_description)
        if  is_not_closed:
            res = (unchecked_boxes_message or default_unchecked_boxes_message) + "\n"
            for unclosed_box_data in unclosed_boxes:
                if unclosed_box_data["checked"] != unclosed_box_data["all"]:
                    group_name = "General" if unclosed_box_data["group"] == "gh_action_default" else unclosed_box_data["group"]
                    unchecked = unclosed_box_data["all"] - unclosed_box_data["checked"]
                    total = unclosed_box_data["all"]

                    line_template = unchecked_box_group_message or default_unchecked_box_group_message
                    res += line_template.format(group=group_name, unchecked=unchecked, all=total)

            if not unchecked_boxes_message:
                res += "\nPlease ensure all items are completed before requesting a review.\n"
            errors.append(res)

    if require_nondefault_branch and default_branch_name == pr_branch_name:
        errors.append(
            (branch_error_message or default_branch_error_message).format(
                base=default_branch_name, head=pr_branch_name
            )
        )



    no_errors = len(errors) == 0
    if no_errors: print(success_message or default_success_message)
    else: print("\n---\n".join(errors))


    sys.exit(0 if no_errors else 1)

main()