# PR Policy Checker

> Ensures PR compliance with project guidelines

![GitHub Marketplace](https://img.shields.io/badge/Marketplace-PR%20Policy%20Checker-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAM6wAADOsB5dZE0gAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAERSURBVCiRhZG/SsMxFEZPfsVJ61jbxaF0cRQRcRJ9hlYn30IHN/+9iquDCOIsblIrOjqKgy5aKoJQj4O3EEtbPwhJbr6Te28CmdSKeqzeqr0YbfVIrTBKakvtOl5dtTkK+v4HfA9PEyBFCY9AGVgCBLaBp1jPAyfAJ/AAdIEG0dNAiyP7+K1qIfMdonZic6+WJoBJvQlvuwDqcXadUuqPA1NKAlexbRTAIMvMOCjTbMwl1LtI/6KWJ5Q6rT6Ht1MA58AX8Apcqqt5r2qhrgAXQC3CZ6i1+KMd9TRu3MvA3aH/fFPnBodb6oe6HM8+lYHrGdRXW8M9bMZtPXUji69lmf5Cmamq7quNLFZXD9Rq7v0Bpc1o/tp0fisAAAAASUVORK5CYII=)

## Usage

```yml
- name: Check PR
  uses: Mozilla-Campus-Club-of-SLIIT/pr-check-action@v1
  with:
    check-closing-statement: true
    check-unchecked-boxes: true
    require-nondefault-branch: true
```

This action can check
- If a PR has proper closing statements (`closes`, `resolves`, `fixes`)
- If a PR has all the necessary checkboxes checked out
- If a PR is originating from a non-default branch (`feat-branch` -> `main` is fine. `main` -> `main` is not)

## Action inputs

By default, the action will run no checks. You can select which check you'd like to perform by configuring the inputs.

| Input | Description | Required | Default value |
| -------- | ---------------- | -------------- | ------------------- |
| `token` | `GITHUB_TOKEN`, [App token](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app) or [PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) | <ul><li>[ ] </li></ul> | `GITHUB_TOKEN` |
| `comment-author` | The account's name which the command check review should be published. Use `[bot]` suffix for apps. | <ul><li>[ ] </li></ul> | `github-actions[bot]` |
| `check-closing-statement` | Run the closing statement checker **only** if this input is set to `true`. | <ul><li>[ ] </li></ul> | `false` |
| `check-unchecked-boxes` | Check if all checkboxes are checked **only** if this input is set to `true`. | <ul><li>[ ] </li></ul> | `false` |
| `require-nondefault-branch` | Check if the PR is originating from a non-default branch. | <ul><li>[ ] </li></ul> | `false` |
| `no-closing-message` | Custom message when no closing statement is found. | <ul><li>[ ] </li></ul> |  |
| `unchecked-boxes-message` | Custom message when there are unchecked checkboxes. | <ul><li>[ ] </li></ul> |  |
| `unchecked-box-group-message` | Custom message template for each checkbox group. Use placeholders `{group}`, `{unchecked}`, `{all}`. | <ul><li>[ ] </li></ul> |  |
| `branch-error-message` | Custom message when the PR is originating from the default branch. Use placeholders `base` and `head` | <ul><li>[ ] </li></ul> |  |
| `success-message` | Custom message when all checks pass. | <ul><li>[ ] </li></ul> |  |

Note: In public repositories this action does not work in `pull_request` workflows when triggered by forks. This is due to token restrictions put in place by GitHub Actions. Alternatively, you can set the event to `pull_request_target`

> [!WARNING]
> Triggering actions with `pull_request_target` event may lead into security vulnerabilities. Read more about it [here](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target). However, you can ensure safety by not checking out the code at all. TLDR; don't use `actions/checkout` with `pull_request_target`

#### Controlling checkbox groups

You can control how checkbox groups behave using HTML comments. By default, every checkbox fall under the **Default** group (`gh_action_default`).

With `check-unchecked-boxes` option set to `true`, the action will check if all the checkboxes are checked under the default group. If there are unchecked boxes, the action will fail.

- If you like to imitate radio button behaviour, you can use the `<!-- begin radio groupname -->` and `<!-- end radio groupname -->` directives.
- If you like to skip checking certain checkboxes, you can ignore them with `<!-- ignore following -->`.

**eg:**

```md
Gender:
<!-- begin radio gender -->
- [ ] Male
- [ ] Female
- [ ] Other
<!-- end radio gender -->

<!-- ignore following -->
- [ ] I'd like to receive a weekly newsletter
```

## Examples

### Using a Github app with this action

The example given below is closer to the workflow we use [here](./.github/workflows/pr-check.yml)

```yml
name: PR Check
run-name: Check PR ${{ github.ref_name }}

on:
  workflow_dispatch:
  pull_request_target:
    types: [opened, synchronize, edited, reopened]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Generate github app token
        uses: wow-actions/use-app-token@v2
        id: app-token
        with:
          app_id: ${{ vars.APP_ID }}
          private_key: ${{ secrets.PRIVATE_KEY }}

      - name: Check PR
        uses: Mozilla-Campus-Club-of-SLIIT/pr-check-action@v1
        with:
          token: ${{ steps.app-token.outputs.bot_token }}
          comment-author: ${{ steps.app-token.outputs.bot_name}}[bot]
          check-closing-statement: true
          check-unchecked-boxes: true
          require-nondefault-branch: true
```

### Use custom error messages
```yml
name: PR Check
run-name: Check PR ${{ github.ref_name }}

on:
  workflow_dispatch:
  pull_request_target:
    types: [opened, synchronize, edited, reopened]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check PR
        uses: Mozilla-Campus-Club-of-SLIIT/pr-check-action@main
        with:
          check-closing-statement: true
          check-unchecked-boxes: true
          require-nondefault-branch: true
          # following lines define custom error messages
          no-closing-message: "Missing closing terms"
          unchecked-boxes-message: "There are unchecked checkboxes"
          unchecked-box-group-message: "{group}: {unchecked} out of {all}"
          branch-error-message: "PR originates from the default branch. Source branch: {head} (default) → Target branch: {base}"
```
