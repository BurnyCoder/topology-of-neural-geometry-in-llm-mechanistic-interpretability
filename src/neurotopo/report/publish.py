"""Publish the verified public datasets and paper as one revision of the existing Hugging Face dataset."""
import hashlib
import json
import logging
from pathlib import Path
import re
import subprocess

from huggingface_hub import CommitOperationAdd, HfApi

from neurotopo import config
from neurotopo.data import hub
from neurotopo.report.science import GIT, REVIEW

log = logging.getLogger(__name__)


def external_markdown(path):
    """Keep local evidence links usable when a GitHub report is mirrored at a different Hub path."""
    root = config.ROOT
    def absolute(match):
        target = match.group(1)
        if "://" in target or target.startswith("#"):
            return match.group(0)
        file, _, anchor = target.partition("#")
        link = (path.parent/file).resolve().relative_to(root).as_posix()
        return "]("+GIT+link+("#"+anchor if anchor else "")+")"
    return re.sub(r"\]\(([^ )]+)\)",absolute,path.read_text(encoding="utf-8")).encode()


def blob_id(data):
    """Match the Git blob identifier used by Hugging Face for an ordinary file."""
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def mirrored_text(data, committed_id):
    """Keep already committed bytes, including historical CRLF and binary-looking text."""
    # Git's text=auto preserves files already committed with CRLF until renormalized.
    # https://git-scm.com/docs/gitattributes#_eol
    if b"\r\n" not in data or b"\0" in data or blob_id(data) == committed_id:
        return data
    return data.replace(b"\r\n", b"\n")


def committed_file_ids(root):
    entries = subprocess.check_output(["git", "ls-tree", "-r", "-z", "HEAD", "--", "results", "logs"], cwd=root)
    ids = {}
    for entry in entries.decode().split("\0"):
        if entry:
            header, name = entry.split("\t", 1)
            ids[name] = header.rsplit(" ", 1)[-1]
    return ids


def run():
    root = config.ROOT
    repo = config.load()["hf"]["dataset"]
    api = HfApi()
    revision = api.repo_info(repo,repo_type="dataset").sha
    remote = {f.path:f for f in api.list_repo_tree(repo,repo_type="dataset",revision=revision,recursive=True)
              if hasattr(f,"blob_id")}
    manifest = json.loads((config.path("inputs")/"manifest.json").read_text())
    payload = {"README.md":hub.dataset_card(manifest).encode(), "paper.pdf":root/"paper/main.pdf",
               "summary.md":external_markdown(root/"reports/summary.md"),
               f"reports/reviews/{REVIEW}.md":external_markdown(root/f"reports/reviews/{REVIEW}.md")}
    # A running publish log is incomplete. Experiment logs are already closed and can be mirrored.
    active_logs = {Path(h.baseFilename).resolve() for h in logging.getLogger().handlers if hasattr(h,"baseFilename")}
    for folder in ("results","logs"):
        payload.update({p.relative_to(root).as_posix():p for p in (root/folder).rglob("*")
                        if p.is_file() and p.resolve() not in active_logs})
    committed = committed_file_ids(root)
    ops = []
    for name,value in sorted(payload.items()):
        entry = remote.get(name)
        data = value.read_bytes() if isinstance(value,Path) else value
        if isinstance(value,Path) and value.suffix in {".csv",".tsv",".json",".log",".md",".txt"}:
            value = data = mirrored_text(data, committed.get(name))
        if entry and entry.size==len(data):
            if entry.lfs:
                same = entry.lfs.sha256 == hashlib.sha256(data).hexdigest()
            else:
                same = entry.blob_id == blob_id(data)
            if same:
                continue
        ops.append(CommitOperationAdd(path_in_repo=name, path_or_fileobj=value))
    if ops:
        commit = api.create_commit(repo,repo_type="dataset",operations=ops,parent_commit=revision,
                                   commit_message="Publish independent scientific audit and corrected study artifacts")
        revision = commit.oid
    log.info("Verified publication files at dataset revision %s (%d changed paths)",revision,len(ops))
