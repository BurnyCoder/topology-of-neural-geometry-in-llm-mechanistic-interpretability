"""Publish the verified public datasets and paper as one revision of the existing Hugging Face dataset."""
import hashlib
import json
import logging
from pathlib import Path
import re

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
    for folder in ("results","logs"):
        payload.update({p.relative_to(root).as_posix():p for p in (root/folder).rglob("*") if p.is_file()})
    ops = []
    for name,value in sorted(payload.items()):
        entry = remote.get(name)
        data = value.read_bytes() if isinstance(value,Path) else value
        if entry and entry.size==len(data):
            if entry.lfs:
                same = entry.lfs.sha256 == hashlib.sha256(data).hexdigest()
            else:
                same = entry.blob_id == hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
            if same:
                continue
        ops.append(CommitOperationAdd(path_in_repo=name, path_or_fileobj=value))
    if ops:
        commit = api.create_commit(repo,repo_type="dataset",operations=ops,parent_commit=revision,
                                   commit_message="Publish independent scientific audit and corrected study artifacts")
        revision = commit.oid
    log.info("Verified publication files at dataset revision %s (%d changed paths)",revision,len(ops))
