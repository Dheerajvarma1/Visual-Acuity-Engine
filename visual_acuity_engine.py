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

    def render_landolt_c(self, acuity_key, orientation):
        """
        Render the Landolt C optotype on a canvas.
        Orientation: 'Up', 'Down', 'Left', 'Right'
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
            
        if height_px < 5.0:
            # If size is very small, display minimum visible size (5px height)
            # and warn in console.
            # 5px height allows for 1px gap and 1px stroke.
            scale = 5.0 / height_px
            height_px = 5.0
            gap_px = gap_px * scale
            warning = f"Warning: {name} stimulus size very small (calculated height {5.0 / scale:.2f}px < 5px), using minimum visible size (5px)."

        # Create canvas (White background)
        canvas = np.ones((self.resolution[1], self.resolution[0], 3), dtype=np.uint8) * 255
        
        # Center coordinates
        center_x, center_y = self.resolution[0] // 2, self.resolution[1] // 2
        
        # Draw Landolt C (Black circle with a hole and a gap)
        # Outer radius = height_px / 2
        # Inner radius = (height_px - 2 * stroke) / 2 = (5g - 2g) / 2 = 3g / 2
        outer_radius = int(round(height_px / 2))
        inner_radius = int(round(3 * gap_px / 2))
        stroke = int(round(gap_px))
        
        # Draw the ring
        cv2.circle(canvas, (center_x, center_y), outer_radius, (0, 0, 0), -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (center_x, center_y), inner_radius, (255, 255, 255), -1, lineType=cv2.LINE_AA)
        
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
        
        # Draw the white gap
        cv2.fillPoly(canvas, [rotated_pts.astype(np.int32)], (255, 255, 255), lineType=cv2.LINE_AA)
        
        # Labels
        cv2.putText(canvas, f"Acuity: {name}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(canvas, f"Orientation: {orientation}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(canvas, "Keys: 1-4 (Acuity), W/A/S/D (Response), ESC (Exit)", (20, self.resolution[1] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        return canvas, warning

if __name__ == "__main__":
    # Test
    engine = VisualAcuityEngine()
    canvas, warn = engine.render_landolt_c('1', 'Right')
    if warn: print(warn)
    cv2.imshow("Test", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
