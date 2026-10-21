"""
POV Pencil Sketch Animation Engine (Authentic A4 Paper on Wooden Desk)
Recreates the exact visual format and camera angle of the reference video:
- Top-down POV angle: Wooden desk, white A4 paper, morning sun & window shadows.
- Natural left hand resting on the paper corner.
- Natural right hand holding a wooden graphite pencil actively drawing.
- 100% authentic graphite-on-paper Multiply blending (zero box edges).
- Tutorial progression in 5 distinct stages (< 60s total, ~35s):
  1. Stage 1 (0s - 10s): Simple Outline (2H Pencil)
  2. Stage 2 (10s - 19s): Inner Details & Contours (2B Pencil)
  3. Stage 3 (19s - 28s): Graphite Shading & Depth (4B Pencil)
  4. Stage 4 (28s - 31.5s): Hand slides off-screen, revealing finished art
  5. Stage 5 (31.5s - 35s): Call-To-Action ("What should I sketch next? Subscribe!")
"""
import sys
import math
import cv2
import numpy as np
from pathlib import Path

from config import ASSETS_DIR, TEMP_DIR


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
        (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        pad_x, pad_y = 20, 10
        bx1 = center_x - tw // 2 - pad_x
        by1 = center_y - th // 2 - pad_y
        bx2 = center_x + tw // 2 + pad_x
        by2 = center_y + th // 2 + pad_y

        overlay = frame.copy()
        # Rounded rectangle pill
        cv2.rectangle(overlay, (bx1, by1), (bx2, by2), bg_color, -1)
        cv2.rectangle(overlay, (bx1, by1), (bx2, by2), (200, 200, 200), 1)
        # 80% opacity
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

        # Text
        tx = center_x - tw // 2
        ty = center_y + th // 2
        cv2.putText(frame, text, (tx, ty), font, font_scale, text_color, thickness, cv2.LINE_AA)

    def _extract_ordered_strokes(self, mask):
        """Extracts ordered stroke paths from binary mask"""
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)
        strokes = []
        for c in contours:
            pts = c.reshape(-1, 2)
            if len(pts) > 2:
                # Downsample slightly for natural hand stroke speed
                step = max(1, len(pts) // 40)
                sub_pts = pts[::step]
                strokes.append(sub_pts)
        return strokes

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

        # Dimensions of the drawing area on the A4 desk paper
        dw, dh = 360, 440
        dx = (self.vw - dw) // 2   # 180 (centered horizontally)
        dy = 480                   # centered on A4 paper

        # Scale source sketch image cleanly to fit drawing zone
        scaled_sketch = cv2.resize(src_img, (dw, dh), interpolation=cv2.INTER_LANCZOS4)
        gray = cv2.cvtColor(scaled_sketch, cv2.COLOR_BGR2GRAY)

        # Normalize tones: map paper background (>220) to pure white (255)
        norm_gray = np.clip((gray.astype(np.float32) - 15) / (225.0 - 15), 0, 1) * 255.0
        inv = (255.0 - norm_gray).astype(np.uint8)

        # Edge feathering mask to guarantee 100% invisible outer border
        feather_mask = np.ones((dh, dw), dtype=np.float32)
        pad = 25
        for i in range(pad):
            f = i / float(pad)
            feather_mask[i, :] = np.minimum(feather_mask[i, :], f)
            feather_mask[dh - 1 - i, :] = np.minimum(feather_mask[dh - 1 - i, :], f)
            feather_mask[:, i] = np.minimum(feather_mask[:, i], f)
            feather_mask[:, dw - 1 - i] = np.minimum(feather_mask[:, dw - 1 - i], f)

        # Target full drawing normalized tone map [0.0 = darkest graphite, 1.0 = paper]
        target_norm = (norm_gray / 255.0)
        target_norm = 1.0 - (1.0 - target_norm) * feather_mask

        # Extraction of stages:
        # 1. Outline mask (main contours / Canny edges)
        edges = cv2.Canny(norm_gray.astype(np.uint8), 40, 130)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dilated_edges = cv2.dilate(edges, kernel)
        outline_strokes = self._extract_ordered_strokes(dilated_edges)

        # 2. Detail mask (dark lines & features)
        _, dark_mask = cv2.threshold(inv, 65, 255, cv2.THRESH_BINARY)
        detail_strokes = self._extract_ordered_strokes(dark_mask)

        # 3. Shading mask (graphite depth)
        shading_weight = np.clip((inv.astype(np.float32) / 255.0) * feather_mask, 0, 1)

        # Flatten stroke points
        flat_outline = [pt for s in outline_strokes for pt in s]
        if not flat_outline:
            flat_outline = [(dw // 2, dh // 2)]

        flat_detail = [pt for s in detail_strokes for pt in s]
        if not flat_detail:
            flat_detail = [(dw // 2, dh // 2)]

        # Video Writer (720x1280 @ 24fps)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_video_path), fourcc, self.fps, (self.vw, self.vh))

        # Timing Setup (Total = 35.0s = 840 frames)
        frames_stage1 = int(10.0 * self.fps)  # 0s - 10s: Outline (240 frames)
        frames_stage2 = int(9.0 * self.fps)   # 10s - 19s: Details (216 frames)
        frames_stage3 = int(9.0 * self.fps)   # 19s - 28s: Shading & Shadows (216 frames)
        frames_stage4 = int(3.5 * self.fps)   # 28s - 31.5s: Reveal & Hand Slide Off (84 frames)
        frames_stage5 = int(3.5 * self.fps)   # 31.5s - 35s: Call-To-Action (84 frames)
        total_frames = frames_stage1 + frames_stage2 + frames_stage3 + frames_stage4 + frames_stage5

        print(f"    Total frames to render: {total_frames} (~35.0s at {self.fps} fps)")

        # Accumulated drawing layer (starts pure 1.0 white paper, darkens as drawn)
        art_layer = np.ones((dh, dw), dtype=np.float32)

        cur_tip_x = dx + flat_outline[0][0]
        cur_tip_y = dy + flat_outline[0][1]

        # =========================================================
        # STAGE 1: SIMPLE OUTLINE (0s - 10s)
        # =========================================================
        print("    -> Rendering Stage 1: Simple Outline (2H)...")
        pts_per_frame_1 = max(1, len(flat_outline) // frames_stage1)
        drawn_idx_1 = 0

        for f in range(frames_stage1):
            next_idx = min(len(flat_outline), drawn_idx_1 + pts_per_frame_1 * 2)

            for i in range(drawn_idx_1, next_idx):
                pt = flat_outline[i]
                # Stamp light graphite line (~0.72)
                cv2.circle(art_layer, (int(pt[0]), int(pt[1])), 2, 0.72, -1, lineType=cv2.LINE_AA)

            drawn_idx_1 = next_idx
            cur_pt = flat_outline[min(len(flat_outline) - 1, drawn_idx_1)]
            cur_tip_x = dx + cur_pt[0]
            cur_tip_y = dy + cur_pt[1]

            # Multiply blend drawing onto blank A4 desk paper
            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            blended_roi = (paper_roi * art_layer[:, :, np.newaxis]).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            # Overlay moving hand holding pencil
            hx = cur_tip_x - self.tip_offset_x
            hy = cur_tip_y - self.tip_offset_y
            frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            # Stage Badge
            self._draw_pill_badge(frame, "STEP 1: LIGHT OUTLINE", self.vw // 2, 70)
            writer.write(frame)

        # =========================================================
        # STAGE 2: DETAILS & CONTOURS (10s - 19s)
        # =========================================================
        print("    -> Rendering Stage 2: Adding Details (2B)...")
        pts_per_frame_2 = max(1, len(flat_detail) // frames_stage2)
        drawn_idx_2 = 0

        for f in range(frames_stage2):
            next_idx = min(len(flat_detail), drawn_idx_2 + pts_per_frame_2 * 2)

            for i in range(drawn_idx_2, next_idx):
                pt = flat_detail[i]
                # Stamp darker crisp graphite line (~0.35)
                cv2.circle(art_layer, (int(pt[0]), int(pt[1])), 2, 0.35, -1, lineType=cv2.LINE_AA)

            drawn_idx_2 = next_idx
            cur_pt = flat_detail[min(len(flat_detail) - 1, drawn_idx_2)]
            cur_tip_x = dx + cur_pt[0]
            cur_tip_y = dy + cur_pt[1]

            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            blended_roi = (paper_roi * art_layer[:, :, np.newaxis]).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            hx = cur_tip_x - self.tip_offset_x
            hy = cur_tip_y - self.tip_offset_y
            frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            self._draw_pill_badge(frame, "STEP 2: ADDING DETAILS", self.vw // 2, 70)
            writer.write(frame)

        # =========================================================
        # STAGE 3: SHADING & DEPTH (19s - 28s)
        # =========================================================
        print("    -> Rendering Stage 3: Shading & Depth (4B)...")
        last_drawn_layer = art_layer.copy()

        for f in range(frames_stage3):
            progress = (f + 1) / float(frames_stage3)

            # Progressive shading reveal
            current_layer = (
                (1.0 - progress) * last_drawn_layer +
                progress * target_norm
            )

            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            blended_roi = (paper_roi * current_layer[:, :, np.newaxis]).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            # Natural shading pencil motion (rapid small back-and-forth cross-hatch movement)
            hatch_angle = f * 0.95
            hatch_radius_x = 24.0 * math.sin(f * 0.3)
            hatch_radius_y = 14.0 * math.cos(f * 0.4)
            shading_tip_x = int(dx + dw // 2 + hatch_radius_x + math.cos(hatch_angle) * 12)
            shading_tip_y = int(dy + dh // 2 + hatch_radius_y + math.sin(hatch_angle) * 8)

            hx = shading_tip_x - self.tip_offset_x
            hy = shading_tip_y - self.tip_offset_y
            frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            self._draw_pill_badge(frame, "STEP 3: SHADING & DEPTH", self.vw // 2, 70)
            writer.write(frame)

        # Lock final art layer
        final_art_layer = target_norm.copy()

        # =========================================================
        # STAGE 4: MASTERPIECE REVEAL & HAND SLIDE OFF (28s - 31.5s)
        # =========================================================
        print("    -> Rendering Stage 4: Reveal & Hand Slide Off...")
        hx_start = cur_tip_x - self.tip_offset_x
        hy_start = cur_tip_y - self.tip_offset_y

        for f in range(frames_stage4):
            progress = f / float(frames_stage4)
            # Cubic ease-in for smooth acceleration off-screen to the right
            slide_progress = progress * progress * progress
            slide_x = int(slide_progress * 550)
            slide_y = int(slide_progress * 80)

            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            blended_roi = (paper_roi * final_art_layer[:, :, np.newaxis]).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            # Slide hand off to the right
            hx = hx_start + slide_x
            hy = hy_start + slide_y
            if hx < self.vw + 50:
                frame = self._overlay_alpha(frame, self.hand_sprite, hx, hy)

            # Elegant reveal badge
            self._draw_pill_badge(
                frame, "COMPLETED PENCIL SKETCH",
                self.vw // 2, 70,
                bg_color=(20, 110, 40), text_color=(255, 255, 255)
            )
            writer.write(frame)

        # =========================================================
        # STAGE 5: CALL-TO-ACTION (31.5s - 35s)
        # =========================================================
        print("    -> Rendering Stage 5: Call-To-Action Overlay...")
        for f in range(frames_stage5):
            frame = self.desk_bg.copy()
            paper_roi = frame[dy:dy+dh, dx:dx+dw].astype(np.float32)
            blended_roi = (paper_roi * final_art_layer[:, :, np.newaxis]).astype(np.uint8)
            frame[dy:dy+dh, dx:dx+dw] = blended_roi

            # Subtle pulsing alpha for CTA card
            card_h = 220
            card_y = self.vh - card_h - 100
            card_x1 = 50
            card_x2 = self.vw - 50

            overlay = frame.copy()
            cv2.rectangle(overlay, (card_x1, card_y), (card_x2, card_y + card_h), (20, 20, 24), -1)
            cv2.rectangle(overlay, (card_x1, card_y), (card_x2, card_y + card_h), (230, 45, 45), 2)
            cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

            # CTA Typography
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

            # Subscribe Button
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
        print(f"[+] POV Sketch video rendered successfully: {output_video_path}")
        return str(output_video_path)


if __name__ == "__main__":
    engine = POVSketchEngine()
    test_img = TEMP_DIR / "test_pencil_pear.jpg"
    test_out = TEMP_DIR / "test_pov_sketch.mp4"
    if test_img.exists():
        engine.render_sketch_video(test_img, "Pear", test_out)
