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
    if not closing_terms: res += "No closing terms\n"
    if is_not_closed:
        res += "Unchecked checkboxes\n"
        for unclosed_box_data in unclosed_boxes:
            res += "{}: {} out of {} checkboxes are unchecked\n".format(
                "General" if unclosed_box_data["group"] == "gh_action_default" else unclosed_box_data["group"],
                unclosed_box_data["all"] - unclosed_box_data["checked"],
                unclosed_box_data["all"]
            )
    print(res)
    sys.exit(1)

print("All good")

