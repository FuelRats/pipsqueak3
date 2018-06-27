# Reporting Issues

Please refrain from using GitHub to report Issues, as we have since moved our main Issue Tracking to JIRA. Feel free to report any issues [there](http://t.fuelr.at/help).

# Contributing

>Welcome!  Contributors are welcome, under the following guidelines.  You don't have to be a member of our GitHub Org to contribute!

This project is a complete rewrite and replacement for mechas2's codebase, written in Python 3.6.5.  This project is open source, released under [BSD-3](LICENSE).

Please note, that while some organization members have direct write access, all code additions are REQUIRED to be peer reviewed.  No one contributor may review their own code for the purposes of PR approval.

## Getting Started

1. Fork the [pipsqueak3](https://github.com/fuelrats/pipsqueak3) repo.
2. Checkout `develop` branch.
3. Develop your feature/doc/fix/insanity.
4. Ensure your local develop branch is up to date with upstream develop.
5. Submit PR.
6. Undergo peer review.
7. Make requested changes, if any.
8. Obtain cold beverage and celebrate when your PR is merged.

(If you are working off of a registered issue, please include the issue number in your PR title: `Spark 99 / Update to Documentation`)

## PR Requirements
* **ALL** Pull Requests must undergo a peer review phase before being committed.
* PRs for new features without **meaningful** testing will _**NOT**_ be accepted.
* PRs that are out of scope or modify unnecessary files will _**NOT**_ be accepted.

Use docstrings and comments to document how your features function and why. Docstrings should be formatted to the flavour of [Google](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments)
Example:
```python
def example_function(param1: int, param2: str) -> Optional[bool]:
"""
This is an example doc string.  It may span multiple lines, however
it may not break the 100 characters per line PEP8 standard.  It is a
good standard to include expected types, explain what your function
attempts to accomplish, and what result is returned, if any.

Args:
    param1 (int): First Parameter.
    param2 (str): Second Parameter.

Returns:
    Optional[bool]: True if successful, False otherwise.
"""
return False
```


### Build Integrity

All pull requests must pass integrated standards:
1. Build must be be successful and functional (obviously!)
2. CodeClimate diff-coverage (85% required)
3. CodeClimate total-coverage (>95% required)
4. PEP8 Standards
5. Circleci deployment testing (if applicable)

## Feature branches

Make a feature branch off of master using `git checkout -b feature/my-awesome-feature`.
For other types of PRs please use one of the following:

* doc - Documentation, or Documentation Update
* feature - New Features/Functionality
* fix - Bugfixes

## Hygiene

After branching, you should immediately use `git push -u origin feature/my-awesome-feature` to make that the default upstream ref.

Before opening a PR, rebase onto develop so your PR can be merged fast-forward only, without merge commits.
The easiest way to do that is to make the main repo a remote using `git remote add upstream git@github.com:fuelrats/pipsqueak` and then running `git pull --rebase upstream develop`.


>Your PR should have sensible commits with sensible commit messages.


**Please do not squash your commits prior to your PR.**  If this is necessary, it will be brought up during the review process.

## Testing

**NOTICE: New tests must be done with py.test!  Furthermore, no new features may break the existing grandfathered unit tests.  They will be rewritten at a later date**

New functionality should not compromise existing tests. They should also contain a docstring with the intended purpose of the testing function.


>All new features are required to contain testing sufficient to test newly added code and to maintain overall code coverage.


Please see our [Testing](TESTING.MD) file for in-depth requirements on this topic.

