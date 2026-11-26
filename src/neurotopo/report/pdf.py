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
    with tempfile.TemporaryDirectory(dir=paper) as folder:
        dest = Path(folder)
        if shutil.which("pdflatex") and shutil.which("bibtex"):
            cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={dest}", "main.tex"]
            subprocess.run(cmd, cwd=paper, env=env, check=True)
            shutil.copyfile(paper/"references.bib", dest/"references.bib")
            subprocess.run(["bibtex", "main"], cwd=dest, env=env, check=True)
            for _ in range(2):
                subprocess.run(cmd, cwd=paper, env=env, check=True)
        else:
            subprocess.run(["tectonic", "--outdir", str(dest), "main.tex"], cwd=paper, env=env, check=True)
        shutil.copyfile(dest/"main.pdf", paper/"main.pdf")
    shutil.copyfile(paper/"main.pdf", config.ROOT/"reports/paper.pdf")
