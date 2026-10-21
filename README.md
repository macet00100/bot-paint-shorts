# BOT TỰ ĐỘNG TẠO VIDEO VẼ TRANH BIẾM HỌA MS PAINT (SHORT / REELS / TIKTOK)

Hệ thống bot tự động 100% FREE, hoạt động 24/7, tự động tìm kiếm xu hướng (Trend Research), sáng tạo tranh biếm họa AI 2K, mô phỏng quá trình vẽ trong MS Paint bằng con trỏ chuột, lồng tiếng tiếng Việt, chèn âm thanh hiệu ứng (SFX/BGM) và đẩy video lên 3 nền tảng: **YouTube Shorts**, **TikTok**, **Facebook Reels**.

---

## 🎯 Cấu trúc Video hoàn thiện (Chuẩn 9:16 - Thời lượng ~30 giây)

1. **0s - 3s (Mở đầu / Hook):** Bức ảnh biếm họa hoàn thiện 2K xuất hiện toàn màn hình với hiệu ứng zoom và tiêu đề kích thích tò mò: *"BẠN CÓ TIN BỨC TRANH NÀY VẼ 100% BẰNG MS PAINT?"*.
2. **3s - 14s (Phác thảo nét vẽ bằng con trỏ chuột):** Chuyển sang giao diện cửa sổ MS Paint. Con trỏ chuột Windows di chuyển trên nền giấy trắng vẽ từng nét chì đen phác thảo khuôn mặt và nhân vật. Kèm âm thanh sột soạt vẽ tranh và click chuột.
3. **14s - 24s (Lên màu & Đổ màu):** Chuột di chuyển lên thanh công cụ chọn bảng màu và đổ từng mảng màu nước/sơn rực rỡ, lan tỏa sống động khắp bức tranh.
4. **24s - 27s (Thành phẩm):** Chuột kết thúc nét vẽ, nhãn *"HOÀN THÀNH: 100% MS PAINT!"* sáng bừng cùng âm thanh chuông reng/ding tinh tế.
5. **27s - 30s (Kêu gọi Like & Đăng ký):** Nút **SUBSCRIBE / LIKE** dạng animation xuất hiện, con trỏ chuột rê vào và CLICK trực tiếp vào nút Subscribe, kết thúc với lời kêu gọi ủng hộ kênh.

---

## ⚙️ Các Module của Bot

| File | Chức năng | Công nghệ (100% Free) |
|---|---|---|
| `trend_researcher.py` | Quét Google Trends VN & Tin tức thời sự 3 lần/ngày, lọc chủ đề hot để làm biếm họa | Google Trends RSS, News RSS, Python Regex |
| `ai_artist.py` | Tạo tranh biếm họa 2K sắc nét, không logo/watermark | Pollinations Turbo/Flux AI (Miễn phí vĩnh viễn) |
| `voice_generator.py` | Tạo giọng lồng tiếng tiếng Việt tự nhiên chuẩn Short | Edge-TTS + Google TTS (gTTS Fallback) |
| `paint_engine.py` | Dựng video mô phỏng MS Paint 9:16 (1080x1920) với chuột vẽ | OpenCV, Pillow, Numpy |
| `video_composer.py` | Ghép video, giọng đọc, tiếng chuột click, tiếng vẽ bút chì, nhạc nền lofi | FFmpeg Filter Complex |
| `auto_uploader.py` | Đẩy video lên YouTube Shorts, Facebook Reels, TikTok | YouTube Data API, Meta Graph API, Playwright |
| `scheduler.py` | Lập lịch tự động 24/7 đăng 3 video/ngày: **11:00, 20:00, 22:00** | APScheduler |
| `main.py` | Trình điều khiển chính | Python CLI |

---

## 🚀 Hướng dẫn sử dụng

### 1. Chạy thử tạo 1 video ngay lập tức
- Nhấp đúp vào file `Chay_Thu_1_Video.bat`
- Hoặc gõ lệnh trong terminal:
```bash
python main.py --run-now
```
Video sau khi tạo xong sẽ nằm trong thư mục `output/` (ví dụ: `output/paint_short_YYYYMMDD_HHMMSS.mp4`).

### 2. Tạo video theo một chủ đề bạn chọn sẵn
```bash
python main.py --topic "Chủ đề bạn muốn (ví dụ: Chú mèo hoàng đế)"
```

### 3. Chạy tự động 24/7 (Đăng 3 video/ngày lúc 11h trưa, 8h tối, 10h tối)
- Nhấp đúp vào file `Chay_Bot_Tu_Dong_24_7.bat`
- Hoặc gõ lệnh:
```bash
python main.py --start-scheduler
```
Bot sẽ chạy ngầm liên tục trên máy, đúng giờ quy định sẽ tự động nghiên cứu trend mới nhất -> vẽ tranh -> ghép video -> đẩy lên mạng xã hội.

---

## 🔑 Hướng dẫn cấu hình Đăng tự động (YouTube, Facebook, TikTok)

Mở file `config.py`:
1. **YouTube Shorts:** Tải file `client_secret.json` từ [Google Cloud Console](https://console.cloud.google.com/) (YouTube Data API v3 miễn phí 10.000 điểm quota/ngày) và để vào thư mục gốc của bot. Lần chạy đầu tiên sẽ mở trình duyệt để xác thực 1 lần duy nhất, sau đó bot tự làm mới token mãi mãi.
2. **Facebook Reels:** Điền `FACEBOOK_PAGE_ID` và `FACEBOOK_ACCESS_TOKEN` (tạo token vĩnh viễn từ Meta for Developers).
3. **TikTok:** Điền cookie `TIKTOK_SESSION_COOKIE` (lấy giá trị `sessionid` từ trình duyệt sau khi đăng nhập TikTok Web) để bot tự động đăng tải qua Playwright mà không cần tài khoản doanh nghiệp.
