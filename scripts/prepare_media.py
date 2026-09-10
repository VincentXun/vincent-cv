"""Prepare web copies without changing original videos; requires imageio-ffmpeg and Pillow."""
from pathlib import Path
import subprocess
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

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for filename, slug, poster_time, already_h264 in ITEMS:
        source = SOURCE / filename
        video_codec = ['-c:v', 'copy'] if already_h264 else ['-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-pix_fmt', 'yuv420p', '-threads', '2']
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), '-map', '0:v:0', '-map', '0:a:0?', *video_codec, '-c:a', 'copy', '-map_metadata', '-1', '-movflags', '+faststart', str(DEST / f'{slug}.mp4')], check=True)
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(poster_time), '-i', str(source), '-frames:v', '1', '-vf', 'scale=960:960:force_original_aspect_ratio=decrease', '-q:v', '3', str(DEST / f'{slug}.jpg')], check=True)
        print(slug, round((DEST / f'{slug}.mp4').stat().st_size / 1048576, 2), 'MiB', flush=True)

if __name__ == '__main__':
    main()
