#!/usr/bin/env python3
"""
Build media matches for Portfolio_list.csv.

Outputs:
  - portfolio_media_map.json
"""

import csv
import json
import os
import re
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
MELON_CSV_PATH = ROOT / "Portfolio_list_with_melon.csv"
YTDLP_PATH = Path.home() / "Library" / "Python" / "3.9" / "bin" / "yt-dlp"
ENABLE_YT_SEARCH = os.getenv("ENABLE_YT_SEARCH", "").strip().lower() in {"1", "true", "yes"}
MANUAL_ALBUM_COVER_OVERRIDES = {
    "잔나비|구여친클럽 ost": "https://is1-ssl.mzstatic.com/image/thumb/Music7/v4/7a/e8/3e/7ae83e8c-c5c1-5ac1-f674-226026046b43/JA.jpg/600x600bb.jpg",
    "잔나비|두번째 스무살 ost": "https://is1-ssl.mzstatic.com/image/thumb/Music6/v4/bb/76/d4/bb76d4b0-8c3a-6096-5f28-b54874452e58/jancover.jpg/600x600bb.jpg",
    "잔나비|디어 마이 프렌즈 ost": "https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/65/f8/46/65f8464c-1c2a-0bb9-67ad-173869873bd2/20165201516391.jpg/600x600bb.jpg",
    "잔나비|혼술남녀 ost": "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/9c/a3/c6/9ca3c65d-7a6a-682d-b05a-452ea772b2a1/8809484118353_Cover.jpg/1200x630wp-60.jpg",
    "잔나비|she": "https://is1-ssl.mzstatic.com/image/thumb/Music118/v4/4b/8c/0f/4b8c0f1e-472e-732b-8dd8-f4a690ef95db/cover-_DS.jpg/1200x630wp-60.jpg",
}


def normalize(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def make_key(artist: str, album: str, title: str) -> str:
    return f"{normalize(artist)}|{normalize(album)}|{normalize(title)}"


def is_youtube_url(value: str) -> bool:
    return bool(re.match(r"^https?://(?:www\.)?(?:youtu\.be|youtube\.com)/", (value or "").strip(), re.IGNORECASE))


def extract_youtube_id(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    short = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", text, re.IGNORECASE)
    if short:
        return short.group(1)
    watch = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", text, re.IGNORECASE)
    if watch:
        return watch.group(1)
    embed = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]{11})", text, re.IGNORECASE)
    if embed:
        return embed.group(1)
    return ""


def to_canonical_youtube_url(value: str) -> str:
    video_id = extract_youtube_id(value)
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""


def make_album_key(artist: str, album: str) -> str:
    return f"{normalize(artist)}|{normalize(album)}"


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


def load_existing_media() -> Dict[str, Dict[str, str]]:
    if not OUTPUT_PATH.exists():
        return {}
    try:
        payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    items = payload.get("items") or []
    return {item.get("key", ""): item for item in items if item.get("key")}


def load_melon_album_fallbacks() -> Dict[str, Dict[str, str]]:
    if not MELON_CSV_PATH.exists():
        return {}
    with MELON_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fallbacks = {}
        for raw in reader:
            artist = (raw.get("Artist") or "").strip()
            album = (raw.get("Album") or "").strip()
            if not artist or not album:
                continue
            album_key = make_album_key(artist, album)
            current = fallbacks.get(album_key, {})
            cover = (raw.get("CoverImageURL") or "").strip()
            youtube_url = to_canonical_youtube_url((raw.get("YoutubeURL") or "").strip())
            if cover and not current.get("cover_url"):
                current["cover_url"] = cover
            if youtube_url and not current.get("youtube_url"):
                current["youtube_url"] = youtube_url
            fallbacks[album_key] = current
    return fallbacks


def run_yt_search(query: str) -> Dict[str, str]:
    if not ENABLE_YT_SEARCH:
        return {}
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


def fetch_youtube_oembed(youtube_url: str) -> Dict[str, str]:
    canonical = to_canonical_youtube_url(youtube_url)
    if not canonical:
        return {}
    try:
        url = f"https://www.youtube.com/oembed?format=json&url={quote_plus(canonical)}"
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return {}
        data = resp.json()
        video_id = extract_youtube_id(canonical)
        return {
            "youtube_id": video_id,
            "youtube_title": data.get("title") or "",
            "youtube_url": canonical,
            "youtube_thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
        }
    except Exception:
        return {}


