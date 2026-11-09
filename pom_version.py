"""Verify that a commit range changes only the literal root Maven project version."""
import re
import subprocess
from xml.parsers import expat


def split_version(data):
    stack, starts, ranges = [], [], []
    parser = expat.ParserCreate(namespace_separator=" ")
    def opened(name, attrs):
        stack.append(name.rsplit(" ", 1)[-1])
        if stack == ["project", "version"]:
            starts.append(parser.CurrentByteIndex)
    def closed(name):
        if stack == ["project", "version"]:
            start = data.index(b">", starts.pop()) + 1
            end = parser.CurrentByteIndex
            if end < start or not re.fullmatch(rb"[A-Za-z0-9][A-Za-z0-9._+-]*", data[start:end]):
                raise ValueError("Expected a literal project version.")
            ranges.append((start, end))
        stack.pop()
    parser.StartElementHandler, parser.EndElementHandler = opened, closed
    parser.Parse(data, True)
    if len(ranges) != 1:
        raise ValueError("Expected one root project version.")
    start, end = ranges[0]
    return data[:start], data[start:end], data[end:]


def verify(before, after):
    commits = [subprocess.check_output(["git", "rev-parse", "--verify", "--end-of-options",
                                        ref + "^{commit}"], text=True).strip() for ref in (before, after)]
    diff = subprocess.check_output(["git", "diff", "--name-only", "-z", *commits])
    if diff != b"pom.xml\0":
        raise ValueError("Only the root pom.xml may change.")
    blobs = []
    for commit in commits:
        tree = subprocess.check_output(["git", "ls-tree", commit, "--", "pom.xml"])
        if not tree.startswith(b"100644 blob "):
            raise ValueError("Expected a regular non-executable root pom.xml.")
        blobs.append(split_version(subprocess.check_output(["git", "show", commit + ":pom.xml"])))
    (prefix, old, suffix), (new_prefix, new, new_suffix) = blobs
    if prefix != new_prefix or suffix != new_suffix or old == new:
        raise ValueError("Only project/version may change.")
    print(f"Verified project version {old.decode()} -> {new.decode()}")
