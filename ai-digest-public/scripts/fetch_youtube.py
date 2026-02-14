#!/usr/bin/env python3
"""Fetch recent videos from YouTube channels using yt-dlp."""

import argparse
import json
import subprocess
import sys


def fetch_channel(handle: str, name: str, max_videos: int) -> list[dict]:
    """Fetch recent videos from a single channel via yt-dlp."""
    url = f"https://www.youtube.com/@{handle}/videos"
    try:
        result = subprocess.run(
            [
                "yt-dlp", "--flat-playlist", "--dump-json",
                "--playlist-end", str(max_videos),
                url,
            ],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as e:
        print(f"Warning: Failed to fetch {name}: {e}", file=sys.stderr)
        return []

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        videos.append({
            "channel": name,
            "title": d.get("title", "Untitled"),
            "video_id": d.get("id", ""),
            "url": d.get("url", ""),
            "description": (d.get("description") or "")[:500],
        })
    return videos


def main():
    parser = argparse.ArgumentParser(description="Fetch recent YouTube videos")
    parser.add_argument(
        "--channels", type=str, required=True,
        help='JSON array of {"handle": "...", "name": "..."} objects',
    )
    parser.add_argument(
        "--max-videos", type=int, default=5,
        help="Max videos per channel (default: 5)",
    )
    args = parser.parse_args()

    channels = json.loads(args.channels)
    all_videos = []
    for ch in channels:
        videos = fetch_channel(ch["handle"], ch["name"], args.max_videos)
        all_videos.extend(videos)

    print(json.dumps(all_videos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
