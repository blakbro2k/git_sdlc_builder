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

The init preview checks the active github.com login, repository role, and label listing.
It prints which branch, labels, and files would be created. Apply uses the same checks.
The preview cannot prove that Git push or a label write will succeed. If a label write
fails, fix the credential access and rerun init to reuse completed remote changes.

## Label palette and branch rules

Init creates or updates the eight SDLC labels from label-colors.json. For an existing
bootstrap, run `sdlc labels --dry-run`, then `sdlc labels`. Existing labels keep their
issue/PR assignments and descriptions.

After the bootstrap workflow has run successfully, preview the proposed rules with
`sdlc ruleset dev` and `sdlc ruleset main`. From the target checkout, create each
reviewed ruleset once using `sdlc ruleset dev | gh api --method POST repos/{owner}/{repo}/rulesets --input -`
(and repeat for main). Check Settings → Rules → Rulesets for existing rules before
creating them. These rules require PRs and the GitHub Actions policy check, prevent
deletion and force pushes, and permit a solo maintainer to merge without a second reviewer.

For deployments configure a production environment: restrict deployment branches to
main, select the owner and named production admins as required reviewers, and disable
administrator bypass. Every production deployment job must reference that environment;
scope production credentials to it. Branch rules do not approve a deployment.

If release automation changes a Maven version, validate the before/after commit pair for
that version change independently of the full release PR (which also contains application
changes). Never grant a blanket bypass on the basis of a pom.xml filename.

Run `sdlc check-pom-version BEFORE AFTER` in the target repository to verify that
the only changed file is the root pom.xml and only the literal project/version value
changed. Use it on the version-bump commit in the eventual release workflow. It is
a standalone check until that workflow invokes it.
