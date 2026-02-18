import cv2
import csv
import time
import os
import random
from datetime import datetime
from visual_acuity_engine import VisualAcuityEngine

def main():
    # Initialize Engine
    # PPI 300, Dist 100mm, Res 800x600 as per requirements
    engine = VisualAcuityEngine(viewing_distance_mm=100.0, display_ppi=300.0, resolution=(800, 600))
    
    # State
    current_acuity_key = '1'
    current_orientation = 'Right'
    log_file = 'acuity_logs.csv'
    
    # Create window
    window_name = "Visual Acuity Stimulus Engine (Landolt C)"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    
    # CSV Setup
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Acuity Level', 'True Orientation', 'User Response', 'Result'])

    print("Engine Started.")
    print("Keys: 1-4 (Acuity Levels), W/A/S/D (Respond Direction), ESC (Exit)")

    while True:
        # Render
        canvas, warning = engine.render_landolt_c(current_acuity_key, current_orientation)
        if warning:
            print(warning)
            
        cv2.imshow(window_name, canvas)
        
        # Key handling
        key = cv2.waitKey(0)
        
        # Exit on ESC
        if key == 27:
            break
            
        # Acuity switching
        if ord('1') <= key <= ord('4'):
            current_acuity_key = chr(key)
            # When changing acuity, randomize orientation for a new trial (Optional Bonus)
            current_orientation = random.choice(['Up', 'Down', 'Left', 'Right'])
            continue

        # Orientation / Response handling
        user_response = None
        # OpenCV waitKey values for arrows can vary by OS, but common ones:
        # Up: 2424832 or 82, Down: 2555904 or 84, Left: 2490368 or 81, Right: 2621440 or 83
        # Using cross-platform values from cv2 indexing if possible or standard ASCII
        
        # Standard Arrow Keys in most OS for cv2.waitKey:
        # Top: 0 (or 2490368), Down: 1 (or 2621440), etc is not reliable
        # We'll use the specific codes for Windows/Linux
        
        if key == ord('w'): user_response = 'Up'
        elif key == ord('s'): user_response = 'Down'
        elif key == ord('a'): user_response = 'Left'
        elif key == ord('d'): user_response = 'Right'

        if user_response:
            # Result calculation
            result = "Correct" if user_response == current_orientation else "Incorrect"
            acuity_name = engine.acuity_levels[current_acuity_key][0]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log to CSV
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, acuity_name, current_orientation, user_response, result])
            
            print(f"Logged: {acuity_name}, True: {current_orientation}, User: {user_response}, Result: {result}")
            
            # Change orientation for next trial
            current_orientation = random.choice(['Up', 'Down', 'Left', 'Right'])

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
