"""
Paint Animation Engine (100% English UI - US/Global View)
Renders a 9:16 vertical video simulating the entire drawing process in Microsoft Paint:
1. Hook & Finished Art Preview (0s - 3s)
2. Pencil Sketching with Mouse Cursor (3s - 14s)
3. Palette Picking & Color Fill (14s - 24s)
4. Final Reveal (24s - 27s)
5. Animated Like & Subscribe Cursor Click (27s - 30s)
"""
import sys
import math
import cv2
import numpy as np
from pathlib import Path
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS,
    DURATION_HOOK, DURATION_SKETCH, DURATION_COLOR, DURATION_REVEAL, DURATION_CTA,
    ASSETS_DIR, TEMP_DIR
)


class PaintEngine:
    def __init__(self):
        self.vw = VIDEO_WIDTH
        self.vh = VIDEO_HEIGHT
        self.fps = FPS
        self._load_assets()

    def _load_assets(self):
        """Load UI elements and cursor"""
        self.cursor_img = cv2.imread(str(ASSETS_DIR / "cursor.png"), cv2.IMREAD_UNCHANGED)
        self.header_img = cv2.imread(str(ASSETS_DIR / "paint_header.png"))
        self.footer_img = cv2.imread(str(ASSETS_DIR / "paint_footer.png"))
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

    def _generate_pencil_sketch(self, color_img):
        """Generates clean pencil sketch line art from color image"""
        gray = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (15, 15), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        return sketch_bgr, sketch

    def _extract_strokes(self, sketch_gray):
        """Extract ordered polyline strokes from pencil sketch"""
        _, bin_edges = cv2.threshold(sketch_gray, 225, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(bin_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        # Sort contours from largest to smallest
        contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)
        strokes = []
        for c in contours:
            pts = c.reshape(-1, 2)
            if len(pts) > 2:
                step = max(1, len(pts) // 15)
                sub_pts = pts[::step]
                strokes.append(sub_pts)
        return strokes

    def render_animation(self, input_image_path, title_text, output_video_path):
        """
        Renders the complete MS Paint video sequence in English.
        """
        output_video_path = Path(output_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[*] Paint Engine rendering video: '{output_video_path.name}'...")

        src_img = cv2.imread(str(input_image_path))
        if src_img is None:
            raise FileNotFoundError(f"Cannot load image: {input_image_path}")

        # Dimensions & Layout Setup
        hw = 1040
        hx = (self.vw - hw) // 2
        hy = 160
        hh = int(self.header_img.shape[0] * (hw / self.header_img.shape[1]))
        header_resized = cv2.resize(self.header_img, (hw, hh))

        cw = hw
        ch = 1350
        cy = hy + hh

        fh = int(self.footer_img.shape[0] * (hw / self.footer_img.shape[1]))
        footer_resized = cv2.resize(self.footer_img, (hw, fh))
        fy = cy + ch

        # Scale source image to fit paper canvas cleanly
        ih, iw = src_img.shape[:2]
        scale = min((cw - 40) / iw, (ch - 40) / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        scaled_color = cv2.resize(src_img, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
        
        scaled_sketch_bgr, scaled_sketch_gray = self._generate_pencil_sketch(scaled_color)
        strokes = self._extract_strokes(scaled_sketch_gray)

        ox = hx + (cw - nw) // 2
        oy = cy + (ch - nh) // 2

        # Video Writer Setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_video_path), fourcc, self.fps, (self.vw, self.vh))

        frames_hook = int(DURATION_HOOK * self.fps)        # ~90
        frames_sketch = int(DURATION_SKETCH * self.fps)    # ~330
        frames_color = int(DURATION_COLOR * self.fps)      # ~300
        frames_reveal = int(DURATION_REVEAL * self.fps)    # ~90
        frames_cta = int(DURATION_CTA * self.fps)          # ~90
        total_frames = frames_hook + frames_sketch + frames_color + frames_reveal + frames_cta

        print(f"    Total frames to render: {total_frames} (~30s)")

        base_frame = np.ones((self.vh, self.vw, 3), dtype=np.uint8) * 235
        base_frame[hy:hy+hh, hx:hx+hw] = header_resized
        base_frame[fy:fy+fh, hx:hx+hw] = footer_resized

        # Draw top Short Hook Banner
        cv2.rectangle(base_frame, (0, 0), (self.vw, hy), (25, 25, 30), -1)
        cv2.line(base_frame, (0, hy-2), (self.vw, hy-2), (0, 180, 255), 3)

        # English Title text in header
        cv2.putText(
            base_frame, "MS PAINT CHALLENGE - 100% MOUSE ONLY",
            (hx + 10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.95, (255, 215, 0), 2, cv2.LINE_AA
        )
        safe_title = title_text[:38]
        cv2.putText(
            base_frame, safe_title,
            (hx + 10, 115), cv2.FONT_HERSHEY_DUPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA
        )

        flat_points = []
        for s in strokes:
            for pt in s:
                flat_points.append(pt)
        if not flat_points:
            flat_points = [(nw // 2, nh // 2)]

        # --- SECTION 1: HOOK (0s - 3s) ---
        print("    -> Rendering Hook (Finished Preview)...")
        for f in range(frames_hook):
            progress = f / max(1, frames_hook)
            zoom = 1.0 + 0.08 * progress
            
            preview = np.zeros((self.vh, self.vw, 3), dtype=np.uint8)
            blurred_bg = cv2.GaussianBlur(cv2.resize(src_img, (self.vw, self.vh)), (51, 51), 0)
            preview = (blurred_bg * 0.4).astype(np.uint8)

            sc = min((self.vw - 120) / iw, (self.vh - 400) / ih) * zoom
            snw, snh = int(iw * sc), int(ih * sc)
            resized_main = cv2.resize(src_img, (snw, snh))
            sx = (self.vw - snw) // 2
            sy = (self.vh - snh) // 2
            
            cv2.rectangle(preview, (sx-4, sy-4), (sx+snw+4, sy+snh+4), (255, 255, 255), 3)
            preview[sy:sy+snh, sx:sx+snw] = resized_main

            # Hook banner overlay
            cv2.rectangle(preview, (0, 80), (self.vw, 220), (0, 0, 0), -1)
            cv2.putText(
                preview, "CAN YOU BELIEVE THIS ARTWORK",
                (80, 135), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA
            )
            cv2.putText(
                preview, "WAS DRAWN 100% IN MS PAINT?",
                (100, 195), cv2.FONT_HERSHEY_DUPLEX, 1.35, (0, 220, 255), 3, cv2.LINE_AA
            )
            writer.write(preview)

        # --- SECTION 2: SKETCHING IN MS PAINT (3s - 14s) ---
        print("    -> Rendering Sketching Phase in MS Paint...")
        total_pts = len(flat_points)
        canvas_drawing = np.ones((nh, nw, 3), dtype=np.uint8) * 255

        for f in range(frames_sketch):
            progress = f / max(1, frames_sketch)
            curr_idx = int(progress * total_pts)
            
            prev_idx = int((f - 1) / max(1, frames_sketch) * total_pts) if f > 0 else 0
            for i in range(prev_idx, min(curr_idx + 1, total_pts)):
                pt = flat_points[i]
                cv2.circle(canvas_drawing, (pt[0], pt[1]), 2, (30, 30, 30), -1)

            frame = base_frame.copy()
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (255, 255, 255), -1)
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (180, 180, 180), 1)
            frame[oy:oy+nh, ox:ox+nw] = canvas_drawing

            tip = flat_points[min(curr_idx, total_pts - 1)]
            cursor_x = ox + tip[0] - 8
            cursor_y = oy + tip[1] - 8
            self._overlay_alpha(frame, self.cursor_img, cursor_x, cursor_y)

            writer.write(frame)

        # --- SECTION 3: COLORING IN MS PAINT (14s - 24s) ---
        print("    -> Rendering Coloring Phase in MS Paint...")
        canvas_drawing = scaled_sketch_bgr.copy()

        for f in range(frames_color):
            progress = f / max(1, frames_color)

            alpha_mask = np.zeros((nh, nw), dtype=np.float32)
            max_dist = math.sqrt((nw // 2) ** 2 + (nh // 2) ** 2)
            reveal_radius = progress * max_dist * 1.2
            
            y_coords, x_coords = np.ogrid[:nh, :nw]
            dist_from_center = np.sqrt((x_coords - nw // 2) ** 2 + (y_coords - nh // 2) ** 2)
            alpha_mask = np.clip((reveal_radius - dist_from_center) / 40.0, 0.0, 1.0)
            alpha_3d = np.repeat(alpha_mask[:, :, np.newaxis], 3, axis=2)

            colored_canvas = (
                alpha_3d * scaled_color + (1.0 - alpha_3d) * scaled_sketch_bgr
            ).astype(np.uint8)

            frame = base_frame.copy()
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (255, 255, 255), -1)
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (180, 180, 180), 1)
            frame[oy:oy+nh, ox:ox+nw] = colored_canvas

            angle = progress * 14 * math.pi
            r_orbit = min(nw // 3, progress * nw // 2.5)
            cx_orbit = int(nw // 2 + r_orbit * math.cos(angle))
            cy_orbit = int(nh // 2 + r_orbit * math.sin(angle))
            
            cursor_x = ox + np.clip(cx_orbit, 0, nw - 1) - 8
            cursor_y = oy + np.clip(cy_orbit, 0, nh - 1) - 8
            self._overlay_alpha(frame, self.cursor_img, cursor_x, cursor_y)

            writer.write(frame)

        # --- SECTION 4: FINAL REVEAL (24s - 27s) ---
        print("    -> Rendering Final Reveal...")
        for f in range(frames_reveal):
            frame = base_frame.copy()
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (255, 255, 255), -1)
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (180, 180, 180), 1)
            frame[oy:oy+nh, ox:ox+nw] = scaled_color

            # Sparkle / Finish Tag in English
            cv2.rectangle(frame, (hx + 20, fy - 70), (hx + 470, fy - 15), (0, 180, 0), -1)
            cv2.putText(
                frame, "FINISHED: 100% MS PAINT!",
                (hx + 30, fy - 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA
            )
            writer.write(frame)

        # --- SECTION 5: SUBSCRIBE & LIKE CTA (27s - 30s) ---
        print("    -> Rendering Subscribe CTA Click...")
        sub_w = 480
        sub_h = int(self.sub_btn_img.shape[0] * (sub_w / self.sub_btn_img.shape[1]))
        sub_resized = cv2.resize(self.sub_btn_img, (sub_w, sub_h))
        sub_x = (self.vw - sub_w) // 2
        sub_y = cy + (ch - sub_h) // 2 + 100

        for f in range(frames_cta):
            progress = f / max(1, frames_cta)
            frame = base_frame.copy()
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (255, 255, 255), -1)
            cv2.rectangle(frame, (hx, cy), (hx+cw, cy+ch), (180, 180, 180), 1)
            dimmed = (scaled_color * 0.75).astype(np.uint8)
            frame[oy:oy+nh, ox:ox+nw] = dimmed

            self._overlay_alpha(frame, sub_resized, sub_x, sub_y)

            start_cx, start_cy = sub_x - 80, sub_y + 120
            target_cx, target_cy = sub_x + sub_w // 2, sub_y + sub_h // 2
            
            cur_p = min(1.0, progress * 1.8)
            cur_x = int(start_cx + (target_cx - start_cx) * cur_p)
            cur_y = int(start_cy + (target_cy - start_cy) * cur_p)

            if progress > 0.6:
                cv2.circle(frame, (target_cx, target_cy), 25, (0, 255, 255), 3)

            self._overlay_alpha(frame, self.cursor_img, cur_x, cur_y)
            writer.write(frame)

        writer.release()
        print(f"[+] Raw video rendered to: {output_video_path}")
        return str(output_video_path)


if __name__ == "__main__":
    engine = PaintEngine()
    test_img = TEMP_DIR / "test_2k_caricature.jpg"
    test_video = TEMP_DIR / "test_paint_raw_en.mp4"
    engine.render_animation(test_img, "DRAWING CAT WITH MOUSE ONLY", test_video)
