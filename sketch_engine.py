"""
Pencil Sketch Animation Engine (100% Graphite on Sketchbook Paper)
Renders a 9:16 vertical drawing video simulating authentic pencil sketching:
1. Stage 1 (0s - 9s): Light Construction Line Art (2H Pencil)
2. Stage 2 (9s - 20s): Deep Contours & Structural Outlines (2B Pencil)
3. Stage 3 (20s - 31s): Progressive Cross-Hatch Shading & Shadows (4B/6B Pencil)
4. Stage 4 (31s - 35s): Masterpiece Reveal & Artistic Zoom
5. Stage 5 (35s - 38s): Subscribe Call-To-Action Overlay
"""
import sys
import math
import cv2
import numpy as np
from pathlib import Path

from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, ASSETS_DIR, TEMP_DIR
)


class SketchEngine:
    def __init__(self):
        self.vw = VIDEO_WIDTH
        self.vh = VIDEO_HEIGHT
        self.fps = FPS
        self._load_assets()

    def _load_assets(self):
        """Loads pencil icon and sound/graphic assets"""
        cursor_path = ASSETS_DIR / "pencil_cursor.png"
        if not cursor_path.exists():
            cursor_path = ASSETS_DIR / "cursor.png"
        self.pencil_img = cv2.imread(str(cursor_path), cv2.IMREAD_UNCHANGED)
        self.sub_btn_img = cv2.imread(str(ASSETS_DIR / "subscribe_btn.png"), cv2.IMREAD_UNCHANGED)

    def _overlay_alpha(self, bg, fg, x, y):
        """Safely overlays an RGBA image onto a BGR background at (x, y)"""
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
            alpha = fg_crop[:, :, 3] / 255.0
            for c in range(3):
                bg_crop[:, :, c] = (
                    alpha * fg_crop[:, :, c] + (1.0 - alpha) * bg_crop[:, :, c]
                ).astype(np.uint8)
        else:
            bg_crop[:] = fg_crop[:, :, :3]
        return bg

    def _generate_paper_texture(self, h, w):
        """Generates realistic warm sketchbook paper with subtle fiber grain"""
        # Base cream / warm off-white color (242, 245, 247 in BGR)
        paper = np.zeros((h, w, 3), dtype=np.uint8)
        paper[:, :, 0] = 238  # B
        paper[:, :, 1] = 244  # G
        paper[:, :, 2] = 247  # R

        # Subtle noise grain
        noise = np.random.normal(0, 3.5, (h, w)).astype(np.float32)
        for c in range(3):
            ch = paper[:, :, c].astype(np.float32) + noise
            paper[:, :, c] = np.clip(ch, 220, 255).astype(np.uint8)

        # Subtle sketchbook border vignette
        cv2.rectangle(paper, (15, 15), (w - 15, h - 15), (215, 222, 225), 2)
        cv2.rectangle(paper, (20, 20), (w - 20, h - 20), (225, 230, 233), 1)
        return paper

    def _extract_ordered_strokes(self, mask):
        """Extracts continuous polyline strokes from a binary mask"""
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        # Sort contours from largest to smallest
        contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)
        strokes = []
        for c in contours:
            pts = c.reshape(-1, 2)
            if len(pts) > 3:
                step = max(1, len(pts) // 30)
                sub_pts = pts[::step]
                strokes.append(sub_pts)
        return strokes

    def render_sketch_video(self, input_image_path, object_display_name, output_video_path):
        """
        Renders complete ~38-second pencil sketching video at 1080x1920 (9:16).
        """
        output_video_path = Path(output_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[*] Sketch Engine rendering video: '{output_video_path.name}'...")

        src_img = cv2.imread(str(input_image_path))
        if src_img is None:
            raise FileNotFoundError(f"Cannot load image: {input_image_path}")

        # Target paper canvas area (central drawing zone)
        cw, ch = 960, 1360
        cx = (self.vw - cw) // 2
        cy = 240

        # Scale source image to fit canvas cleanly
        ih, iw = src_img.shape[:2]
        scale = min((cw - 60) / iw, (ch - 60) / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        scaled_img = cv2.resize(src_img, (nw, nh), interpolation=cv2.INTER_LANCZOS4)

        # Convert to graphite grayscale
        gray = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray

        # Stage Masks
        # 1. Light lines (construction lines)
        _, light_mask = cv2.threshold(inv, 25, 255, cv2.THRESH_BINARY)
        # 2. Dark lines (structural contours)
        _, dark_mask = cv2.threshold(inv, 65, 255, cv2.THRESH_BINARY)
        # 3. Shading mask (graphite tones)
        shading_mask = np.clip((inv.astype(np.float32) / 255.0) * 1.5, 0, 1)

        light_strokes = self._extract_ordered_strokes(light_mask)
        dark_strokes = self._extract_ordered_strokes(dark_mask)

        ox = cx + (cw - nw) // 2
        oy = cy + (ch - nh) // 2

        # Video Writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_video_path), fourcc, self.fps, (self.vw, self.vh))

        # Timing (Total 38.0s = 1140 frames)
        frames_stage1 = int(9.0 * self.fps)   # 0s - 9s: Light Construction (270 frames)
        frames_stage2 = int(11.0 * self.fps)  # 9s - 20s: Deep Contours (330 frames)
        frames_stage3 = int(11.0 * self.fps)  # 20s - 31s: Shading & Texture (330 frames)
        frames_stage4 = int(4.0 * self.fps)   # 31s - 35s: Reveal Polish (120 frames)
        frames_stage5 = int(3.0 * self.fps)   # 35s - 38s: Subscribe CTA (90 frames)
        total_frames = frames_stage1 + frames_stage2 + frames_stage3 + frames_stage4 + frames_stage5

        print(f"    Total frames to render: {total_frames} (~38.0s)")

        # Generate base paper canvas
        paper_canvas = self._generate_paper_texture(self.vh, self.vw)

        # Header Title on Paper (Clean artist lettering)
        cv2.putText(
            paper_canvas, "PENCIL SKETCH TUTORIAL",
            (cx + 20, 110), cv2.FONT_HERSHEY_DUPLEX, 0.9, (120, 120, 125), 2, cv2.LINE_AA
        )
        display_title = f"How to draw: {object_display_name}"[:32]
        cv2.putText(
            paper_canvas, display_title,
            (cx + 20, 175), cv2.FONT_HERSHEY_DUPLEX, 1.15, (40, 40, 45), 2, cv2.LINE_AA
        )
        cv2.line(paper_canvas, (cx + 20, 205), (cx + cw - 20, 205), (180, 185, 190), 2)

        # Active drawing canvas (starts as white paper)
        art_layer = np.ones((nh, nw, 3), dtype=np.uint8) * 255

        # All points for Stage 1
        flat_light = [pt for s in light_strokes for pt in s]
        if not flat_light:
            flat_light = [(nw // 2, nh // 2)]

        # All points for Stage 2
        flat_dark = [pt for s in dark_strokes for pt in s]
        if not flat_dark:
            flat_dark = [(nw // 2, nh // 2)]

        pencil_tip_offset = (10, 175)  # Tip location in pencil image

        # ==========================================
        # STAGE 1: LIGHT CONSTRUCTION (0s - 9s)
        # ==========================================
        print("    -> Rendering Stage 1: Light Construction Lines...")
        pts_per_frame_1 = max(1, len(flat_light) // frames_stage1)
        drawn_idx_1 = 0

        for f in range(frames_stage1):
            frame = paper_canvas.copy()
            next_idx = min(len(flat_light), drawn_idx_1 + pts_per_frame_1 * 2)

            for i in range(drawn_idx_1, next_idx):
                pt = flat_light[i]
                # Draw faint graphite pencil point (light gray 190)
                cv2.circle(art_layer, (int(pt[0]), int(pt[1])), 2, (190, 190, 190), -1, lineType=cv2.LINE_AA)

            drawn_idx_1 = next_idx
            cur_pt = flat_light[min(len(flat_light) - 1, drawn_idx_1)]

            # Place art layer on paper
            frame[oy:oy+nh, ox:ox+nw] = cv2.addWeighted(
                frame[oy:oy+nh, ox:ox+nw], 0.15, art_layer, 0.85, 0
            )

            # Draw moving pencil cursor
            px = ox + cur_pt[0] - pencil_tip_offset[0]
            py = oy + cur_pt[1] - pencil_tip_offset[1]
            frame = self._overlay_alpha(frame, self.pencil_img, px, py)

            # Stage label
            cv2.putText(frame, "STAGE 1: LIGHT OUTLINE (2H)", (cx + 20, cy + ch + 50),
                        cv2.FONT_HERSHEY_DUPLEX, 0.75, (100, 100, 110), 2, cv2.LINE_AA)
            writer.write(frame)

        # ==========================================
        # STAGE 2: DEEP CONTOURS (9s - 20s)
        # ==========================================
        print("    -> Rendering Stage 2: Deep Graphite Contours...")
        pts_per_frame_2 = max(1, len(flat_dark) // frames_stage2)
        drawn_idx_2 = 0

        for f in range(frames_stage2):
            frame = paper_canvas.copy()
            next_idx = min(len(flat_dark), drawn_idx_2 + pts_per_frame_2 * 2)

            for i in range(drawn_idx_2, next_idx):
                pt = flat_dark[i]
                # Draw dark crisp graphite pencil stroke (dark gray 50-70)
                cv2.circle(art_layer, (int(pt[0]), int(pt[1])), 2, (60, 60, 60), -1, lineType=cv2.LINE_AA)

            drawn_idx_2 = next_idx
            cur_pt = flat_dark[min(len(flat_dark) - 1, drawn_idx_2)]

            frame[oy:oy+nh, ox:ox+nw] = cv2.addWeighted(
                frame[oy:oy+nh, ox:ox+nw], 0.15, art_layer, 0.85, 0
            )

            px = ox + cur_pt[0] - pencil_tip_offset[0]
            py = oy + cur_pt[1] - pencil_tip_offset[1]
            frame = self._overlay_alpha(frame, self.pencil_img, px, py)

            cv2.putText(frame, "STAGE 2: DEFINING CONTOURS (2B)", (cx + 20, cy + ch + 50),
                        cv2.FONT_HERSHEY_DUPLEX, 0.75, (60, 60, 70), 2, cv2.LINE_AA)
            writer.write(frame)

        # ==========================================
        # STAGE 3: SHADING & TEXTURE (20s - 31s)
        # ==========================================
        print("    -> Rendering Stage 3: Graphite Shading & Depth...")
        target_bgr = scaled_img.copy()

        for f in range(frames_stage3):
            frame = paper_canvas.copy()
            progress = (f + 1) / frames_stage3

            # Progressive shading reveal via vertical + radial blend
            alpha_map = np.clip((shading_mask * progress * 1.3), 0, 1)[:, :, np.newaxis]
            shaded_current = (
                (1.0 - alpha_map) * art_layer.astype(np.float32) +
                alpha_map * target_bgr.astype(np.float32)
            ).astype(np.uint8)

            frame[oy:oy+nh, ox:ox+nw] = cv2.addWeighted(
                frame[oy:oy+nh, ox:ox+nw], 0.10, shaded_current, 0.90, 0
            )

            # Orbiting shading motion with pencil
            angle = f * 0.28
            radius = min(nw, nh) * 0.28
            px = int(ox + nw // 2 + math.cos(angle) * radius - pencil_tip_offset[0])
            py = int(oy + nh // 2 + math.sin(angle * 1.5) * radius * 0.7 - pencil_tip_offset[1])
            frame = self._overlay_alpha(frame, self.pencil_img, px, py)

            cv2.putText(frame, "STAGE 3: SHADING & TEXTURE (4B)", (cx + 20, cy + ch + 50),
                        cv2.FONT_HERSHEY_DUPLEX, 0.75, (40, 40, 50), 2, cv2.LINE_AA)
            writer.write(frame)

        # ==========================================
        # STAGE 4: MASTERPIECE REVEAL (31s - 35s)
        # ==========================================
        print("    -> Rendering Stage 4: Masterpiece Reveal...")
        for f in range(frames_stage4):
            progress = f / max(1, frames_stage4)
            zoom = 1.0 + 0.05 * progress

            frame = paper_canvas.copy()
            frame[oy:oy+nh, ox:ox+nw] = cv2.addWeighted(
                frame[oy:oy+nh, ox:ox+nw], 0.08, scaled_img, 0.92, 0
            )

            # Elegant reveal banner
            cv2.putText(frame, "COMPLETED PENCIL DRAWING", (cx + 20, cy + ch + 50),
                        cv2.FONT_HERSHEY_DUPLEX, 0.85, (20, 130, 40), 2, cv2.LINE_AA)
            writer.write(frame)

        # ==========================================
        # STAGE 5: SUBSCRIBE CALL-TO-ACTION (35s - 38s)
        # ==========================================
        print("    -> Rendering Stage 5: Subscribe Call-To-Action...")
        for f in range(frames_stage5):
            frame = paper_canvas.copy()
            frame[oy:oy+nh, ox:ox+nw] = cv2.addWeighted(
                frame[oy:oy+nh, ox:ox+nw], 0.08, scaled_img, 0.92, 0
            )

            # Semi-transparent dark bottom card for CTA
            card_h = 240
            card_y = self.vh - card_h - 120
            overlay = frame.copy()
            cv2.rectangle(overlay, (cx, card_y), (cx + cw, card_y + card_h), (25, 25, 30), -1)
            cv2.rectangle(overlay, (cx, card_y), (cx + cw, card_y + card_h), (220, 50, 50), 3)
            frame = cv2.addWeighted(overlay, 0.88, frame, 0.12, 0)

            # CTA Text
            cv2.putText(
                frame, "WHAT SHOULD I SKETCH NEXT?",
                (cx + 40, card_y + 70), cv2.FONT_HERSHEY_DUPLEX, 1.05, (255, 255, 255), 2, cv2.LINE_AA
            )
            cv2.putText(
                frame, "Leave a comment & SUBSCRIBE for daily art!",
                (cx + 40, card_y + 130), cv2.FONT_HERSHEY_DUPLEX, 0.80, (200, 200, 200), 1, cv2.LINE_AA
            )

            # Draw Subscribe Button
            if self.sub_btn_img is not None:
                sb_w = 260
                sb_h = int(self.sub_btn_img.shape[0] * (sb_w / self.sub_btn_img.shape[1]))
                sb_resized = cv2.resize(self.sub_btn_img, (sb_w, sb_h))
                sb_x = cx + (cw - sb_w) // 2
                sb_y = card_y + 155
                frame = self._overlay_alpha(frame, sb_resized, sb_x, sb_y)

            writer.write(frame)

        writer.release()
        print(f"[+] Sketch video successfully rendered: {output_video_path}")
        return str(output_video_path)


if __name__ == "__main__":
    engine = SketchEngine()
    test_img = TEMP_DIR / "test_pencil_pear.jpg"
    test_out = TEMP_DIR / "test_sketch_output.mp4"
    if test_img.exists():
        engine.render_sketch_video(test_img, "Pear", test_out)
