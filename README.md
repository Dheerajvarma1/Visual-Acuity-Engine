# Visual Acuity Stimulus Engine: Landolt C Framework

## Executive Summary
The **Visual Acuity Stimulus Engine (VASE)** is a high-precision rendering framework developed for head-mounted visual testing systems. Designed for near-eye micro-displays (optical distance ~100mm), VASE translates standard clinical visual acuity requirements into mathematically accurate digital stimuli using visual-angle geometry.

> [!IMPORTANT]
> This system is designed for a medical device context where stimulus accuracy and consistent calibration are paramount.

---

## 1. Domain Context & Problem Definition
Traditional visual acuity tests (like the Snellen chart) are often static and non-adaptive. In the context of Head-Mounted Displays (HMDs), clinical testing requires:
- **Dynamic Scaling**: Stimuli must adapt to specific hardware parameters (PPI, viewing distance).
- **Sub-pixel Accuracy**: At high acuity levels (6/6), stimuli gaps can be smaller than a single physical pixel.
- **Controlled Interaction**: Logging of user response against "Ground Truth" for adaptive testing logic.

VASE addresses these by decoupled stimulus math from the rendering layer, ensuring that physics-based requirements drive the visual output.

---

## 2. System Objectives & Scope
The primary objective is to render a mathematically correct **Landolt C** optotype that subtends precise angles at the fovea.

### In Scope
- Calculation of visual angle $\theta$ based on Snellen-equivalent acuity levels (6/6 to 6/60).
- Real-time rendering with anti-aliasing to mitigate pixelation artifacts.
- Automated CSV logging for clinical data collection.
- Safety-first clamping for stimuli that fall below hardware resolution thresholds.

---

## 3. Technical Architecture

### 3.1 Design Principles
1. **Physical Accuracy**: No hardcoded pixel values. All dimensions are derived from distance and PPI.
2. **Modular Decoupling**: Separation of the `VisualAcuityEngine` (math/logic) from the `AppManager` (interaction/IO).
3. **Safety Through Admonition**: Console-level warnings when stimulus integrity is compromised by hardware limits.

### 3.2 The Visual Angle Pipeline
The engine follows a three-stage transformation pipeline:

1.  **Acuity to Radians**: $\theta_{rad} = \text{arcmin} \times \frac{\pi}{180 \times 60}$
2.  **Visual Angle to Physical Size (mm)**: $\text{gap}_{mm} = d \times \tan(\theta_{rad})$
3.  **Physical Size to Raster Pixels**: $\text{pixels} = \text{gap}_{mm} \times \frac{PPI}{25.4}$

> [!NOTE]
> While a small-angle approximation ($\tan(\theta) \approx \theta$) is common in clinical software, VASE utilizes the full tangent function to ensure maximum accuracy across a broader range of visual distances.

### 3.3 Hardware Assumptions
| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Viewing Distance** | 100 mm | Optical path from eye to display. |
| **Display PPI** | 300 | Pixels Per Inch (Density). |
| **Output Resolution** | 800 × 600 px | Restricted small-display simulation. |

---

## 4. Implementation Details

### Optotype Geometry
The Landolt C is rendered following the **1:5 ratio** standard:
- **Stroke Width ($s$)** = Gap Size ($g$)
- **Total Height ($D$)** = $5 \times g$

### Rendering Strategy
VASE utilizes OpenCV's `LINE_AA` (Anti-Aliasing) for all polygon and circle fills. This is critical for 6/6 and 6/12 levels where the calculated gap size is $< 1.0$ px, as it allows for sub-pixel intensity variation that better simulates the intended visual angle on high-density displays.

---

## 5. Operational Guide

### Prerequisites
- Python 3.8+
- Dependencies: `opencv-python`, `numpy`

### Launching the System
```bash
python main.py
```

### Interactive Controls
| Key | Action | Clinical Purpose |
| :--- | :--- | :--- |
| **1 - 4** | Switch Acuity Level | Incremental testing (6/6, 6/12, 6/18, 6/60). |
| **W, A, S, D** | Submit Response | Input perceived gap (Up, Left, Down, Right). |
| **ESC** | Terminate Session | Safe exit and log finalization. |

---

## 6. Safety & Limitations

> [!WARNING]
> **Hardware Resolution Floor**: At 300 PPI and 100mm distance, the 6/6 acuity level gap is calculated at **0.34 pixels**. On standard digital displays, this is physically impossible to render with absolute fidelity.

### Safety Handling
- **Minimum Stimulus Size**: VASE enforces a **5.0 px height** minimum. If a stimulus falls below this, it is scaled up to 5px (the smallest size providing a 1px gap/stroke) and a warning is triggered.
- **Proportional Scaling**: If a stimulus exceeds 800px (e.g., at extremely long distances), it is scaled down to fit the foveal region of the display.

---

## 7. Future Roadmap
- **Contrast Control**: Variable luminance for contrast sensitivity testing.
- **Adaptive staircase algorithms**: Implementation of the *QUEST* or *PEST* protocol for faster threshold detection.
- **Eye-chart mode**: Multiple optotype presentation for crowding effect analysis.
