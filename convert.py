from dataclasses import dataclass
from pathlib import Path

import md_toc  # type: ignore
import requests

URL = "https://twitter.com/{name}/status/{id}"
API = "https://publish.twitter.com/oembed?url={url}"


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
        return API.format(url=self.url)

    def html(self):
        return requests.get(self.api_url).json()["html"]

    def _repr_html_(self):
        return self.html()


def mk_tweet(s: str) -> Tweet:
    a = s.strip().split("/")
    ix = a.index("status")
    return Tweet(a[ix - 1], int(a[ix + 1]))


def to_list(doc: str):
    return doc.split("\n")


def substitute_tweets(line: str) -> str:
    if line.startswith("http") and ("status" in line):
        return mk_tweet(line).html()
    else:
        return line


def main(source_file="_README.md", destination_file="README.md"):
    doc = Path(source_file).read_text()
    toc = md_toc.build_toc(source_file)
    lines = [toc] + to_list(doc)
    lines = list(map(substitute_tweets, lines))
    text = "\n".join(lines)
    Path(destination_file).write_text(text, encoding="utf-8")
    return lines


if __name__ == "__main__":
    main()
