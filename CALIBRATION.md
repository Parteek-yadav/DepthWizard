# DepthWizard — Depth-to-Elevation Calibration Methodology

## 1. Physical Principle

Monocular depth models produce scale-ambiguous, non-metric relative depth $D_{\text{rel}} \in [0, 1]$. In remote sensing, true terrain elevation $Z_{\text{true}}$ (in meters above sea level) follows a linear or piece-wise affine transformation across a local geographic extent:

$$Z_{\text{pred}}(x, y) = s \cdot D_{\text{rel}}(x, y) + t$$

Where:
- $s$ is the physical height scaling factor ($\text{meters / relative unit}$).
- $t$ is the base terrain datum offset ($\text{meters}$).

---

## 2. Robust Huber M-Estimation

Ordinary Least Squares (OLS) is vulnerable to localized artifacts such as cloud cover, shadow occlusions, and water bodies. DepthWizard solves for $(s, t)$ using **Huber Loss Regression**:

$$\min_{s, t} \sum_{i=1}^{N} \rho_\delta \left( Z_{\text{ref}, i} - (s \cdot D_{\text{rel}, i} + t) \right)$$

$$\rho_\delta(r) = \begin{cases} \frac{1}{2} r^2 & \text{if } |r| \le \delta \\ \delta \cdot (|r| - \frac{1}{2}\delta) & \text{if } |r| > \delta \end{cases}$$

We use $\delta = 1.35 \cdot \sigma$, which guarantees 95% statistical efficiency for normal distributions while completely damping large outlier leverage.

---

## 3. Validation & Diagnostic Metrics

To prevent overfitting, DepthWizard reserves a 20% held-out test split of reference points and calculates:

1. **Mean Absolute Error (MAE)**:
   $$\text{MAE} = \frac{1}{N_{\text{val}}} \sum_{i=1}^{N_{\text{val}}} |Z_{\text{pred}, i} - Z_{\text{ref}, i}|$$

2. **Root Mean Square Error (RMSE)**:
   $$\text{RMSE} = \sqrt{\frac{1}{N_{\text{val}}} \sum_{i=1}^{N_{\text{val}}} (Z_{\text{pred}, i} - Z_{\text{ref}, i})^2}$$

3. **Pearson Correlation ($r$)**:
   $$r = \frac{\sum (Z_{\text{pred}} - \bar{Z}_{\text{pred}})(Z_{\text{ref}} - \bar{Z}_{\text{ref}})}{\sqrt{\sum (Z_{\text{pred}} - \bar{Z}_{\text{pred}})^2 \sum (Z_{\text{ref}} - \bar{Z}_{\text{ref}})^2}}$$

4. **Coefficient of Determination ($R^2$)**:
   $$R^2 = 1 - \frac{\sum_{i=1}^{N_{\text{val}}} (Z_{\text{ref}, i} - Z_{\text{pred}, i})^2}{\sum_{i=1}^{N_{\text{val}}} (Z_{\text{ref}, i} - \bar{Z}_{\text{ref}})^2}$$

---

## 4. Ground Control Point (GCP) Mode

When continuous DEM rasters are unavailable, users can input discrete Ground Control Points $[(x_k, y_k, Z_k)]_{k=1}^K$.
- For $K \ge 4$, Huber robust regression is used.
- For $2 \le K < 4$, standard linear regression is fitted.
- Individual residuals $r_k = Z_k - Z_{\text{pred}, k}$ are reported to detect surveying misalignments.
