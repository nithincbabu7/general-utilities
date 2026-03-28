import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

import yt_dlp


def sanitize_filename(title: str) -> str:
    title = re.sub(r'[<>:"/\\|?*]', '_', title)
    title = title.strip('. ')
    return title or "untitled"


def normalize_url(line: str) -> str:
    if '/' in line:
        return line
    return f"https://www.youtube.com/watch?v={line}"


def get_title(url: str) -> str:
    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['title']


def download_stream(url: str, fmt: str, out_tmpl: str) -> str:
    opts = {
        'format': fmt,
        'outtmpl': out_tmpl,
        'quiet': False,
        'no_warnings': False,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    matches = glob.glob(out_tmpl.replace('%(ext)s', '*'))
    if not matches:
        raise FileNotFoundError(f"Downloaded file not found for template: {out_tmpl}")
    return matches[0]


def encode(video_path: str, audio_path: str, output_path: str) -> None:
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-crf', '18',
        '-preset', 'slow',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-movflags', '+faststart',
        '-y',
        output_path,
    ]
    subprocess.run(cmd, check=True)


def process_video(url: str, video_id: str, output_dir: str) -> None:
    print(f"\n[{video_id}] Fetching metadata...")
    title = get_title(url)
    safe_title = sanitize_filename(title)
    output_path = os.path.join(output_dir, f"{safe_title}.mp4")

    if os.path.exists(output_path):
        print(f"[{video_id}] Skipping — already exists: {output_path}")
        return

    print(f"[{video_id}] Title: {title}")
    tmp_dir = os.path.join('temp', video_id)
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        print(f"[{video_id}] Downloading video stream...")
        video_file = download_stream(url, 'bestvideo', os.path.join(tmp_dir, 'video.%(ext)s'))

        print(f"[{video_id}] Downloading audio stream...")
        audio_file = download_stream(url, 'bestaudio', os.path.join(tmp_dir, 'audio.%(ext)s'))

        print(f"[{video_id}] Encoding -> {output_path}")
        encode(video_file, audio_file, output_path)
        print(f"[{video_id}] Done: {output_path}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Download YouTube videos and encode to H.264/AAC MP4.'
    )
    parser.add_argument('--links_file', default='links.txt',
                        help='Text file with YouTube video IDs or URLs (one per line)')
    parser.add_argument('--output_dir', default='downloads',
                        help='Directory to save output MP4 files')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.links_file, encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

    if not lines:
        print("No video IDs found in links file.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(lines)} video(s) to process.")
    errors = []

    for line in lines:
        url = normalize_url(line)
        video_id = line.split('v=')[-1].split('&')[0] if 'v=' in line else line
        try:
            process_video(url, video_id, args.output_dir)
        except Exception as e:
            print(f"[{video_id}] ERROR: {e}", file=sys.stderr)
            errors.append((video_id, str(e)))

    if errors:
        print(f"\n{len(errors)} video(s) failed:")
        for vid_id, msg in errors:
            print(f"  {vid_id}: {msg}")
        sys.exit(1)


if __name__ == '__main__':
    main()
