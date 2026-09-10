"""Prepare web copies without changing original videos; requires imageio-ffmpeg and Pillow."""
from pathlib import Path
import subprocess
import argparse
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / '视频demo'
DEST = ROOT / 'public/assets'
ITEMS = [
 ('触觉 SmolVLA-触觉成功.mp4', 'tactile', 20, False),
 ('触觉 SmolVLA-无触觉失败.mp4', 'vision', 16, False),
 ('触觉 SmolVLA-抗干扰能力.mp4', 'perturbation', 26, False),
 ('拧灯泡.mp4', 'bulb', 16.8, False),
 ('拧螺母.mp4', 'nut', 35, True),
 ('双臂双手遥操作系统.mp4', 'teleop', 40, True),
]

# The full head movement remains inside this background region in all 550 frames.
# 6 × 6 blocks deliberately remove facial detail; the bulb/contact area stays visible.
BULB_PRIVACY_FILTER = '[0:v]split[base][face];[face]crop=300:320:940:0,scale=6:6:flags=area,scale=300:320:flags=neighbor[mask];[base][mask]overlay=940:0[v]'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', choices=[item[1] for item in ITEMS])
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for filename, slug, poster_time, already_h264 in ITEMS:
        if args.only and slug != args.only:
            continue
        source = SOURCE / filename
        video_codec = ['-c:v', 'copy'] if already_h264 else ['-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-pix_fmt', 'yuv420p', '-threads', '2']
        video_map = ['-filter_complex', BULB_PRIVACY_FILTER, '-map', '[v]'] if slug == 'bulb' else ['-map', '0:v:0']
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), *video_map, '-map', '0:a:0?', *video_codec, '-c:a', 'copy', '-map_metadata', '-1', '-movflags', '+faststart', str(DEST / f'{slug}.mp4')], check=True)
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(poster_time), '-i', str(DEST / f'{slug}.mp4'), '-frames:v', '1', '-vf', 'scale=960:960:force_original_aspect_ratio=decrease', '-q:v', '3', str(DEST / f'{slug}.jpg')], check=True)
        print(slug, round((DEST / f'{slug}.mp4').stat().st_size / 1048576, 2), 'MiB', flush=True)

if __name__ == '__main__':
    main()
