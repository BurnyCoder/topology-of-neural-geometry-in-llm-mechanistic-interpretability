"""Compile the publication using native LaTeX and BibTeX, or the self-contained Tectonic engine."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from neurotopo import config


def run():
    paper = config.ROOT / "paper"
    env = {**os.environ, "SOURCE_DATE_EPOCH":"1795651200", "FORCE_SOURCE_DATE":"1"}
    # TeX reads auxiliaries in its working directory. Stage just source files so a
    # bibliography left by a previous build cannot override the newly generated one.
    with tempfile.TemporaryDirectory(dir=paper) as folder:
        staging = Path(folder)
        work = staging / "paper"
        work.mkdir()
        for name in ("main.tex", "references.bib"):
            shutil.copyfile(paper/name, work/name)
        shutil.copytree(paper/"generated", work/"generated")
        shutil.copytree(config.path("figures"), staging/"docs"/"figures")
        if shutil.which("pdflatex") and shutil.which("bibtex"):
            cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
            subprocess.run(cmd, cwd=work, env=env, check=True)
            subprocess.run(["bibtex", "main"], cwd=work, env=env, check=True)
            for _ in range(2):
                subprocess.run(cmd, cwd=work, env=env, check=True)
            final_log = (work/"main.log").read_text(encoding="utf-8", errors="replace")
            if "There were undefined" in final_log:
                raise ValueError("The final LaTeX pass contains undefined references")
        else:
            subprocess.run(["tectonic", "main.tex"], cwd=work, env=env, check=True)
        shutil.copyfile(work/"main.pdf", paper/"main.pdf")
    shutil.copyfile(paper/"main.pdf", config.ROOT/"reports/paper.pdf")
