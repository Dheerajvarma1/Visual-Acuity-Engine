import cv2
import csv
import os
import random
from datetime import datetime
from visual_acuity_engine import VisualAcuityEngine

# Acuity key sequence: '1' = 6/6 (hardest) ... '4' = 6/60 (easiest)
ACUITY_SEQUENCE = ['1', '2', '3', '4']


def step_acuity(current_key, direction):
    """
    Adaptively step the acuity level.
    direction='harder' → move toward '1' (6/6, smaller gap).
    direction='easier' → move toward '4' (6/60, larger gap).
    Returns the new key (clamped at boundaries).
    """
    idx = ACUITY_SEQUENCE.index(current_key)
    if direction == 'harder':
        idx = max(0, idx - 1)
    else:
        idx = min(len(ACUITY_SEQUENCE) - 1, idx + 1)
    return ACUITY_SEQUENCE[idx]


def main():
    # Initialize Engine
    engine = VisualAcuityEngine(viewing_distance_mm=100.0, display_ppi=300.0, resolution=(800, 600))

    # State
    current_acuity_key = '2'            # Start at 6/12 (mid-range)
    current_orientation = random.choice(['Up', 'Down', 'Left', 'Right'])
    adaptive_mode = True                # Toggle with 'M'
    dark_mode = False                   # Toggle with 'T' (starts light)
    fullscreen = False                  # Toggle with 'F'
    hide_hud = False                    # Toggle with 'H'
    log_file = 'acuity_logs.csv'

    # Create window (WINDOW_NORMAL allows resizing and fullscreen)
    window_name = "Visual Acuity Stimulus Engine (Landolt C)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    # CSV Setup
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'Timestamp', 'Acuity Level', 'True Orientation',
                'User Response', 'Result', 'Mode'
            ])

    print("Engine Started.")
    print("Keys: 1-4 (Acuity), W/A/S/D (Respond), M (Adaptive), T (Theme), F (Fullscreen), ESC (Exit)")
    print(f"Adaptive Mode: {'ON' if adaptive_mode else 'OFF'} | Theme: {'Dark' if dark_mode else 'Light'}")

    while True:
        # Render
        canvas, warning = engine.render_landolt_c(
            current_acuity_key, current_orientation, adaptive_mode, dark_mode, hide_hud
        )
        if warning:
            print(warning)

        cv2.imshow(window_name, canvas)

        # waitKeyEx returns full extended keycodes — needed for arrow keys on Windows
        key = cv2.waitKeyEx(0)

        # Exit on ESC
        if key == 27:
            break

        # Toggle adaptive mode with 'M'
        if key == ord('m') or key == ord('M'):
            adaptive_mode = not adaptive_mode
            print(f"Adaptive Mode: {'ON' if adaptive_mode else 'OFF'}")
            continue

        # Toggle theme with 'T'
        if key == ord('t') or key == ord('T'):
            dark_mode = not dark_mode
            print(f"Theme: {'Dark' if dark_mode else 'Light'}")
            continue

        # Toggle fullscreen with 'F'
        if key == ord('f') or key == ord('F'):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 800, 600)
            print(f"Fullscreen: {'ON' if fullscreen else 'OFF'}")
            continue

        # Toggle HUD visibility with 'H'
        if key == ord('h') or key == ord('H'):
            hide_hud = not hide_hud
            print(f"HUD: {'Hidden' if hide_hud else 'Visible'}")
            continue

        # Manual acuity switching (disables adaptive for that pick)
        if ord('1') <= key <= ord('4'):
            current_acuity_key = chr(key)
            current_orientation = random.choice(['Up', 'Down', 'Left', 'Right'])
            print(f"Manual override → {engine.acuity_levels[current_acuity_key][0]}")
            continue

        # Response handling — WASD and Arrow keys
        user_response = None
        # Arrow key codes returned by cv2.waitKeyEx() on Windows:
        # Up=2490368, Down=2621440, Left=2424832, Right=2555904
        if   key == ord('w') or key == 2490368: user_response = 'Up'
        elif key == ord('s') or key == 2621440: user_response = 'Down'
        elif key == ord('a') or key == 2424832: user_response = 'Left'
        elif key == ord('d') or key == 2555904: user_response = 'Right'

        if user_response:
            result = "Correct" if user_response == current_orientation else "Incorrect"
            acuity_name = engine.acuity_levels[current_acuity_key][0]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mode_label = "Adaptive" if adaptive_mode else "Manual"

            # Log to CSV
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, acuity_name, current_orientation,
                    user_response, result, mode_label
                ])

            print(f"[{mode_label}] {acuity_name} | True: {current_orientation} | "
                  f"User: {user_response} | {result}")

            # Adaptive stepping
            if adaptive_mode:
                if result == "Correct":
                    new_key = step_acuity(current_acuity_key, 'harder')
                    if new_key != current_acuity_key:
                        print(f"  → Stepping HARDER: {engine.acuity_levels[new_key][0]}")
                    else:
                        print(f"  → Already at hardest level (6/6).")
                else:
                    new_key = step_acuity(current_acuity_key, 'easier')
                    if new_key != current_acuity_key:
                        print(f"  → Stepping EASIER: {engine.acuity_levels[new_key][0]}")
                    else:
                        print(f"  → Already at easiest level (6/60).")
                current_acuity_key = new_key

            # Randomize orientation for next trial
            current_orientation = random.choice(['Up', 'Down', 'Left', 'Right'])

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
