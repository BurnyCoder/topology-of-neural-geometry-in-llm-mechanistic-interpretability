"""Fetch bibliographic identity from Crossref, arXiv and primary sites for the publication's reference audit."""
from concurrent.futures import ThreadPoolExecutor
from html import unescape
import json
import re
import sys
import time
import unicodedata
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd

from neurotopo import config


def field(entry, name):
    """Read a braced BibTeX field, preserving nested title-capitalization braces."""
    start = re.search(r"\b"+name+r"\s*=\s*\{",entry,re.I)
    if not start:
        return ""
    level = 1
    for i in range(start.end(),len(entry)):
        level += (entry[i]=="{")-(entry[i]=="}")
        if not level:
            return entry[start.end():i]
    raise ValueError(f"Unclosed BibTeX field {name}")


def get(url):
    req = Request(url,headers={"User-Agent":"neurotopo scientific source verification/1.0"})
    for attempt in range(3):
        try:
            with urlopen(req,timeout=25) as response:
                return response.read().decode("utf-8",errors="replace")
        except HTTPError as exc:
            if attempt==2 or exc.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2**attempt)


def normalized(s):
    s = re.sub(r"\\v\s*\{?([A-Za-z])\}?", r"\1", s)
    plain = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    return "".join(re.findall(r"[a-z0-9]+",plain.lower()))


def check(entry):
    key = entry.split("{",1)[1].split(",",1)[0]
    title,doi,url = [field(entry,k) for k in ("title","doi","url")]
    if not doi and "doi.org/" in url:
        doi = url.split("doi.org/",1)[1]
    result = dict(key=key, bibliographic_title=title,source=url or "https://doi.org/"+doi)
    try:
        if doi:
            work = json.loads(get("https://api.crossref.org/works/"+quote(doi,safe="/")))["message"]
            actual = ": ".join([work["title"][0], *work.get("subtitle",[])])
            site = "publisher metadata via Crossref"
        elif "arxiv.org/" in url:
            document = get("https://arxiv.org/abs/"+url.rstrip("/").rsplit("/",1)[1])
            actual = re.search(r'<meta name="citation_title" content="([^"]+)',document).group(1)
            site = "arXiv version metadata"
        else:
            body = get(url)
            match = re.search(r"<title[^>]*>(.*?)</title>",body,re.I|re.S)
            actual,site = (match.group(1).strip() if match else ""), "linked primary resource"
        actual = unescape(re.sub(r"<[^>]*>","",actual))
        result.update(source_title=actual,basis=site,title_match=normalized(actual)==normalized(title))
    except Exception as exc:
        result.update(source_title="",basis="lookup unavailable: "+str(exc),title_match=False)
    return result


def main():
    sys.stdout.reconfigure(errors="backslashreplace")
    bib = (config.ROOT/"paper/references.bib").read_text(encoding="utf-8")
    entries = [e for e in re.split(r"(?m)^(?=@)",bib) if e.strip()]
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(check,entries))
    out = config.path("results")/"science"
    out.mkdir(exist_ok=True,parents=True)
    pd.DataFrame(rows).to_csv(out/"bibliography.csv",index=False)
    for r in rows:
        if not r["title_match"]:
            print(r["key"],r["basis"],r["source_title"][:140])


if __name__=="__main__":
    main()
