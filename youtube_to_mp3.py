#!/usr/bin/env python3
"""
YouTube to MP3 Converter
Tải và chuyển đổi video YouTube thành file MP3
"""

import os
import sys
import argparse
from pathlib import Path
import yt_dlp


def download_youtube_to_mp3(url, output_path="downloads"):
    """
    Tải video YouTube và chuyển đổi sang MP3

    Args:
        url (str): Link YouTube cần tải
        output_path (str): Thư mục lưu file MP3

    Returns:
        str: Đường dẫn đến file MP3 đã tải
    """
    # Tạo thư mục output nếu chưa có
    Path(output_path).mkdir(parents=True, exist_ok=True)

    # Cấu hình yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }

    try:
        print(f"\n🎵 Đang tải video từ: {url}")
        print("=" * 60)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Lấy thông tin video
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)

            print(f"📹 Tiêu đề: {video_title}")
            print(f"⏱️  Thời lượng: {duration // 60}:{duration % 60:02d}")
            print(f"📂 Thư mục lưu: {output_path}")
            print("\n🔄 Đang tải và chuyển đổi sang MP3...")

            # Tải và chuyển đổi
            ydl.download([url])

            # Tìm file MP3 đã tải
            mp3_file = os.path.join(output_path, f"{video_title}.mp3")

            print("\n✅ Hoàn thành!")
            print(f"📁 File đã lưu: {mp3_file}")

            return mp3_file

    except Exception as e:
        print(f"\n❌ Lỗi: {str(e)}", file=sys.stderr)
        return None


def main():
    """Hàm chính"""
    parser = argparse.ArgumentParser(
        description='Tải video YouTube và chuyển đổi sang MP3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python youtube_to_mp3.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python youtube_to_mp3.py "https://youtu.be/dQw4w9WgXcQ" -o my_music
        """
    )

    parser.add_argument(
        'url',
        help='Link YouTube cần tải (đặt trong dấu ngoặc kép)'
    )

    parser.add_argument(
        '-o', '--output',
        default='downloads',
        help='Thư mục lưu file MP3 (mặc định: downloads)'
    )

    args = parser.parse_args()

    # Kiểm tra URL
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Lỗi: URL không hợp lệ. Vui lòng cung cấp link YouTube đầy đủ.", file=sys.stderr)
        sys.exit(1)

    # Tải và chuyển đổi
    result = download_youtube_to_mp3(args.url, args.output)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
