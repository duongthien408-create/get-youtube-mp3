# YouTube to MP3 Converter

Script Python đơn giản để tải video từ YouTube và chuyển đổi sang định dạng MP3.

## Tính năng

- ✅ Tải video YouTube chất lượng cao
- ✅ Tự động chuyển đổi sang MP3 (192kbps)
- ✅ Hiển thị thông tin video (tiêu đề, thời lượng)
- ✅ Hỗ trợ nhiều định dạng URL YouTube
- ✅ Giao diện dòng lệnh đơn giản

## Yêu cầu hệ thống

- Python 3.7 trở lên
- FFmpeg (để chuyển đổi audio)

### Cài đặt FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Tải FFmpeg từ https://ffmpeg.org/download.html và thêm vào PATH

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/your-username/get-youtube-mp3.git
cd get-youtube-mp3
```

2. Cài đặt thư viện Python:
```bash
pip install -r requirements.txt
```

## Cách sử dụng

### Cơ bản

Tải và chuyển đổi video YouTube sang MP3:

```bash
python youtube_to_mp3.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Với thư mục tùy chỉnh

Lưu file MP3 vào thư mục cụ thể:

```bash
python youtube_to_mp3.py "https://www.youtube.com/watch?v=VIDEO_ID" -o my_music
```

### Ví dụ

```bash
# Tải video và lưu vào thư mục mặc định (downloads)
python youtube_to_mp3.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Tải video và lưu vào thư mục "music"
python youtube_to_mp3.py "https://youtu.be/dQw4w9WgXcQ" -o music

# Xem hướng dẫn
python youtube_to_mp3.py --help
```

## Các tham số

- `url`: Link YouTube cần tải (bắt buộc)
- `-o, --output`: Thư mục lưu file MP3 (mặc định: `downloads`)
- `--no-check-certificate`: Bỏ qua kiểm tra SSL certificate (dùng khi gặp lỗi SSL)
- `-h, --help`: Hiển thị hướng dẫn

## Lưu ý

- Đảm bảo bạn có quyền tải và sử dụng nội dung từ YouTube
- Chỉ sử dụng cho mục đích cá nhân, tuân thủ bản quyền
- Cần kết nối internet để tải video

## Khắc phục sự cố

**Lỗi "ffmpeg not found":**
- Cài đặt FFmpeg theo hướng dẫn ở trên
- Đảm bảo FFmpeg có trong PATH

**Lỗi "SSL: CERTIFICATE_VERIFY_FAILED" (phổ biến trên macOS):**

Cách 1 - Sử dụng option bỏ qua SSL (nhanh nhất):
```bash
python youtube_to_mp3.py "LINK_YOUTUBE" --no-check-certificate
```

Cách 2 - Cài đặt certificates (khuyến khích):
```bash
# Với Anaconda/Miniconda:
conda update certifi
conda install -c conda-forge certifi

# Với pip:
pip install --upgrade certifi

# Nếu dùng Python từ python.org:
/Applications/Python*/Install\ Certificates.command
```

Cách 3 - Update yt-dlp:
```bash
pip install --upgrade yt-dlp
```

**Lỗi "Unable to extract":**
- Kiểm tra URL YouTube có hợp lệ không
- Thử lại sau vài phút
- Cập nhật yt-dlp: `pip install --upgrade yt-dlp`

## License

MIT License