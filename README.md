# git_sdlc_builder

Install a GitHub SDLC workflow in an existing repository. Requires Python 3, Git, and an authenticated GitHub CLI with permission to push branches and manage labels in the target.

Clone this builder next to the target checkout. From RocketFlyIII, run:

```sh
../git_sdlc_builder/sdlc init --dry-run
../git_sdlc_builder/sdlc init
git status --short
git add .github CONTRIBUTING.md
git commit -m "Install branch and PR label policy"
../git_sdlc_builder/sdlc pr --version patch
```

Init uses the profile shipped with the builder. It creates a missing dev branch from main, installs missing labels, and writes new policy files on feature/sdlc-bootstrap. Review that branch and merge its PR into dev. For a pending bootstrap, finish the existing branch; after merge, init recognizes installed files. Dry-run fetches the base commit locally for comparison.

After bootstrap, from the target checkout:

```sh
../git_sdlc_builder/sdlc start feature "List Firefly accounts" --issue 1
# Implement and commit your changes.
../git_sdlc_builder/sdlc pr --version minor
```

Replace 1 with a real issue number, or omit --issue. start also accepts bug and remediate. Use --push to publish the branch immediately. The generated policy checks work labels for integration and release/version labels for integration and production. Required-check enforcement can be configured separately in GitHub repository settings. Production PRs from dev to main are opened manually.
