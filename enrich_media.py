#!/usr/bin/env python3
"""
Build media matches for Portfolio_list.csv.

Outputs:
  - portfolio_media_map.json
"""

import csv
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import requests


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "Portfolio_list.csv"
OUTPUT_PATH = ROOT / "portfolio_media_map.json"
YTDLP_PATH = Path.home() / "Library" / "Python" / "3.9" / "bin" / "yt-dlp"


def normalize(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def make_key(artist: str, album: str, title: str) -> str:
    return f"{normalize(artist)}|{normalize(album)}|{normalize(title)}"


@dataclass
class MediaMatch:
    artist: str
    album: str
    title: str
    work: str
    note: str
    key: str
    youtube_id: str = ""
    youtube_title: str = ""
    youtube_url: str = ""
    youtube_thumbnail: str = ""
    cover_url: str = ""


def run_yt_search(query: str) -> Dict[str, str]:
    if not YTDLP_PATH.exists():
        return {}

    try:
        cmd = [
            str(YTDLP_PATH),
            "--no-warnings",
            "--skip-download",
            "--dump-json",
            f"ytsearch1:{query}",
        ]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)
        if result.returncode != 0 or not result.stdout.strip():
            return {}

        first = json.loads(result.stdout.splitlines()[0])
        video_id = first.get("id") or ""
        if not video_id:
            return {}

        thumbnails = first.get("thumbnails") or []
        thumb = ""
        if thumbnails:
            thumb = thumbnails[-1].get("url") or thumbnails[0].get("url") or ""

        return {
            "youtube_id": video_id,
            "youtube_title": first.get("title") or "",
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "youtube_thumbnail": thumb or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        }
    except Exception:
        return {}


def run_cover_search(artist: str, album: str, title: str) -> str:
    terms = [f"{artist} {album}", f"{artist} {title}", f"{artist}"]
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    for term in terms:
        try:
            url = f"https://itunes.apple.com/search?term={quote_plus(term)}&entity=album,song&country=KR&limit=5"
            resp = session.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue
            data = resp.json()
            results = data.get("results") or []
            for item in results:
                artwork = item.get("artworkUrl100") or item.get("artworkUrl60")
                if artwork:
                    return artwork.replace("100x100bb", "600x600bb").replace("60x60bb", "600x600bb")
        except Exception:
            continue
    return ""


def build_matches() -> List[MediaMatch]:
    rows: List[MediaMatch] = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            artist = (raw.get("Artist") or "").strip()
            album = (raw.get("Album") or "").strip()
            title = (raw.get("Title") or "").strip()
            work = (raw.get("Work") or "").strip()
            note = (raw.get("note") or "").strip()
            if not artist:
                continue

            item = MediaMatch(
                artist=artist,
                album=album,
                title=title,
                work=work,
                note=note,
                key=make_key(artist, album, title),
            )

            query_parts = [artist]
            if title:
                query_parts.append(title.split(",")[0].strip())
            elif album:
                query_parts.append(album)
            query = " ".join(part for part in query_parts if part)

            yt = run_yt_search(query)
            item.youtube_id = yt.get("youtube_id", "")
            item.youtube_title = yt.get("youtube_title", "")
            item.youtube_url = yt.get("youtube_url", "")
            item.youtube_thumbnail = yt.get("youtube_thumbnail", "")
            item.cover_url = run_cover_search(artist, album, title)

            rows.append(item)
            print(f"Matched: {artist} | {title or '(no title)'}")
    return rows


def main() -> None:
    matches = build_matches()
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(matches),
        "items": [asdict(m) for m in matches],
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

