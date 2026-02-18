from visual_acuity_engine import VisualAcuityEngine
import math

def test_calculations():
    engine = VisualAcuityEngine(viewing_distance_mm=100.0, display_ppi=300.0)
    
    print(f"{'Acuity':<10} | {'Angle (min)':<12} | {'Gap (px)':<10} | {'Height (px)':<12}")
    print("-" * 55)
    
    for key, (name, arcmin) in engine.acuity_levels.items():
        gap_px, height_px = engine.calculate_sizes_px(arcmin)
        print(f"{name:<10} | {arcmin:<12.1f} | {gap_px:<10.3f} | {height_px:<12.3f}")

if __name__ == "__main__":
    test_calculations()
