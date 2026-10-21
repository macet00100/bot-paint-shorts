"""
POV Pencil Sketch Animation Engine (Authentic A4 Paper on Wooden Desk)
Renders clean, smooth, tutorial-style pencil drawing:
- 100% clean continuous vector strokes (zero dithering, zero broken noise artifacts).
- Authentic physical graphite Multiply blending onto blank A4 desk paper.
- 5 Tutorial Stages (< 60s total, exactly 35.0s at 24fps):
  1. Stage 1 (0s - 10s): Simple Outline (Light 2H Pencil)
  2. Stage 2 (10s - 19s): Retracing & Defining Contours (Bold 2B Pencil - "Dặm lại nét")
  3. Stage 3 (19s - 28s): Clean Diagonal Hatching & Depth (4B Pencil - "Dặm bóng")
  4. Stage 4 (28s - 31.5s): Hand lifts and glides off-screen, revealing clean art
  5. Stage 5 (31.5s - 35s): Call-To-Action ("What should I sketch next? Subscribe!")
"""
import math
import cv2
import numpy as np
from pathlib import Path

from config import ASSETS_DIR


class POVSketchEngine:
    def __init__(self):
        self.vw = 720
        self.vh = 1280
        self.fps = 24
        self._load_assets()

    def _load_assets(self):
        """Loads blank A4 desk canvas and hand-pencil sprite"""
        desk_path = ASSETS_DIR / "blank_a4_desk.jpg"
        if not desk_path.exists():
            raise FileNotFoundError(f"Missing background template: {desk_path}")
        self.desk_bg = cv2.imread(str(desk_path))
        if self.desk_bg.shape[:2] != (self.vh, self.vw):
            self.desk_bg = cv2.resize(self.desk_bg, (self.vw, self.vh))

        hand_path = ASSETS_DIR / "hand_pencil.png"
        if not hand_path.exists():
            raise FileNotFoundError(f"Missing hand sprite: {hand_path}")
        self.hand_sprite = cv2.imread(str(hand_path), cv2.IMREAD_UNCHANGED)

        # Exact graphite pencil tip coordinates inside hand_pencil.png
        self.tip_offset_x = 21
        self.tip_offset_y = 335

        # Subscribe button
        sub_btn_path = ASSETS_DIR / "subscribe_btn.png"
        if sub_btn_path.exists():
            self.sub_btn_img = cv2.imread(str(sub_btn_path), cv2.IMREAD_UNCHANGED)
        else:
            self.sub_btn_img = None

    def _overlay_alpha(self, bg, fg, x, y):
        """Safely alpha-blends an RGBA image onto a BGR background at (x, y)"""
        if fg is None:
            return bg
        fh, fw = fg.shape[:2]
        bh, bw = bg.shape[:2]

        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(bw, x + fw), min(bh, y + fh)
        if x1 >= x2 or y1 >= y2:
            return bg

        fg_x1 = max(0, -x)
        fg_y1 = max(0, -y)
        fg_x2 = fg_x1 + (x2 - x1)
        fg_y2 = fg_y1 + (y2 - y1)

        fg_crop = fg[fg_y1:fg_y2, fg_x1:fg_x2]
        bg_crop = bg[y1:y2, x1:x2]

        if fg_crop.shape[2] == 4:
            alpha = (fg_crop[:, :, 3] / 255.0)[:, :, np.newaxis]
            bg_crop[:] = (alpha * fg_crop[:, :, :3] + (1.0 - alpha) * bg_crop).astype(np.uint8)
        else:
            bg_crop[:] = fg_crop[:, :, :3]
        return bg

    def _draw_pill_badge(self, frame, text, center_x, center_y, bg_color=(25, 25, 30), text_color=(255, 255, 255)):
        """Draws a clean, rounded tutorial HUD badge"""
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.65
        thickness = 1
        (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)

        pad_x, pad_y = 20, 10
        bx1 = center_x - tw // 2 - pad_x
        by1 = center_y - th // 2 - pad_y
        bx2 = center_x + tw // 2 + pad_x
        by2 = center_y + th // 2 + pad_y

        overlay = frame.copy()
        cv2.rectangle(overlay, (bx1, by1), (bx2, by2), bg_color, -1)
        cv2.rectangle(overlay, (bx1, by1), (bx2, by2), (180, 180, 185), 1)
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

        tx = center_x - tw // 2
        ty = center_y + th // 2
        cv2.putText(frame, text, (tx, ty), font, font_scale, text_color, thickness, cv2.LINE_AA)

    def _extract_clean_strokes(self, gray_img):
        """
        Extracts clean, smooth, ordered vector strokes from line art image.
        Filters out noise, specks, and jitter.
        """
        dh, dw = gray_img.shape[:2]

        # Clean binary threshold: dark lines are foreground
        _, binary = cv2.threshold(gray_img, 195, 255, cv2.THRESH_BINARY_INV)

        # Remove stray noise specks
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        valid_strokes = []
        for c in contours:
            length = cv2.arcLength(c, False)
            if length > 25:
                # Smooth curve to eliminate jagged pixelation
                smooth = cv2.approxPolyDP(c, epsilon=1.2, closed=False)
                pts = smooth.reshape(-1, 2)
                if len(pts) >= 2:
                    valid_strokes.append((length, pts))

        # Sort largest/longest strokes first (main outline first, then inner details)
        valid_strokes.sort(key=lambda x: x[0], reverse=True)

        strokes_pts = [pts for _, pts in valid_strokes]
        if not strokes_pts:
            # Fallback circle if image had no clear lines
            pts = []
            for deg in range(0, 360, 10):
                rad = math.radians(deg)
                pts.append([int(dw // 2 + 100 * math.cos(rad)), int(dh // 2 + 120 * math.sin(rad))])
            strokes_pts = [np.array(pts)]

        return strokes_pts, cleaned

    def _generate_hatching_strokes(self, binary_mask, dw, dh):
        """
        Generates clean, parallel 45-degree diagonal hatching pencil strokes
        in the shadow zone of the object and contact shadow below it.
        """
        # Find object bounding box
        y_idx, x_idx = np.where(binary_mask > 0)
        if len(y_idx) == 0:
            return []

        y_min, y_max = y_idx.min(), y_idx.max()
        x_min, x_max = x_idx.min(), x_idx.max()
        obj_w = x_max - x_min
        obj_h = y_max - y_min

        # Shadow zone: lower-right portion inside the object
        shadow_mask = np.zeros((dh, dw), dtype=np.uint8)
        # Fill object interior using convex hull
        hull = cv2.convexHull(np.column_stack((x_idx, y_idx)))
        cv2.drawContours(shadow_mask, [hull], -1, 255, -1)

        # Crescent shadow mask (right and bottom side)
        crescent_center_x = int(x_min + obj_w * 0.58)
        crescent_center_y = int(y_min + obj_h * 0.55)
        crescent_mask = np.zeros((dh, dw), dtype=np.uint8)
        cv2.ellipse(
            crescent_mask,
            (crescent_center_x, crescent_center_y),
            (int(obj_w * 0.42), int(obj_h * 0.42)),
            0, 0, 360, 255, -1
        )
        inner_shadow = cv2.bitwise_and(shadow_mask, crescent_mask)

        # Contact shadow beneath object on paper
        contact_y = min(dh - 15, y_max + 8)
        cv2.ellipse(
            inner_shadow,
            (int(x_min + obj_w * 0.5), contact_y),
            (int(obj_w * 0.35), 8),
            0, 0, 360, 255, -1
        )

        # Generate clean 45-degree parallel hatching lines spaced 10px apart
        hatch_strokes = []
        step = 10
        for d in range(-dh, dw + dh, step):
            pts_on_line = []
            for x in range(0, dw, 3):
                y = x - d
                if 0 <= y < dh and inner_shadow[y, x] > 0:
                    pts_on_line.append((x, y))
            if len(pts_on_line) > 4:
                # Add straight hatching line from start to end
                hatch_strokes.append(np.array([pts_on_line[0], pts_on_line[-1]]))

        return hatch_strokes

    def render_sketch_video(self, input_image_path, object_display_name, output_video_path):
        """
        Renders complete ~35s POV pencil sketching video at 720x1280 (9:16).
        """
        output_video_path = Path(output_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[*] POV Sketch Engine rendering video: '{output_video_path.name}'...")

        src_img = cv2.imread(str(input_image_path))
        if src_img is None:
            raise FileNotFoundError(f"Cannot load image: {input_image_path}")

        # Dimensions of drawing area on A4 paper
        dw, dh = 360, 440
        dx = (self.vw - dw) // 2  # 180 (centered horizontally)
        dy = 480                  # centered on A4 paper

        scaled = cv2.resize(src_img, (dw, dh), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)

        # Extract clean vector strokes and shadow hatching
        strokes, binary_mask = self._extract_clean_strokes(gray)
        hatch_strokes = self._generate_hatching_strokes(binary_mask, dw, dh)

        # Flatten segments for Stage 1 (Outline)
        # Each segment is (p1, p2)
        segments_outline = []
        for s in strokes:
            for i in range(1, len(s)):
                segments_outline.append((s[i - 1], s[i]))

        if not segments_outline:
            segments_outline = [((dw // 2, dh // 2), (dw // 2 + 10, dh // 2 + 10))]

        # Flatten segments for Stage 2 (Dặm lại & Details)
        segments_details = segments_outline.copy()

        # Flatten segments for Stage 3 (Hatching Shading)
        segments_hatching = []
        for hs in hatch_strokes:
            p1, p2 = hs[0], hs[1]
            segments_hatching.append((p1, p2))
        if not segments_hatching:
            segments_hatching = [((dw // 2, dh // 2), (dw // 2 + 15, dh // 2 + 15))]

        # Video Writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_video_path), fourcc, self.fps, (self.vw, self.vh))

        # Timing Setup (Total = 35.0s = 840 frames at 24fps)
        frames_stage1 = int(10.0 * self.fps)  # 0s - 10s: Outline (240 frames)
        frames_stage2 = int(9.0 * self.fps)   # 10s - 19s: Dặm lại & Details (216 frames)
        frames_stage3 = int(9.0 * self.fps)   # 19s - 28s: Dặm bóng (216 frames)
        frames_stage4 = int(3.5 * self.fps)   # 28s - 31.5s: Reveal & Hand Slide Off (84 frames)
        frames_stage5 = int(3.5 * self.fps)   # 31.5s - 35s: Call-To-Action (84 frames)
        total_frames = frames_stage1 + frames_stage2 + frames_stage3 + frames_stage4 + frames_stage5

        print(f"    Total frames to render: {total_frames} (~35.0s at {self.fps} fps)")

        # Active drawing canvas on pure white paper (starts 255)
        art_canvas = np.ones((dh, dw), dtype=np.uint8) * 255

        cur_tip_x = dx + segments_outline[0][0][0]
        cur_tip_y = dy + segments_outline[0][0][1]

        # =========================================================
        # STAGE 1: NÉT CHÌ ĐƠN GIẢN (0s - 10s)
        # =========================================================
        print("    -> Rendering Stage 1: Simple Outline (2H)...")
        segs_per_frame_1 = max(1, len(segments_outline) // frames_stage1)
        drawn_idx_1 = 0

        for f in range(frames_stage1):
            next_idx = min(len(segments_outline), drawn_idx_1 + segs_per_frame_1 * 2)

            for i in range(drawn_idx_1, next_idx):
                p1, p2 = segments_outline[i]
                # Draw light pencil stroke (light gray 175, thickness 2)
                cv2.line(art_canvas, tuple(p1), tuple(p2), 175, 2, cv2.LINE_AA)

            drawn_idx_1 = next_idx
            last_p = segments_outline[min(len(segments_outline) - 1, drawn_idx_1)][1]
            cur_tip_x = dx + int(last_p[0])
            cur_tip_y = dy + int(last_p[1])

            # Multiply blend onto blank desk paper
            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            art_norm = (art_canvas.astype(np.float32) / 255.0)[:, :, np.newaxis]
            blended_roi = (paper_roi * art_norm).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            # Overlay hand with pencil tip exactly at cur_tip
            hx = cur_tip_x - self.tip_offset_x
            hy = cur_tip_y - self.tip_offset_y
            frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            self._draw_pill_badge(frame, "STEP 1: LIGHT OUTLINE", self.vw // 2, 70)
            writer.write(frame)

        # =========================================================
        # STAGE 2: DẶM LẠI NÉT & CHI TIẾT (10s - 19s)
        # =========================================================
        print("    -> Rendering Stage 2: Retracing Contours (2B)...")
        segs_per_frame_2 = max(1, len(segments_details) // frames_stage2)
        drawn_idx_2 = 0

        for f in range(frames_stage2):
            next_idx = min(len(segments_details), drawn_idx_2 + segs_per_frame_2 * 2)

            for i in range(drawn_idx_2, next_idx):
                p1, p2 = segments_details[i]
                # Retrace with bold dark graphite line (dark charcoal 40, thickness 3)
                cv2.line(art_canvas, tuple(p1), tuple(p2), 40, 3, cv2.LINE_AA)

            drawn_idx_2 = next_idx
            last_p = segments_details[min(len(segments_details) - 1, drawn_idx_2)][1]
            cur_tip_x = dx + int(last_p[0])
            cur_tip_y = dy + int(last_p[1])

            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            art_norm = (art_canvas.astype(np.float32) / 255.0)[:, :, np.newaxis]
            blended_roi = (paper_roi * art_norm).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            hx = cur_tip_x - self.tip_offset_x
            hy = cur_tip_y - self.tip_offset_y
            frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            self._draw_pill_badge(frame, "STEP 2: DEFINING CONTOURS", self.vw // 2, 70)
            writer.write(frame)

        # =========================================================
        # STAGE 3: DẶM BÓNG KHỐI & BÓNG ĐỔ (19s - 28s)
        # =========================================================
        print("    -> Rendering Stage 3: Shading & Hatching (4B)...")
        hatch_per_frame = max(1, len(segments_hatching) // frames_stage3)
        drawn_hatch_idx = 0

        for f in range(frames_stage3):
            next_idx = min(len(segments_hatching), drawn_hatch_idx + hatch_per_frame * 2)

            for i in range(drawn_hatch_idx, next_idx):
                p1, p2 = segments_hatching[i]
                # Draw crisp diagonal pencil hatching lines (gray 85, thickness 1)
                cv2.line(art_canvas, tuple(p1), tuple(p2), 85, 1, cv2.LINE_AA)

            drawn_hatch_idx = next_idx
            last_hatch = segments_hatching[min(len(segments_hatching) - 1, drawn_hatch_idx)]
            # Interpolate tip along active hatching line for fluid motion
            sub_progress = (f % 4) / 4.0
            cur_tip_x = dx + int(last_hatch[0][0] + (last_hatch[1][0] - last_hatch[0][0]) * sub_progress)
            cur_tip_y = dy + int(last_hatch[0][1] + (last_hatch[1][1] - last_hatch[0][1]) * sub_progress)

            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            art_norm = (art_canvas.astype(np.float32) / 255.0)[:, :, np.newaxis]
            blended_roi = (paper_roi * art_norm).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            hx = cur_tip_x - self.tip_offset_x
            hy = cur_tip_y - self.tip_offset_y
            frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            self._draw_pill_badge(frame, "STEP 3: SHADING & DEPTH", self.vw // 2, 70)
            writer.write(frame)

        # =========================================================
        # STAGE 4: RÚT TAY KHOE TRANH (28s - 31.5s)
        # =========================================================
        print("    -> Rendering Stage 4: Reveal & Hand Slide Off...")
        hx_start = cur_tip_x - self.tip_offset_x
        hy_start = cur_tip_y - self.tip_offset_y

        for f in range(frames_stage4):
            progress = f / float(frames_stage4)
            # Smooth cubic ease-in
            slide_progress = progress * progress * progress
            slide_x = int(slide_progress * 550)
            slide_y = int(slide_progress * 80)

            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            art_norm = (art_canvas.astype(np.float32) / 255.0)[:, :, np.newaxis]
            blended_roi = (paper_roi * art_norm).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            hx = hx_start + slide_x
            hy = hy_start + slide_y
            if hx < self.vw + 50:
                frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            self._draw_pill_badge(
                frame, "COMPLETED PENCIL SKETCH",
                self.vw // 2, 70,
                bg_color=(20, 110, 40), text_color=(255, 255, 255)
            )
            writer.write(frame)

        # =========================================================
        # STAGE 5: CALL-TO-ACTION OVERLAY (31.5s - 35s)
        # =========================================================
        print("    -> Rendering Stage 5: Call-To-Action Overlay...")
        for f in range(frames_stage5):
            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            art_norm = (art_canvas.astype(np.float32) / 255.0)[:, :, np.newaxis]
            blended_roi = (paper_roi * art_norm).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            card_h = 220
            card_y = self.vh - card_h - 100
            card_x1 = 50
            card_x2 = self.vw - 50

            overlay = frame.copy()
            cv2.rectangle(overlay, (card_x1, card_y), (card_x2, card_y + card_h), (20, 20, 24), -1)
            cv2.rectangle(overlay, (card_x1, card_y), (card_x2, card_y + card_h), (230, 45, 45), 2)
            cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

            cv2.putText(
                frame, "WHAT SHOULD I SKETCH NEXT?",
                (card_x1 + 30, card_y + 60),
                cv2.FONT_HERSHEY_DUPLEX, 0.80, (255, 255, 255), 2, cv2.LINE_AA
            )
            cv2.putText(
                frame, "Comment below & SUBSCRIBE for daily art!",
                (card_x1 + 30, card_y + 115),
                cv2.FONT_HERSHEY_DUPLEX, 0.62, (200, 200, 205), 1, cv2.LINE_AA
            )

            if self.sub_btn_img is not None:
                sb_w = 220
                sb_h = int(self.sub_btn_img.shape[0] * (sb_w / self.sub_btn_img.shape[1]))
                sb_resized = cv2.resize(self.sub_btn_img, (sb_w, sb_h))
                sb_x = (self.vw - sb_w) // 2
                sb_y = card_y + 140
                frame = self._overlay_alpha(frame, sb_resized, sb_x, sb_y)

            self._draw_pill_badge(
                frame, f"SKETCH TUTORIAL: {object_display_name.upper()}",
                self.vw // 2, 70
            )
            writer.write(frame)

        writer.release()
        print(f"[+] Clean POV Sketch video rendered: {output_video_path}")
        return str(output_video_path)


if __name__ == "__main__":
    engine = POVSketchEngine()
    test_img = Path("temp/test_simple_apple.jpg")
    test_out = Path("temp/test_clean_apple.mp4")
    if test_img.exists():
        engine.render_sketch_video(test_img, "Apple", test_out)
