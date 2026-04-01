#!/usr/bin/env python3
"""
Enrich Portfolio_list.csv with Melon album metadata.

- Finds Melon album page by artist+album query
- Extracts cover image and genre from album detail page
- Writes columns:
  - GenreMelon
  - CoverImageURL
  - MelonAlbumId
  - MelonAlbumURL
  - MelonReleaseDate
  - MelonLookupStatus

Optionally fills empty Genre with GenreMelon.
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


SEARCH_URL = "https://www.melon.com/search/total/index.htm?q={query}"
ALBUM_DETAIL_URL = "https://www.melon.com/album/detail.htm?albumId={album_id}"
HTML_PARSER = "html.parser"

try:
    import lxml  # noqa: F401
    HTML_PARSER = "lxml"
except Exception:
    HTML_PARSER = "html.parser"


def normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def compact(text: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", normalize(text))


def score_candidate(query_artist: str, query_album: str, cand_artist: str, cand_album: str) -> int:
    qa = compact(query_artist)
    qal = compact(query_album)
    ca = compact(cand_artist)
    cal = compact(cand_album)

    score = 0
    if qal and cal == qal:
        score += 12
    elif qal and qal in cal:
        score += 8
    elif qal and cal in qal:
        score += 4

    if qa and ca == qa:
        score += 8
    elif qa and qa in ca:
        score += 4

    # Shared token overlap can salvage minor spacing/punctuation differences.
    q_tokens = set(normalize(query_album).split())
    c_tokens = set(normalize(cand_album).split())
    if q_tokens and c_tokens:
        overlap = len(q_tokens & c_tokens)
        score += overlap

    return score


@dataclass
class MelonAlbumMeta:
    album_id: str = ""
    album_url: str = ""
    cover_url: str = ""
    genre: str = ""
    release_date: str = ""
    status: str = "not_found"


class MelonClient:
    def __init__(self, sleep_seconds: float = 0.45, timeout: int = 15):
        self.sleep_seconds = sleep_seconds
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.7,en;q=0.6",
            }
        )

    def _get(self, url: str) -> requests.Response:
        time.sleep(self.sleep_seconds)
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def find_album_id(self, artist: str, album: str) -> Tuple[str, str, str]:
        query = " ".join(part for part in [artist, album] if part).strip()
        if not query:
            return "", "", ""

        url = SEARCH_URL.format(query=quote_plus(query))
        html = self._get(url).text
        soup = BeautifulSoup(html, HTML_PARSER)

        # Prefer explicit album list area.
        section = soup.select_one("div.d_album_list") or soup

        candidates: List[Tuple[int, str, str, str]] = []
        for a in section.select("a[href*='goAlbumDetail']"):
            href = a.get("href", "")
            m = re.search(r"goAlbumDetail\('([0-9]+)'\)", href)
            if not m:
                continue
            album_id = m.group(1)

            cand_album = a.get_text(" ", strip=True)
            if not cand_album:
                continue

            # Try to infer artist from nearby container.
            cand_artist = ""
            li = a.find_parent("li")
            if li:
                artist_a = li.select_one("a[href*='goArtistDetail']")
                if artist_a:
                    cand_artist = artist_a.get_text(" ", strip=True)

            s = score_candidate(artist, album, cand_artist, cand_album)
            candidates.append((s, album_id, cand_album, cand_artist))

        if not candidates:
            # Fallback: search whole page for goAlbumDetail in song result rows.
            for m in re.finditer(r"goAlbumDetail\('([0-9]+)'\)", html):
                album_id = m.group(1)
                candidates.append((0, album_id, "", ""))

        if not candidates:
            return "", "", ""

        candidates.sort(key=lambda x: x[0], reverse=True)
        _, best_id, best_album, best_artist = candidates[0]
        return best_id, best_album, best_artist

    def fetch_album_meta(self, album_id: str) -> MelonAlbumMeta:
        if not album_id:
            return MelonAlbumMeta(status="not_found")

        url = ALBUM_DETAIL_URL.format(album_id=album_id)
        try:
            html = self._get(url).text
            soup = BeautifulSoup(html, HTML_PARSER)

            cover_url = ""
            og_image = soup.select_one("meta[property='og:image']")
            if og_image:
                cover_url = (og_image.get("content") or "").strip()

            genre = ""
            release_date = ""
            for dt in soup.select("div.meta dl.list dt"):
                label = dt.get_text(" ", strip=True)
                dd = dt.find_next_sibling("dd")
                if not dd:
                    continue
                value = dd.get_text(" ", strip=True)
                if label == "장르":
                    genre = value
                elif label == "발매일":
                    release_date = value

            return MelonAlbumMeta(
                album_id=album_id,
                album_url=url,
                cover_url=cover_url,
                genre=genre,
                release_date=release_date,
                status="found" if (genre or cover_url) else "partial",
            )
        except Exception:
            return MelonAlbumMeta(album_id=album_id, album_url=url, status="error")


def enrich_csv(
    input_path: Path,
    output_path: Path,
    fill_empty_genre: bool,
    sleep_seconds: float,
    limit_albums: int,
) -> None:
    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    added_fields = [
        "GenreMelon",
        "CoverImageURL",
        "MelonAlbumId",
        "MelonAlbumURL",
        "MelonReleaseDate",
        "MelonLookupStatus",
    ]
    for col in added_fields:
        if col not in fieldnames:
            fieldnames.append(col)

    client = MelonClient(sleep_seconds=sleep_seconds)
    cache: Dict[Tuple[str, str], MelonAlbumMeta] = {}

    unique_keys = []
    seen = set()
    for row in rows:
        key = (normalize(row.get("Artist", "")), normalize(row.get("Album", "")))
        if not key[0] or not key[1] or key in seen:
            continue
        seen.add(key)
        unique_keys.append(key)

    if limit_albums > 0:
        unique_keys = unique_keys[:limit_albums]

    print(f"Target unique albums: {len(unique_keys)}")

    for idx, (artist_n, album_n) in enumerate(unique_keys, start=1):
        artist = artist_n.strip()
        album = album_n.strip()
        try:
            album_id, _, _ = client.find_album_id(artist, album)
            meta = client.fetch_album_meta(album_id)
            cache[(artist_n, album_n)] = meta
            print(f"[{idx}/{len(unique_keys)}] {artist} | {album} -> {meta.status} ({meta.album_id})")
        except Exception:
            cache[(artist_n, album_n)] = MelonAlbumMeta(status="error")
            print(f"[{idx}/{len(unique_keys)}] {artist} | {album} -> error")

    for row in rows:
        key = (normalize(row.get("Artist", "")), normalize(row.get("Album", "")))
        meta = cache.get(key)
        if not meta:
            # Not processed because of limit or empty key
            row.setdefault("MelonLookupStatus", "skipped")
            continue

        row["GenreMelon"] = meta.genre
        row["CoverImageURL"] = meta.cover_url
        row["MelonAlbumId"] = meta.album_id
        row["MelonAlbumURL"] = meta.album_url
        row["MelonReleaseDate"] = meta.release_date
        row["MelonLookupStatus"] = meta.status

        if fill_empty_genre and not (row.get("Genre") or "").strip() and meta.genre:
            row["Genre"] = meta.genre

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich portfolio CSV from Melon metadata")
    parser.add_argument("--input", default="Portfolio_list.csv", help="Input CSV path")
    parser.add_argument("--output", default="Portfolio_list_with_melon.csv", help="Output CSV path")
    parser.add_argument("--fill-genre-empty", action="store_true", help="Fill empty Genre with GenreMelon")
    parser.add_argument("--sleep", type=float, default=0.45, help="Sleep between requests (seconds)")
    parser.add_argument("--limit-albums", type=int, default=0, help="Limit unique album lookups for testing")
    args = parser.parse_args()

    enrich_csv(
        input_path=Path(args.input),
        output_path=Path(args.output),
        fill_empty_genre=args.fill_genre_empty,
        sleep_seconds=args.sleep,
        limit_albums=args.limit_albums,
    )


if __name__ == "__main__":
    main()
