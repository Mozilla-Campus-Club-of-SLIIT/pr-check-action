import os
import re
import sys

pr_description = os.getenv("PR_DESCRIPTION", "")
check_closing = os.getenv("CHECK_CLOSING_STATEMENT", "false").lower() == "true"
check_boxes = os.getenv("CHECK_UNCHECKED_BOXES", "false").lower() == "true"

no_closing_message = os.getenv("NO_CLOSING_MESSAGE", "").strip()
unchecked_boxes_message = os.getenv("UNCHECKED_BOXES_MESSAGE", "").strip()
unchecked_box_group_message = os.getenv("UNCHECKED_BOX_GROUP_MESSAGE", "").strip()
success_message = os.getenv("SUCCESS_MESSAGE", "").strip()

default_no_closing_message = (
    "### ❌ Missing Closing Terms\n"
    "This PR does not reference an issue with `closes`, `fixes`, or `resolves` keywords.\n"
    "Please update the PR description to automatically close the relevant issue when merged.\n"
)

default_unchecked_boxes_message = (
    "### ❌ Unchecked Checkboxes\n"
    "Some required checklist items in the PR description are not checked. Make sure all mandatory tasks are completed:\n"
)

default_unchecked_group_line = "- **{group}**: {unchecked} out of {all} checkboxes are unchecked\n"

default_unchecked_boxes_footer = "\nPlease ensure all items are completed before requesting a review.\n"

default_success_message = "✅ All checks passed"

def has_closing_terms(description: str):
    return bool(re.search(
        r"(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved):?\s#\d+",
        description,
        flags=re.MULTILINE | re.IGNORECASE
    ))

def get_checkbox_errors(checkboxes):
    errors = []
    for g, c in checkboxes.items():
        if c["checked"] != c["all"]:
            errors.append({"group": g, "all": c["all"], "checked": c["checked"]})
    return errors

def has_unclosed_checkboxes(description: str):
    checkboxes = {"gh_action_default": {"all": 0, "checked": 0}}
    active_group = None
    ignore_following = False

    for line in description.splitlines():
        line = line.strip()
        if ignore_following:
            ignore_following = False
            continue
        if line.startswith("<!-- ignore following -->"):
            ignore_following = True
            continue
        if line.startswith("<!-- begin radio"):
            group_name = line[len("<!-- begin radio "):-len(" -->")]
            active_group = group_name
            if active_group not in checkboxes:
                checkboxes[active_group] = {"all": 0, "checked": 0}
            continue
        if line.startswith("<!-- end radio"):
            active_group = None
            continue
        if not line.startswith("- ["):
            continue

        group = active_group or "gh_action_default"
        if line.startswith("- [ ]"):
            checkboxes[group]["all"] += 1
        elif line.startswith("- [X]"):
            checkboxes[group]["all"] += 1
            checkboxes[group]["checked"] += 1

    errors = get_checkbox_errors(checkboxes)
    return [len(errors) != 0, errors]

def main():
    errors = []

    if check_closing and not has_closing_terms(pr_description):
        errors.append(no_closing_message or default_no_closing_message)

    if check_boxes:
        has_errors, unclosed_boxes = has_unclosed_checkboxes(pr_description)
        if has_errors:
            res = (unchecked_boxes_message or default_unchecked_boxes_message) + "\n"
            for unclosed_box_data in unclosed_boxes:
                group_name = (
                    "General" if unclosed_box_data["group"] == "gh_action_default"
                    else unclosed_box_data["group"]
                )
                unchecked = unclosed_box_data["all"] - unclosed_box_data["checked"]
                total = unclosed_box_data["all"]
                line_template = unchecked_box_group_message or default_unchecked_group_line
                res += line_template.format(group=group_name, unchecked=unchecked, all=total).rstrip() + "\n"
            if not unchecked_boxes_message:
                res += default_unchecked_boxes_footer
            errors.append(res)

    no_errors = len(errors) == 0
    print(success_message or default_success_message if no_errors else "\n---\n".join(errors))
    sys.exit(0 if no_errors else 1)

main()
