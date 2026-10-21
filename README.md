# BOT TỰ ĐỘNG TẠO VIDEO PHÁC THẢO BÚT CHÌ POV (SHORTS / TIKTOK / REELS)

Hệ thống bot tự động 100% FREE, hoạt động 24/7, chuyên tạo video vẽ phác thảo bút chì nghệ thuật góc nhìn POV (Point-Of-View) trên giấy A4 đặt trên bàn gỗ, kèm giọng thuyết minh tiếng Anh bản xứ (US English), hiệu ứng âm thanh ASMR vẽ bút chì, nhạc nền lofi acoustic và tự động đăng tải lên 3 nền tảng: **YouTube Shorts**, **TikTok**, **Facebook Reels**.

---

## 🎯 Cấu trúc Video hoàn thiện (Chuẩn 9:16 - Thời lượng ~35 giây, < 60s)

1. **Góc quay POV siêu thực:** Bàn gỗ ấm áp, tờ giấy trắng A4 ở trung tâm dưới ánh nắng sáng sớm rọi qua rèm lá cửa sổ, bàn tay trái đặt tự nhiên cố định góc giấy, bàn tay phải cầm bút chì gỗ chuyển động vẽ trực tiếp lên mặt giấy.
2. **Step 1 (0s - 10s | Phác thảo khung cơ bản):** Nét chì 2H phác thảo dáng tổng thể của vật thể. Đầu bút chì lướt tới đâu, nét vẽ hiện ra chân thực tới đó. Badge HUD: `STEP 1: LIGHT OUTLINE`.
3. **Step 2 (10s - 19s | Đi nét chi tiết):** Bút chì 2B đi lại các đường nét cấu trúc chính, cuống lá, gân, các góc cạnh đặc trưng. Badge HUD: `STEP 2: ADDING DETAILS`.
4. **Step 3 (19s - 28s | Đánh bóng tạo khối 3D):** Nét chì 4B/6B đan chéo (cross-hatching) đánh bóng mịn màng, tạo chiều sâu và bóng đổ chân thực trên mặt giấy. Badge HUD: `STEP 3: SHADING & DEPTH`.
5. **Step 4 (28s - 31.5s | Hoàn thiện & Rút tay khoe tranh):** Tay phải nhấc bút chì và lướt êm ra mép ngoài màn hình, để lộ bức tranh bút chì hoàn chỉnh tuyệt đẹp trên bàn. Badge HUD: `COMPLETED PENCIL SKETCH`.
6. **Step 5 (31.5s - 35s | Kêu gọi Đăng ký & Bình luận):** Thẻ CTA thanh lịch xuất hiện: *"What should I sketch next? Comment below & SUBSCRIBE for daily art tutorials!"* kèm nút Subscribe đỏ nổi bật.

---

## 🛡️ Hệ thống Chống Trùng lặp Vật thể (Zero-Duplication Catalog)
- Quản lý danh mục hơn **300+ vật thể đời thường quen thuộc** (hoa quả, xe cộ, dụng cụ, kiến trúc, động vật, trò chơi...).
- File `history_objects.json` tự động ghi nhớ toàn bộ vật thể đã vẽ trên kênh. Mỗi video là một vật thể độc nhất 100%, không bao giờ bị lặp lại.

---

## 🌐 3 Khung Giờ Đăng Dễ Viral Quốc Tế Nhất (Target US & Global Views)
- **07:00 Sáng VN (08:00 PM EDT tối hôm trước tại Mỹ):** Giờ vàng Prime Time của người Mỹ lướt mạng xã hội sau bữa tối.
- **19:00 Tối VN (08:00 AM EDT tại Mỹ & 01:00 PM Châu Âu):** Giờ đi làm buổi sáng tại Mỹ và đầu giờ chiều tại Châu Âu.
- **23:00 Đêm VN (12:00 PM EDT tại Mỹ):** Giờ nghỉ trưa Peak Scrolling tại Mỹ.

---

## ⚙️ Các Module của Bot

| File | Chức năng | Công nghệ |
|---|---|---|
| `object_catalog.py` | Quản lý 300+ vật thể, chống trùng lặp qua `history_objects.json`, tạo prompt tranh và kịch bản tutorial tiếng Anh | Python JSON Engine |
| `ai_artist.py` | Tạo tranh phác thảo bút chì đen trắng trên nền trắng tinh khiết | Pollinations Turbo / AI Engine (100% Free) |
| `voice_generator.py` | Tạo giọng đọc hướng dẫn tiếng Anh bản xứ chuẩn US | Edge-TTS (`en-US-ChristopherNeural`) + gTTS Fallback |
| `pov_sketch_engine.py` | Render video POV góc nhìn cầm bút chì vẽ trên giấy A4 với bàn tay chuyển động thực | OpenCV (Multiply Blend, Alpha Blending) |
| `video_composer.py` | Ghép video, giọng đọc, âm thanh cọ xát bút chì ASMR, nhạc nền BGM | FFmpeg Filter Complex |
| `auto_uploader.py` | Tự động tải video lên YouTube Shorts, Facebook Reels, TikTok | YouTube API v3, Meta Graph API, Playwright |
| `scheduler.py` | Lập lịch tự động 24/7 đăng 3 video/ngày (07:00, 19:00, 23:00) | APScheduler |
| `main.py` | Trình điều khiển chính | Python CLI |

---

## 🚀 Hướng dẫn sử dụng

### 1. Chạy thử tạo 1 video ngay lập tức
- Nhấp đúp vào file `Chay_Thu_1_Video.bat`
- Hoặc gõ lệnh:
```bash
python main.py --run-now
```

### 2. Vẽ một vật thể tùy chọn (ví dụ: quả táo, máy bay, ngôi nhà)
```bash
python main.py --object "airplane"
```

### 3. Chạy tự động 24/7
- Nhấp đúp vào file `Chay_Bot_Tu_Dong_24_7.bat`
- Hoặc gõ lệnh:
```bash
python main.py --start-scheduler
```
