# Contributing

>Welcome!  Contributors are welcome, under the following guidelines.  You don't have to be a member of our GitHub Org to contribute!

This project is a complete rewrite and replacement for mechas2's codebase, written in Python 3.6.5.  This project is open source, released under [BSD-3](LICENSE).

Please note, that while some organization members have direct write access, all code additions are REQUIRED to be peer reviewed.  No one contributor may review their own code for the purposes of PR approval.

## Getting Started

1. Fork the [pipsqueak3](https://github.com/fuelrats/pipsqueak3) repo.
2. Checkout `develop` branch
3. Create a feature branch (See 'Feature Branches')
4. Develop your feature/doc/fix/insanity.
5. Ensure your local develop branch is up to date with upstream develop.
6. Submit PR.
7. Undergo peer review.
8. Make requested changes, if any.
9. Obtain cold beverage and celebrate when your PR is merged.

(If you are working off of a registered issue, please include the issue number in your PR title:
`Spark 99 / Update to Documentation`)

## Feature Branches

Make a feature branch off of master using `git checkout -b feature/my-awesome-feature`.
For other types of PRs please use one of the following:

* doc - Documentation, or Documentation Update
* feature - New Features/Functionality
* fix - Bug fixes

## PR Requirements
* **ALL** Pull Requests must undergo a peer review phase before being committed.
* PRs for new features without **meaningful** testing will _**NOT**_ be accepted.
* PRs that are out of scope or modify unnecessary files will _**NOT**_ be accepted.

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
* CodeClimate diff-coverage (85% required)
* CodeClimate total-coverage (>95% required)
* PEP8 Standards
* Circleci deployment testing (if applicable)

## Hygiene

**Please do not squash your commits prior to your PR.**  If this is necessary, it will be brought up during the review process.

Your PR should have sensible commits and messages.

All new features are required to contain tests sufficient for newly added code to be evaluated without reducing coverage.

After branching, you should immediately use `git push -u origin feature/my-awesome-feature` to make that the default upstream ref.

Before opening a PR, rebase onto develop so your PR can be merged fast-forward only, without merge commits.
The easiest way to do that is to make the main repo a remote using `git remote add upstream git@github.com:fuelrats/pipsqueak` and then running `git pull --rebase upstream develop`.

## Testing

**NOTICE: New tests must be done with py.test!  Furthermore, no Pull Request may break any existing test.**

New functionality should not compromise existing tests. Test definitions shall contain a docstring with the intended purpose of the testing function.

Please see our [Testing](./TESTING.md) file for in-depth requirements on this topic.

## Reporting Issues

Please refrain from using GitHub to report Issues, as we have since moved our main Issue Tracking to JIRA. Feel free to report any issues [there](http://t.fuelr.at/help).

