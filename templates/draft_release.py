"""Stage a draft GitHub release for a merged production PR."""
import json
import os
from pathlib import Path
import re
import subprocess

from sdlc_policy import errors


def output(*args):
    return subprocess.check_output(args, text=True).strip()


def release_tag(sha, bump):
    versions = {}
    for tag in output("git", "tag", "--merged", sha).splitlines():
        match = re.fullmatch(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", tag)
        if match:
            versions[tuple(map(int, match.groups()))] = tag
    existing = [tag for tag in versions.values()
                if output("git", "rev-parse", tag + "^{commit}") == sha]
    if len(existing) > 1:
        raise ValueError("Multiple production tags already point to this merge.")
    if existing:
        return existing[0], True
    parts = list(max(versions, default=(0, 0, 0)))
    index = ("major", "minor", "patch").index(bump)
    parts[index] += 1
    parts[index + 1:] = [0] * (2 - index)
    return "v" + ".".join(map(str, parts)), False


def main():
    pr = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())["pull_request"]
    profile = json.loads(Path(".github/sdlc.json").read_text())
    repo = os.environ["GITHUB_REPOSITORY"]
    sha = pr["merge_commit_sha"]
    if (not pr["merged"] or pr["head"]["repo"]["full_name"] != repo
            or pr["base"]["ref"] != profile["production"] or output("git", "rev-parse", "HEAD") != sha):
        raise ValueError("Expected the merged production PR checkout.")
    labels = {label["name"] for label in pr["labels"]}
    problems = errors(profile, pr["head"]["ref"], pr["base"]["ref"], labels)
    if problems:
        raise ValueError(" ".join(problems))
    bump = next(label.removeprefix("version:") for label in labels if label.startswith("version:"))
    tag, exists = release_tag(sha, bump)
    if not exists:
        # A non-forced push fails safely if another release claimed the version.
        subprocess.run(["git", "push", "origin", f"{sha}:refs/tags/{tag}"], check=True)
    lookup = subprocess.run(["gh", "release", "view", tag, "--repo", repo, "--json", "tagName"])
    if lookup.returncode:
        subprocess.run(["gh", "release", "create", tag, "--repo", repo, "--verify-tag",
                        "--draft", "--title", tag, "--generate-notes"], check=True)


if __name__ == "__main__":
    main()
