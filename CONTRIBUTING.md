# Contributing

>Welcome!  Contributors are welcome, under the following guidelines.  You don't have to be a member of our GitHub Org to contribute!

This project is a complete rewrite and replacement for mechas2's codebase, written in Python 3.7.  This project is open source, released under [BSD-3](LICENSE).

Please note that while some organization members have direct write access, all code additions are **REQUIRED** to be peer reviewed.

## Getting Started

1. Fork the [pipsqueak3](https://github.com/fuelrats/pipsqueak3) repository.
2. Checkout `develop` branch
3. Create a feature branch (See 'Feature Branches')
4. Develop your feature/doc/fix/insanity.
5. Ensure your local develop branch is up to date with upstream develop.
6. Submit PR.
7. Undergo peer review.
8. Make requested changes, if any.  If after your peer review changes are requested, your work cannot be merged until changed.
9. Obtain cold beverage and celebrate when your PR is merged.

**Blocked Pull Request?** If any reviewer adds a blocking tag to a comment during the review,  changes are *required* and a merge cannot proceed without a change.  All additions undergo this process, and it is used to ensure that only high quality, professional code is merged with the code base without incurring any technical debt.  Please see the section on tagging below for more details.

## Feature Branches

Make a feature branch off of master using `git checkout -b feature/my-awesome-feature`.
For other types of pull requests please use one of the following:

* doc - Documentation, or Documentation Update
* feature - New Features/Functionality
* fix - Bug fixes
* testing - New or updated tests.

## PR Requirements
* **ALL** Pull Requests must undergo a peer review phase before being committed.
* Pull Requests for new features without **meaningful** testing will _**NOT**_ be accepted.
* Pull Requests that are out of scope or modify unnecessary files will _**NOT**_ be accepted.

Use docstrings and comments to document how your features function and why. Docstrings should be formatted to the flavour of [Google](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments).

Example docstring:
```python
def example_function(param1: int, param2: str) -> bool:
    """
    This is an example doc string.  It may span multiple lines, however
    it may not break the 100 characters per line PEP8 standard.  It is a
    good standard to include expected types, explain what your function
    attempts to accomplish, and what result is returned, if any.

    Args:
        param1 (int): First Parameter.
        param2 (str): Second Parameter.

    Returns:
        bool: True if successful, False otherwise.
    """
    return False
```

### Build Integrity

All pull requests must pass standard checks:
* Build must be be successful and functional (obviously!)
* Must pass all integrity checks
    * Codecov diff-coverage (85% required)
    * Codecov total-coverage (>90% required)
    * pycodestyle pep8 standards
    * pylint pass with no error levels or higher
    * Circleci unit test run (Pytest)
* Circleci deployment testing (if applicable)

> It is good practice to ensure that all tests are passing in your feature branch before submitting your pull request. If the test suite fails to pass, your request WILL be blocked from merging until testing is resolved.
## Hygiene

**Please do not squash your commits prior to your PR.**  If this is necessary, it will be brought up during the review process.

Your PR should have sensible commits and messages.  Please see the **Naming & Commenting Standards** section below.

New features are required to contain tests sufficient for newly added code to be evaluated without reducing coverage.

After branching, you should immediately use `git push -u origin feature/my-awesome-feature` to make that the default upstream ref.

Before opening a PR, rebase onto develop so your PR can be merged fast-forward only, without merge commits.
The easiest way to do that is to make the main repository a remote using `git remote add upstream git@github.com:fuelrats/pipsqueak3` and then running `git pull --rebase upstream develop`.

## Naming & Commenting Standards

### Commit Messages
Prefix all commit messages with the SPARK issue number.  If addressing multiple tickets, create a commit for each change and do not combine them.

#### Example Commit message (Single Issue)
This is most commonly used.  The issue number should match the pull request issue.

Pull Request Title: ``[SPARK-4021] Add color support to MechaClient``

```
Commit Messages:
[SPARK-4021] Add method for color override
[SPARK-4021] Change property to global
[SPARK-4021] Create new base class for colors, added to stdlib
```

#### Example Commit message - Multiple Issues

In the event your pull request covers multiple issues (such as a sprint or JIRA Story), prefix each commit with the issue it covers.

``[SPARK-4024]`` in this case would be a Story.

Pull Request Title: ``[SPARK-4024] Prepare for Major Release``

```
Commit Messages:
[SPARK-4030] Increment Version number
[SPARK-4032] Pipfile update for dependencies, pre-release
[SPARK-4038] Adjust Sphinx configuration toc-tree depth
```

### Pull Requests Naming
If working from a registered issue, Include the issue name enclosed in brackets in the title of your Pull Request, ie `[SPARK-99] Update to CONTRIBUTING.md`

Otherwise, use the type of request:

``[Doc] Update TOS to revoke snickers delivery``

``[Fix] Mechaclient.py should return None after valid on_message event``

You may be asked to rename your Pull Request before peer review can begin if the name is not specific enough or not within standard.

### Peer Review Tagging System
During a peer review, reviewers will add a tag to the comment to help the author understand what type of action is required to receive an approving review.

#### Blocking Tags

| Tag | Explanation |
| --- | --- |
[Consensus]|Team Decision required.  This issue will be hammered out until an agreement is made.
[Discussion]|Discussion is required between the author and the reviewer.
[Error]|Incorrect Methodology or Implementation.
[Incomplete]|Incomplete code and/or Pull Request.
[Scope]|Out of scope for your Pull Request.
[Style]|Breaking style guidelines, or other issue specifically with code style.
[Testing]|Reviewer requests a usage case, or testing is missing from the pull request.

#### Non-Blocking Tags

| Tag | Explanation |
| --- | --- |
[Not Blocking]|Not to be used alone.  Negates a blocking issue.
[Kudos]|The reviewer liked this, specifically. Go you.
[Suggestion]| An optional, alternative approach.

Adding multiple tags to a comment is fine.  Do not combine tags.

Good: ``[Suggestion][Kudos] This is great, but...``

Bad:  ``[Suggestion|Kudos] This is great, but...``


## Pull request labels
Labels may be applied to your pull requests, for the purposes of organization and / or overall 
status.

| label | Explanation |
| --- | --- |
Awaiting changes    | this pull request is on hold until requested changes have been effected
Feature             | this pull request adds a new feature
Bug Fix             | this pull request fixes some bug
Refactor            | this pull request refactors something
Documentation       | this pull request only effects documentation
Linting             | this pull request adjusts our linting configurations
CI change           | This pull request reconfigures the CI environment
Dependency change   | this pull request modifies our dependencies
Policy              | this pull request modifies our contributing policies
Consensus required  | this pull request requires the consensus of all core contributors

## Testing

**NOTICE: All tests will be run with pytest. Furthermore, no Pull Request may break any existing test.**

New functionality should not compromise existing tests. Test definitions shall contain a docstring with the intended purpose of the testing function.

Please see our [Testing](./TESTING.md) file for in-depth requirements on this topic.

## Reporting Issues

Please refrain from using GitHub to report Issues, as we have since moved our main Issue Tracking to JIRA. Feel free to report any issues [there](http://t.fuelr.at/help).