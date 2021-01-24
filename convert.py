"""Convert twitter URLs in markdown file to HTML cards

Also sorts H1 headers.
"""
from dataclasses import dataclass
from pathlib import Path
from datetime import timedelta

import md_toc  # type: ignore
import requests

URL = "https://twitter.com/{name}/status/{id}"
API = "https://publish.twitter.com/oembed?url={url}"

import requests_cache
requests_cache.install_cache("tweets", expire_after = timedelta(days=30))

@dataclass
class Tweet:
    """Original code: https://bit.ly/3p9kI0T"""

    name: str
    id: int

    @property
    def url(self):
        return URL.format(name=self.name, id=self.id)

    @property
    def api_url(self):
        # Twitter's oEmbed API  https://dev.twitter.com/web/embedded-tweets
        print("Processing", self)
        return API.format(url=self.url)

    def html(self):
        return requests.get(self.api_url).json()["html"]

    def _repr_html_(self):
        return self.html()


def mk_tweet(s: str) -> Tweet:
    """Constructor for Tweet instance.
    
    Parameters
    ----------
    s : str
        twitter URL, eg "https://twitter.com/PHuenermund/status/1352909842118291457"
    """
    a = s.strip().split("/")
    ix = a.index("status")
    return Tweet(a[ix - 1], int(a[ix + 1]))


def to_list(doc: str):
    return [x.strip() for x in doc.split("\n")]


def substitute_tweets(line: str) -> str:
    """Change tweet url to html."""
    return mk_tweet(line).html() if is_tweet_url(line) else line

def yield_groups(lines, mark="# "):
    group = []
    for line in lines:
        if line.startswith(mark):
            yield group
            group = [line]
        else:
            group += [line]

def is_tweet_url(line: str) -> bool:
    return line.startswith("http") and ("status" in line)

def sort_blocks(doc):
    """Sort H1 header blocks alphabetically."""
    lines = to_list(doc)
    groups = [group for group in yield_groups(lines) if group]
    groups = sorted(groups, key = lambda xs: xs[0])
    lines = [line for group in groups for line in group]
    return "\n".join(lines)


def count_tweets(lines):
    return len(list(filter(is_tweet_url, lines)))
    
def create_output(doc: str):    
    # create toc via temp file (that is how md_toc.build_toc works)
    text = sort_blocks(doc)
    Path("tempfile.txt").write_text(text, encoding="utf-8")    
    toc = md_toc.build_toc("tempfile.txt")
    
    # make cards
    lines = to_list(doc)
    lines = list(map(substitute_tweets, lines))    
    
    # combine toc and body
    body = "\n".join(lines)    
    return "\n".join([toc, body])

    
def main(source_file="_README.md", destination_file="README.md"):    
    doc = Path(source_file).read_text()
    text = create_output(doc)
    Path(destination_file).write_text(text, encoding="utf-8")
    return doc, text


if __name__ == "__main__":
    doc, text = main(source_file="_README.md", destination_file="README.md")
    lines = to_list(doc)
    print(count_tweets(lines))
    