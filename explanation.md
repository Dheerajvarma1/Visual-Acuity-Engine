# Visual Acuity Stimulus Engine: Technical Explanation

## 1. Visual Angle Implementation

The visual angle θ is the angle subtended at the eye by the target. For visual acuity, the critical dimension is the **gap size** of the Landolt C.

### Calculation Pipeline

**Step 1 — Arc minutes to Radians:**

$$\theta_{rad} = \text{arcmin} \times \frac{\pi}{180 \times 60}$$

**Step 2 — Visual Angle to Physical Size (mm):**

Given viewing distance $d = 100$ mm:

$$\text{gap}_{mm} = d \times \tan(\theta_{rad})$$

> **Choice**: I used the full `tan(θ)` function rather than the small-angle approximation `θ ≈ tan(θ)`. This ensures accurate results across a wider range of viewing distances and angles.

**Step 3 — Total Letter Dimensions:**

$$\text{height} = 5 \times \text{gap}_{mm}, \quad \text{stroke} = 1 \times \text{gap}_{mm}$$

**Step 4 — Physical Size to Pixels:**

$$\text{pixels} = \text{size}_{mm} \times \frac{PPI}{25.4}$$

Where PPI = 300 and 25.4 mm = 1 inch.

---

## 2. Calculated Pixel Sizes

For $d = 100$ mm and $PPI = 300$:

| Acuity | Gap Angle (arcmin) | Gap (mm)  | Gap (px) | Total Height (px) |
|--------|---------------------|-----------|----------|--------------------|
| 6/6    | 1.0                 | 0.02909   | 0.344    | 1.72               |
| 6/12   | 2.0                 | 0.05818   | 0.688    | 3.44               |
| 6/18   | 3.0                 | 0.08727   | 1.030    | 5.15               |
| 6/60   | 10.0                | 0.29089   | 3.438    | 17.18              |

---

## 3. Assumptions & Display Constraint Handling

- **Viewing Distance**: 100 mm (optical path, near-eye micro-display).
- **Display PPI**: 300 (high-density small display).
- **Resolution**: 800 × 600 px; stimulus always centered.
- **tan(θ) vs θ**: Full `tan(θ)` used for greater accuracy.
- **Sub-pixel rendering**: Anti-aliasing (`cv2.LINE_AA`) is applied to better
  represent sub-pixel dimensions at 6/6 and 6/12.
- **Minimum size constraint**: Per requirements, if the computed height is
  less than **2 pixels**, the system clamps to a minimum visible size and
  prints a console warning. At 100 mm / 300 PPI:
  - 6/6 (1.72 px) → clamped, warning printed ✓
  - 6/12 (3.44 px) → clamped, warning printed ✓
  - 6/18 (5.15 px) → rendered at natural size ✓
  - 6/60 (17.18 px) → rendered at natural size ✓
- **Maximum size constraint**: If the stimulus height exceeds the display
  resolution, it is scaled down proportionally.
