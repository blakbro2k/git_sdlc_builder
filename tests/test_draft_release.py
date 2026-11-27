import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DraftReleaseTest(unittest.TestCase):
    def test_merge_retry_and_rejected_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "project"
            repo.mkdir()

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

            git("init", "--quiet")
            git("init", "--quiet", "--bare", str(root / "remote"))
            git("remote", "add", "origin", str(root / "remote"))
            git("config", "user.email", "test@example.com")
            git("config", "user.name", "Test")
            config = repo / ".github"
            config.mkdir()
            shutil.copy(ROOT / "profile.json", config / "sdlc.json")
            for source, target in [("policy.py", "sdlc_policy.py"), ("draft_release.py", "draft_release.py")]:
                shutil.copy(ROOT / "templates" / source, repo / target)
            git("add", ".")
            git("commit", "-qm", "previous")
            git("tag", "v1.9.4")
            git("tag", "v9.0.0-SNAPSHOT")
            git("commit", "--allow-empty", "-qm", "production merge")
            sha = git("rev-parse", "HEAD")
            pr = {"merged": True, "merge_commit_sha": sha, "head": {"ref": "dev", "repo": {"full_name": "test/repo"}},
                  "base": {"ref": "main"}, "labels": [{"name": "release:production"}, {"name": "version:minor"}]}
            event = root / "event.json"
            gh = root / "gh"
            gh.write_text('#!/bin/sh\ncase "$2" in\nview) test -f release-record;;\ncreate) echo "$@" >>release-record;;\nesac\n')
            gh.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ["PATH"],
                       GITHUB_EVENT_PATH=str(event), GITHUB_REPOSITORY="test/repo")

            def run():
                event.write_text(json.dumps({"pull_request": pr}))
                return subprocess.run(["python3", "draft_release.py"], cwd=repo, env=env, capture_output=True)

            pr["labels"].append({"name": "version:patch"})
            self.assertNotEqual(run().returncode, 0)
            self.assertEqual(git("ls-remote", "--tags", "origin"), "")
            pr["labels"].pop()
            self.assertEqual(run().returncode, 0)
            git("fetch", "--tags", "origin")
            self.assertEqual(git("rev-parse", "v1.10.0"), sha)
            self.assertEqual(run().returncode, 0)
            record = (repo / "release-record").read_text().splitlines()
            self.assertEqual(len(record), 1)
            self.assertIn("--draft", record[0])
