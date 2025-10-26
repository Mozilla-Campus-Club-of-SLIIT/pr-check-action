import sys
import os
import re

pr_description = os.getenv("PR_DESCRIPTION", "")

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
        if (g == default_group and c["checked"] != c["all"])
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
    

closing_terms = has_closing_terms(pr_description)
[ is_not_closed, unclosed_boxes ] = has_unclosed_checkboxes(pr_description)


if (not closing_terms) or is_not_closed:
    res = ""
    
    if not closing_terms:
        res += "### ❌ Missing Closing Terms\n"
        res += "This PR does not reference an issue with `closes`, `fixes`, or `resolves` keywords. "
        res += "Please update the PR description to automatically close the relevant issue when merged.\n\n"
    
    if is_not_closed:
        res += "### ❌ Unchecked Checkboxes\n"
        res += "Some required checklist items in the PR description are not checked. Make sure all mandatory tasks are completed:\n"
        for unclosed_box_data in unclosed_boxes:
            group_name = "General" if unclosed_box_data["group"] == "gh_action_default" else unclosed_box_data["group"]
            unchecked = unclosed_box_data["all"] - unclosed_box_data["checked"]
            total = unclosed_box_data["all"]
            res += f"- **{group_name}**: {unchecked} out of {total} checkboxes are unchecked\n"
        res += "\nPlease ensure all items are completed before requesting a review.\n"
    
    print(res)
    sys.exit(1)

print("✅ All checks passed")


