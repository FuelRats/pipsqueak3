# Reporting Issues

Please refrain from using GitHub to report Issues, as we have since moved our main Issue Tracking to JIRA. Feel free to report any Issues [there.](http://t.fuelr.at/help)

# Contributing

* You are free to commit to the develop branch directly if you are a Tech Rat Team member.

1. Fork the main repo on github
2. Create a feature branch
3. Develop your feature/fix/whatever
4. Rebase onto upstream mecha3
5. Submit a PR

## Feature branches

Make a feature branch off of master using `git checkout -b feature/my-awesome-feature`. Instead of 'feature' you can also put 'fix' in front of the branch name if it's a bugfix or 'doc' if you only add documentation.

## Hygiene

After branching, you should immediately use `git push -u origin feature/my-awesome-feature` to make that the default upstream ref.

Before opening a PR, rebase onto `mecha3` so your PR can be merged fast-forward only, without merge commits. The easiest way to do that is to make the main repo a remote using `git remote add upstream git@github.com:fuelrats/pipsqueak` and then running `git pull --rebase upstream mecha3`. Your PR should have sensible commits with sensible commit messages. It is *not* required or appreciated to squash PRs into a single commit. Every commit by itself should leave the codebase in a working state.

## Testing and Documentation

Use docstrings and comments to document how your features function and why.
Docstrings should be formatted to the flavour of [Google](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments)
Further, all new features must include Unit Tests.
 
PRs for new features without **meaningful** Unit Tests will _**NOT**_
be accepted. 

If you are fixing an existing feature, the relevant UTs should not break. 

### Code Coverage
At least 85% of your introduced code must be covered by tests, the more the merrier.
The module you touch should not fall below 85% coverage, and should cover all meaningful portions of the contribution.
If your tests are not covering enough, we will request you revisit your testing before we will considering merging.