def run_cover_search(artist: str, album: str, title: str) -> str:
    title_term = (title or "").split(",")[0].strip()
    if is_youtube_url(title_term):
        title_term = ""
    terms = [f"{artist} {album}", f"{artist} {title_term}", f"{artist} {album} {title_term}", f"{artist}"]
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    for term in terms:
        term = " ".join(term.split())
        if not term:
            continue
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
    existing_by_key = load_existing_media()
    melon_by_album = load_melon_album_fallbacks()
    existing_album_cache: Dict[str, Dict[str, str]] = {}
    cover_cache: Dict[str, str] = {}
    youtube_cache: Dict[str, Dict[str, str]] = {}

    for item in existing_by_key.values():
        album_key = make_album_key(item.get("artist", ""), item.get("album", ""))
        if not album_key:
            continue
        cached = existing_album_cache.setdefault(album_key, {})
        if item.get("cover_url") and not cached.get("cover_url"):
            cached["cover_url"] = item["cover_url"]
        if item.get("youtube_url") and not cached.get("youtube_url"):
            cached["youtube_url"] = item["youtube_url"]
        if item.get("youtube_thumbnail") and not cached.get("youtube_thumbnail"):
            cached["youtube_thumbnail"] = item["youtube_thumbnail"]

    rows: List[MediaMatch] = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            artist = (raw.get("Artist") or "").strip()
            album = (raw.get("Album") or "").strip()
            title = (raw.get("Title") or "").strip()
            youtube_url = (raw.get("YoutubeURL") or raw.get("YouTubeURL") or raw.get("youtube_url") or "").strip()
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
            album_key = make_album_key(artist, album)
            exact_existing = existing_by_key.get(item.key, {})
            album_existing = existing_album_cache.get(album_key, {})
            melon_fallback = melon_by_album.get(album_key, {})

            source_url = youtube_url or (title if is_youtube_url(title) else "")
            yt = {}
            if exact_existing.get("youtube_id") or exact_existing.get("youtube_url"):
                yt = {
                    "youtube_id": exact_existing.get("youtube_id", ""),
                    "youtube_title": exact_existing.get("youtube_title", ""),
                    "youtube_url": exact_existing.get("youtube_url", ""),
                    "youtube_thumbnail": exact_existing.get("youtube_thumbnail", ""),
                }
            elif source_url:
                canonical_source = to_canonical_youtube_url(source_url)
                if canonical_source in youtube_cache:
                    yt = youtube_cache[canonical_source]
                else:
                    yt = fetch_youtube_oembed(source_url)
                    youtube_cache[canonical_source] = yt
            elif album_existing.get("youtube_url"):
                yt = {
                    "youtube_id": extract_youtube_id(album_existing.get("youtube_url", "")),
                    "youtube_title": album_existing.get("youtube_title", ""),
                    "youtube_url": album_existing.get("youtube_url", ""),
                    "youtube_thumbnail": album_existing.get("youtube_thumbnail", ""),
                }
            elif melon_fallback.get("youtube_url"):
                yt_url = melon_fallback["youtube_url"]
                yt = {
                    "youtube_id": extract_youtube_id(yt_url),
                    "youtube_title": "",
                    "youtube_url": yt_url,
                    "youtube_thumbnail": f"https://img.youtube.com/vi/{extract_youtube_id(yt_url)}/hqdefault.jpg" if extract_youtube_id(yt_url) else "",
                }

            if not yt:
                query_parts = [artist]
                if title and not is_youtube_url(title):
                    query_parts.append(title.split(",")[0].strip())
                elif album:
                    query_parts.append(album)
                query = " ".join(part for part in query_parts if part)
                yt = run_yt_search(query)

            item.youtube_id = yt.get("youtube_id", "")
            item.youtube_title = yt.get("youtube_title", "")
            item.youtube_url = yt.get("youtube_url", "")
            item.youtube_thumbnail = yt.get("youtube_thumbnail", "")
            if exact_existing.get("cover_url"):
                item.cover_url = exact_existing["cover_url"]
            elif MANUAL_ALBUM_COVER_OVERRIDES.get(album_key):
                item.cover_url = MANUAL_ALBUM_COVER_OVERRIDES[album_key]
            elif melon_fallback.get("cover_url"):
                item.cover_url = melon_fallback["cover_url"]
            elif album_existing.get("cover_url"):
                item.cover_url = album_existing["cover_url"]
            else:
                cached_cover = cover_cache.get(album_key)
                if cached_cover is None:
                    cached_cover = run_cover_search(artist, album, title)
                    cover_cache[album_key] = cached_cover
                item.cover_url = cached_cover or ""

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
