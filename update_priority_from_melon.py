#!/usr/bin/env python3
"""
Recalculate `priority` from Melon metrics.

Priority basis:
1) Melon digital metrics (streaming + download) if detectable
2) Fallback to Melon like count (album like, then sum of song likes)

Writes (if missing) these columns:
- MelonPriorityStream
- MelonPriorityDownload
- MelonPriorityLike
- PriorityMetricSource
- PriorityMetricValue
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


SEARCH_URL = "https://www.melon.com/search/total/index.htm?q={query}"
ALBUM_DETAIL_URL = "https://www.melon.com/album/detail.htm?albumId={album_id}"
SONG_DETAIL_URL = "https://www.melon.com/song/detail.htm?songId={song_id}"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def compact(text: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", normalize(text))


def parse_int(text: str) -> int:
    if text is None:
        return 0
    m = re.findall(r"\d[\d,]*", str(text))
    if not m:
        return 0
    try:
        return int(m[0].replace(",", ""))
    except Exception:
        return 0


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


@dataclass
class AlbumMetric:
    album_id: str = ""
    stream: int = 0
    download: int = 0
    like: int = 0
    metric_source: str = "unavailable"
    metric_value: int = 0


class MelonPriorityClient:
    def __init__(self, sleep_seconds: float = 0.25, timeout: int = 15):
        self.sleep_seconds = sleep_seconds
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )
        self.album_like_cache: Dict[str, int] = {}
        self.song_like_cache: Dict[str, int] = {}
        self.song_digital_cache: Dict[str, Tuple[int, int]] = {}
        self.album_song_ids_cache: Dict[str, List[str]] = {}
        self.search_album_cache: Dict[Tuple[str, str], str] = {}

    def _get(self, url: str) -> str:
        time.sleep(self.sleep_seconds)
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.text

    def _score_candidate(self, q_artist: str, q_album: str, c_artist: str, c_album: str) -> int:
        qa, qal = compact(q_artist), compact(q_album)
        ca, cal = compact(c_artist), compact(c_album)
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

        q_tokens = set(normalize(q_album).split())
        c_tokens = set(normalize(c_album).split())
        score += len(q_tokens & c_tokens)
        return score

    def find_album_id(self, artist: str, album: str) -> str:
        key = (normalize(artist), normalize(album))
        if key in self.search_album_cache:
            return self.search_album_cache[key]

        if not key[0] or not key[1]:
            self.search_album_cache[key] = ""
            return ""

        try:
            html = self._get(SEARCH_URL.format(query=quote_plus(f"{artist} {album}")))
            soup = BeautifulSoup(html, "html.parser")
            section = soup.select_one("div.d_album_list") or soup

            candidates = []
            for a in section.select("a[href*='goAlbumDetail']"):
                href = a.get("href", "")
                m = re.search(r"goAlbumDetail\('([0-9]+)'\)", href)
                if not m:
                    continue
                album_id = m.group(1)
                cand_album = a.get_text(" ", strip=True)
                if not cand_album:
                    continue

                cand_artist = ""
                li = a.find_parent("li")
                if li:
                    artist_a = li.select_one("a[href*='goArtistDetail']")
                    if artist_a:
                        cand_artist = artist_a.get_text(" ", strip=True)

                score = self._score_candidate(artist, album, cand_artist, cand_album)
                candidates.append((score, album_id))

            if not candidates:
                # fallback scan
                m = re.search(r"goAlbumDetail\('([0-9]+)'\)", html)
                if m:
                    self.search_album_cache[key] = m.group(1)
                    return m.group(1)
                self.search_album_cache[key] = ""
                return ""

            candidates.sort(key=lambda x: x[0], reverse=True)
            best = candidates[0][1]
            self.search_album_cache[key] = best
            return best
        except Exception:
            self.search_album_cache[key] = ""
            return ""

    def get_album_like(self, album_id: str) -> int:
        if not album_id:
            return 0
        if album_id in self.album_like_cache:
            return self.album_like_cache[album_id]

        try:
            url = f"https://www.melon.com/commonlike/getAlbumLike.json?contsIds={album_id}"
            time.sleep(self.sleep_seconds)
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            conts = (data or {}).get("contsLike") or []
            like = parse_int(conts[0].get("SUMMCNT")) if conts else 0
            self.album_like_cache[album_id] = like
            return like
        except Exception:
            self.album_like_cache[album_id] = 0
            return 0

    def get_song_like(self, song_id: str) -> int:
        if not song_id:
            return 0
        if song_id in self.song_like_cache:
            return self.song_like_cache[song_id]

        try:
            url = f"https://www.melon.com/commonlike/getSongLike.json?contsIds={song_id}"
            time.sleep(self.sleep_seconds)
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            conts = (data or {}).get("contsLike") or []
            like = parse_int(conts[0].get("SUMMCNT")) if conts else 0
            self.song_like_cache[song_id] = like
            return like
        except Exception:
            self.song_like_cache[song_id] = 0
            return 0

    def get_album_song_ids(self, album_id: str) -> List[str]:
        if not album_id:
            return []
        if album_id in self.album_song_ids_cache:
            return self.album_song_ids_cache[album_id]

        try:
            html = self._get(ALBUM_DETAIL_URL.format(album_id=album_id))
            ids = set(re.findall(r"goSongDetail\('([0-9]+)'\)", html))
            ids.update(re.findall(r"playSong\('\\d+','([0-9]+)'\)", html))
            ordered = sorted(ids)
            self.album_song_ids_cache[album_id] = ordered
            return ordered
        except Exception:
            self.album_song_ids_cache[album_id] = []
            return []

    def get_song_digital(self, song_id: str) -> Tuple[int, int]:
        if not song_id:
            return (0, 0)
        if song_id in self.song_digital_cache:
            return self.song_digital_cache[song_id]

        stream = 0
        download = 0
        try:
            html = self._get(SONG_DETAIL_URL.format(song_id=song_id))
            soup = BeautifulSoup(html, "html.parser")

            # structured dt/dd parsing if present
            for dt in soup.select("div.section_info div.meta dl.list dt"):
                label = dt.get_text(" ", strip=True)
                dd = dt.find_next_sibling("dd")
                if not dd:
                    continue
                value = dd.get_text(" ", strip=True)
                if "스트리밍" in label:
                    stream = max(stream, parse_int(value))
                if "다운로드" in label:
                    download = max(download, parse_int(value))

            # regex fallback
            if stream == 0:
                m = re.search(r"(?:누적\s*)?스트리밍[^0-9]{0,40}([0-9][0-9,]{2,})", html)
                if m:
                    stream = parse_int(m.group(1))
            if download == 0:
                m = re.search(r"(?:누적\s*)?다운로드[^0-9]{0,40}([0-9][0-9,]{2,})", html)
                if m:
                    download = parse_int(m.group(1))
        except Exception:
            pass

        self.song_digital_cache[song_id] = (stream, download)
        return (stream, download)

    def get_album_metric(self, album_id: str) -> AlbumMetric:
        if not album_id:
            return AlbumMetric(album_id="", metric_source="unavailable", metric_value=0)

        song_ids = self.get_album_song_ids(album_id)
        stream_total = 0
        download_total = 0
        song_like_total = 0

        for sid in song_ids:
            s, d = self.get_song_digital(sid)
            stream_total += s
            download_total += d
            if s == 0 and d == 0:
                # we can still collect likes for fallback quality
                song_like_total += self.get_song_like(sid)

        album_like = self.get_album_like(album_id)

        if stream_total > 0 or download_total > 0:
            metric_value = stream_total + download_total
            source = "melon_digital"
            like_value = album_like if album_like > 0 else song_like_total
        elif album_like > 0:
            metric_value = album_like
            source = "melon_like_album"
            like_value = album_like
        elif song_like_total > 0:
            metric_value = song_like_total
            source = "melon_like_song_sum"
            like_value = song_like_total
        else:
            metric_value = 0
            source = "unavailable"
            like_value = 0

        return AlbumMetric(
            album_id=album_id,
            stream=stream_total,
            download=download_total,
            like=like_value,
            metric_source=source,
            metric_value=metric_value,
        )


def compute_priority(metric_value: int, min_log: float, max_log: float) -> int:
    if metric_value <= 0:
        return 1
    lv = math.log10(metric_value + 1)
    if max_log <= min_log:
        return 5
    score = 1 + round(9 * ((lv - min_log) / (max_log - min_log)))
    return clamp(score, 1, 10)


def update_priorities(input_csv: Path, output_csv: Path, sleep_seconds: float = 0.25) -> None:
    with input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    required = [
        "MelonPriorityStream",
        "MelonPriorityDownload",
        "MelonPriorityLike",
        "PriorityMetricSource",
        "PriorityMetricValue",
    ]
    for col in required:
        if col not in fieldnames:
            fieldnames.append(col)

    client = MelonPriorityClient(sleep_seconds=sleep_seconds)

    album_keys: List[Tuple[str, str]] = []
    seen = set()
    for r in rows:
        artist = (r.get("Artist") or "").strip()
        album = (r.get("Album") or "").strip()
        if not artist or not album:
            continue
        key = (normalize(artist), normalize(album))
        if key in seen:
            continue
        seen.add(key)
        album_keys.append(key)

    album_metrics: Dict[Tuple[str, str], AlbumMetric] = {}

    for idx, key in enumerate(album_keys, start=1):
        artist_n, album_n = key
        # recover original case text for search quality
        sample = next(r for r in rows if normalize(r.get("Artist", "")) == artist_n and normalize(r.get("Album", "")) == album_n)
        artist = (sample.get("Artist") or "").strip()
        album = (sample.get("Album") or "").strip()

        album_id = (sample.get("MelonAlbumId") or "").strip()
        if not album_id:
            album_id = client.find_album_id(artist, album)

        metric = client.get_album_metric(album_id) if album_id else AlbumMetric(album_id="", metric_source="unavailable", metric_value=0)
        album_metrics[key] = metric

        print(
            f"[{idx}/{len(album_keys)}] {artist} | {album} -> "
            f"source={metric.metric_source}, metric={metric.metric_value}, stream={metric.stream}, dl={metric.download}, like={metric.like}, albumId={metric.album_id}"
        )

    positive = [m.metric_value for m in album_metrics.values() if m.metric_value > 0]
    if positive:
        logs = [math.log10(v + 1) for v in positive]
        min_log, max_log = min(logs), max(logs)
    else:
        min_log, max_log = 0.0, 0.0

    for r in rows:
        key = (normalize(r.get("Artist", "")), normalize(r.get("Album", "")))
        metric = album_metrics.get(key, AlbumMetric())

        pr = compute_priority(metric.metric_value, min_log, max_log)
        r["priority"] = str(pr)
        r["MelonPriorityStream"] = str(metric.stream)
        r["MelonPriorityDownload"] = str(metric.download)
        r["MelonPriorityLike"] = str(metric.like)
        r["PriorityMetricSource"] = metric.metric_source
        r["PriorityMetricValue"] = str(metric.metric_value)

        if metric.album_id and not (r.get("MelonAlbumId") or "").strip():
            r["MelonAlbumId"] = metric.album_id
            r["MelonAlbumURL"] = ALBUM_DETAIL_URL.format(album_id=metric.album_id)

    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved: {output_csv}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update priority from Melon digital/like metrics")
    parser.add_argument("--input", default="Portfolio_list.csv")
    parser.add_argument("--output", default="Portfolio_list.csv")
    parser.add_argument("--sleep", type=float, default=0.25)
    args = parser.parse_args()

    update_priorities(Path(args.input), Path(args.output), sleep_seconds=args.sleep)


if __name__ == "__main__":
    main()
