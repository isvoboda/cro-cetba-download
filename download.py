#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from pathlib import Path
from typing import Optional

import click
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

RE_FILE_URL = re.compile("(?P<file_url>^.*mp3)")


@click.command()
@click.option("--url", required=True, type=str)
@click.option("--destination", "--dest", required=False, type=str, default=None)
def download(url: str, destination: Optional[str] = None):
    page = requests.get(url)
    soup = BeautifulSoup(markup=page.content, features="html.parser")

    tags = soup.findAll(name="div", attrs={"id": re.compile("^file-\d+")})

    for ith, tag in enumerate(tqdm(tags, leave=False, position=1)):
        href_tag = tag.find_all(name="a", attrs={"href": re.compile("^.*mp3")})[0]
        title = tag.find_all(name="div", attrs={"class": "filename"})[0]

        file_url = RE_FILE_URL.match(href_tag["href"]).group("file_url")

        file_name = f"{ith:02} {title['title']}.mp3"
        # file_name = re.sub(' +',' ',file_name)
        file_name_norm = "".join(char if char.isalnum() else "-" for char in file_name)
        path = Path(file_name_norm)

        if destination is not None:
            path = Path(destination) / path
            path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(file_url, stream=True)
        total_size_mb = int(response.headers.get("content-length", 0)) / (1024 ** 2)
        block_size = 1024

        progress_bar = tqdm(
            total=total_size_mb, unit="iMB", unit_scale=True, position=2
        )

        with open(path, "wb") as wfd:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data) / (1024 ** 2))
                wfd.write(data)


if __name__ == "__main__":
    download()
