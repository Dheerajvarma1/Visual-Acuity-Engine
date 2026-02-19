import numpy as np
import cv2
import math

class VisualAcuityEngine:
    """
    Core engine for calculating stimulus sizes and rendering Landolt C optotypes.
    """
    def __init__(self, viewing_distance_mm=100.0, display_ppi=300.0, resolution=(800, 600)):
        self.viewing_distance_mm = viewing_distance_mm
        self.display_ppi = display_ppi
        self.resolution = resolution  # (width, height)
        
        # Visual Acuity Levels: (Name, Gap Angle in arc minutes)
        self.acuity_levels = {
            '1': ('6/6', 1.0),
            '2': ('6/12', 2.0),
            '3': ('6/18', 3.0),
            '4': ('6/60', 10.0)
        }

    def arcmin_to_rad(self, arcmin):
        """Convert arc minutes to radians."""
        return arcmin * (math.pi / (180.0 * 60.0))

    def visual_angle_to_mm(self, angle_rad):
        """Convert visual angle (radians) to physical size (mm) using tan(theta)."""
        # Using tan(theta) as specified in requirements
        return self.viewing_distance_mm * math.tan(angle_rad)

    def mm_to_pixels(self, size_mm):
        """Convert physical size (mm) to pixels based on display PPI."""
        # 1 inch = 25.4 mm
        return size_mm * (self.display_ppi / 25.4)

    def calculate_sizes_px(self, arcmin):
        """
        Calculate gap size and total letter height in pixels for a given arc minute angle.
        """
        angle_rad = self.arcmin_to_rad(arcmin)
        gap_mm = self.visual_angle_to_mm(angle_rad)
        gap_px = self.mm_to_pixels(gap_mm)
        
        # Total height = 5 * gap size
        # Stroke width = gap size
        height_px = 5 * gap_px
        
        return gap_px, height_px

    def render_landolt_c(self, acuity_key, orientation, adaptive_mode=False, dark_mode=False, hide_hud=False):
        """
        Render the Landolt C optotype on a canvas.
        Orientation: 'Up', 'Down', 'Left', 'Right'
        adaptive_mode: If True, display adaptive indicator on HUD.
        dark_mode: If True, white C on black; else black C on white.
        hide_hud: If True, hide acuity/orientation/adaptive labels (clean view).
        """
        if acuity_key not in self.acuity_levels:
            return None, "Invalid Acuity Level"
            
        name, arcmin = self.acuity_levels[acuity_key]
        gap_px, height_px = self.calculate_sizes_px(arcmin)
        
        # Constraints check
        warning = None
        if height_px > min(self.resolution):
            # Scale down proportionally if it exceeds screen
            scale = min(self.resolution) / height_px
            height_px = min(self.resolution)
            gap_px = gap_px * scale
            warning = f"Warning: {name} stimulus exceeds screen size, scaled down."
            
        if height_px < 2.0:
            scale = 2.0 / height_px
            height_px = 2.0
            gap_px = gap_px * scale
            warning = f"Warning: {name} stimulus size very small (calculated height {2.0 / scale:.2f}px < 2px), using minimum visible size."

        # Theme colors
        if dark_mode:
            bg_color      = (0, 0, 0)        # Black background
            ring_color    = (255, 255, 255)  # White C
            hole_color    = (0, 0, 0)        # Black hole
            gap_color     = (0, 0, 0)        # Black gap
            text_color    = (255, 255, 255)  # White text
            hint_color    = (160, 160, 160)  # Light grey hint
        else:
            bg_color      = (255, 255, 255)  # White background
            ring_color    = (0, 0, 0)        # Black C
            hole_color    = (255, 255, 255)  # White hole
            gap_color     = (255, 255, 255)  # White gap
            text_color    = (0, 0, 0)        # Black text
            hint_color    = (100, 100, 100)  # Dark grey hint

        # Create canvas
        canvas = np.full((self.resolution[1], self.resolution[0], 3), bg_color, dtype=np.uint8)
        
        # Center coordinates
        center_x, center_y = self.resolution[0] // 2, self.resolution[1] // 2
        
        # Draw Landolt C (Black circle with a hole and a gap)
        # Outer radius = height_px / 2
        # Inner radius = (height_px - 2 * stroke) / 2 = (5g - 2g) / 2 = 3g / 2
        outer_radius = int(round(height_px / 2))
        inner_radius = int(round(3 * gap_px / 2))
        stroke = int(round(gap_px))
        
        # Draw the ring
        cv2.circle(canvas, (center_x, center_y), outer_radius, ring_color, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (center_x, center_y), inner_radius, hole_color, -1, lineType=cv2.LINE_AA)
        
        # Draw the gap
        # The gap is a rectangle of width 'stroke' and extends from center to outer edge
        # We can draw a white rectangle over the ring
        
        gap_rect_width = stroke
        gap_rect_height = outer_radius + 5 # Extra for overlap
        
        # Define the rotation angle based on orientation
        # 0: Right, 90: Down, 180: Left, 270: Up
        angles = {
            'Right': 0,
            'Down': 90,
            'Left': 180,
            'Up': 270
        }
        angle = angles.get(orientation, 0)
        
        # Create a overlay with transparency for anti-aliasing if needed, 
        # but for simplicity we use rotation matrix on a rectangle
        
        # Coordinates of the gap rectangle relative to center
        # It should cover the area where the gap should be
        pts = np.array([
            [0, -gap_rect_width / 2],
            [gap_rect_height, -gap_rect_width / 2],
            [gap_rect_height, gap_rect_width / 2],
            [0, gap_rect_width / 2]
        ])
        
        # Rotate points
        rad = math.radians(angle)
        rot_matrix = np.array([
            [math.cos(rad), -math.sin(rad)],
            [math.sin(rad), math.cos(rad)]
        ])
        rotated_pts = pts @ rot_matrix.T
        rotated_pts = rotated_pts + [center_x, center_y]
        
        # Draw the gap
        cv2.fillPoly(canvas, [rotated_pts.astype(np.int32)], gap_color, lineType=cv2.LINE_AA)

        # Top HUD labels (hidden when hide_hud=True)
        if not hide_hud:
            cv2.putText(canvas, f"Acuity: {name}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
            cv2.putText(canvas, f"Orientation: {orientation}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)

            # Adaptive mode badge
            mode_label = "[ ADAPTIVE MODE: ON ]"
            mode_color = (0, 220, 0) if dark_mode else (0, 150, 0)
            if not adaptive_mode:
                mode_label = "[ ADAPTIVE MODE: OFF ]"
                mode_color = hint_color
            cv2.putText(canvas, mode_label, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.55, mode_color, 2)

            # Theme indicator (always visible unless hidden)
            theme_label = "[ THEME: DARK ]" if dark_mode else "[ THEME: LIGHT ]"
            cv2.putText(canvas, theme_label, (620, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, hint_color, 1)

            cv2.putText(canvas,
                        "1-4 (Acuity) | W/A/S/D/Arrows (Respond) | M (Adaptive) | T (Theme) | F (Fullscreen) | H (Hide HUD) | ESC (Exit)",
                        (10, self.resolution[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36, hint_color, 1)

        return canvas, warning

    def _draw_single_c(self, canvas, center, height_px, gap_px, orientation, color, bg_color):
        """Helper to draw a single Landolt C."""
        cx, cy = center
        outer_radius = height_px / 2.0
        inner_radius = outer_radius * 0.6
        
        # 1. Full circle
        cv2.circle(canvas, (cx, cy), int(outer_radius), color, -1, lineType=cv2.LINE_AA)
        
        # 2. Inner hole
        cv2.circle(canvas, (cx, cy), int(inner_radius), bg_color, -1, lineType=cv2.LINE_AA)
        
        # 3. Gap
        gap_w = gap_px
        gap_h = outer_radius + 2
        
        # Define rectangle centered at (0,0)
        pts = np.array([
            [0, -gap_w/2],
            [gap_h, -gap_w/2],
            [gap_h, gap_w/2],
            [0, gap_w/2]
        ])
        
        # Rotate
        angle = 0
        if orientation == 'Up': angle = -90
        elif orientation == 'Down': angle = 90
        elif orientation == 'Left': angle = 180
        elif orientation == 'Right': angle = 0
            
        theta = np.radians(angle)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        
        rotated_pts = pts.dot(R.T)
        rotated_pts[:, 0] += cx
        rotated_pts[:, 1] += cy
        
        # Draw gap
        cv2.fillPoly(canvas, [rotated_pts.astype(np.int32)], bg_color, lineType=cv2.LINE_AA)

    def render_chart_mode(self, dark_mode=False, hide_hud=False):
        """Renders a multi-optotype chart with rows of decreasing size."""
        # Colors
        if dark_mode:
            bg_color = (0, 0, 0); text_color = (255, 255, 255); hint_color = (100, 100, 100)
        else:
            bg_color = (255, 255, 255); text_color = (0, 0, 0); hint_color = (180, 180, 180)
            
        canvas = np.full((self.resolution[1], self.resolution[0], 3), bg_color, dtype=np.uint8)
        
        # Define rows: (Acuity Key, Y-position, Count)
        # 6/60 (Key '4'), 6/18 ('3'), 6/12 ('2'), 6/6 ('1')
        rows = [
            ('4', 150, 2), 
            ('3', 280, 3), 
            ('2', 380, 4), 
            ('1', 460, 5)
        ]
        
        import random
        orientations = ['Up', 'Down', 'Left', 'Right']
        
        for key, y_pos, count in rows:
            name = self.acuity_levels[key][0]
            arcmin = self.acuity_levels[key][1]
            gap_px, height_px = self.calculate_sizes_px(arcmin)
            
            # Clamp logic (same as main renderer to ensure visibility)
            if height_px < 2.0:
                scale = 2.0 / height_px
                height_px = 2.0
                gap_px = gap_px * scale
            
            # Spacing
            total_width = self.resolution[0]
            spacing = total_width / (count + 1)
            
            for i in range(count):
                x_pos = int(spacing * (i + 1))
                ori = random.choice(orientations)
                self._draw_single_c(canvas, (x_pos, y_pos), height_px, gap_px, ori, text_color, bg_color)
            
            # Draw row label
            if not hide_hud:
                cv2.putText(canvas, name, (int(spacing * count) + 60, y_pos + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, hint_color, 1)

        if not hide_hud:
             mode_title = "[ CHART MODE ]"
             cv2.putText(canvas, mode_title, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
             
             # Theme indicator
             theme_label = "[ THEME: DARK ]" if dark_mode else "[ THEME: LIGHT ]"
             cv2.putText(canvas, theme_label, (620, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, hint_color, 1)
             
             cv2.putText(canvas,
                        "C (Switch Mode) | T (Theme) | F (Fullscreen) | H (Hide HUD) | ESC (Exit)",
                        (10, self.resolution[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36, hint_color, 1)
                        
        return canvas

if __name__ == "__main__":
    # Test
    engine = VisualAcuityEngine()
    canvas, warn = engine.render_landolt_c('1', 'Right')
    if warn: print(warn)
    cv2.imshow("Test", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
