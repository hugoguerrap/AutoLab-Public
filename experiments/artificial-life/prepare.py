"""
Artificial Life (Lenia) — Simulation & Evaluation
===================================================
FROZEN FILE — Claude must NOT modify this.

Simulates a continuous cellular automaton (Lenia) and measures
emergent behavior: survival, complexity, movement, stability.

Usage:
    python prepare.py evaluate          # Evaluate current rules in rules.py
    python prepare.py render <name>     # Render a GIF of the simulation
    python prepare.py baseline          # Show baseline rules for comparison
"""

import sys
import json
import math
import numpy as np
from datetime import datetime

# ============================================================
# LENIA SIMULATION ENGINE — FROZEN
# ============================================================

GRID_SIZE = 128
STEPS = 500
DT = 0.1  # Time step


def make_kernel(radius, beta_peaks, kernel_type="gaussian"):
    """Create a convolution kernel for Lenia."""
    size = 2 * radius + 1
    kernel = np.zeros((size, size))
    cx, cy = radius, radius

    for x in range(size):
        for y in range(size):
            dx = (x - cx) / radius
            dy = (y - cy) / radius
            r = math.sqrt(dx * dx + dy * dy)

            if r > 1.0:
                continue

            # Shell-based kernel with beta peaks
            if kernel_type == "gaussian":
                for i, (peak, width) in enumerate(beta_peaks):
                    kernel[x, y] += math.exp(-((r - peak) ** 2) / (2 * width * width))
            elif kernel_type == "ring":
                for peak, width in beta_peaks:
                    if abs(r - peak) < width:
                        kernel[x, y] += 1.0 - abs(r - peak) / width

    # Normalize
    total = kernel.sum()
    if total > 0:
        kernel /= total

    return kernel


def growth_function(u, mu, sigma):
    """Lenia growth function — determines how cells grow/shrink."""
    return 2.0 * np.exp(-((u - mu) ** 2) / (2 * sigma * sigma)) - 1.0


def simulate(params, steps=STEPS, grid_size=GRID_SIZE, return_frames=False):
    """
    Run a Lenia simulation with the given parameters.

    Args:
        params: dict with keys: mu, sigma, radius, beta_peaks, kernel_type, init_type
        steps: number of simulation steps
        grid_size: size of the grid (NxN)
        return_frames: if True, return list of grid states for rendering

    Returns:
        dict with simulation metrics
    """
    # Extract parameters
    mu = params.get("mu", 0.15)
    sigma = params.get("sigma", 0.015)
    radius = min(params.get("radius", 13), 20)  # Cap at 20 for performance
    beta_peaks = params.get("beta_peaks", [(0.5, 0.15)])
    kernel_type = params.get("kernel_type", "gaussian")
    init_type = params.get("init_type", "circle")
    dt = params.get("dt", DT)

    # Create kernel
    kernel = make_kernel(radius, beta_peaks, kernel_type)

    # Initialize grid
    grid = np.zeros((grid_size, grid_size))
    cx, cy = grid_size // 2, grid_size // 2

    if init_type == "circle":
        r_init = grid_size // 8
        for x in range(grid_size):
            for y in range(grid_size):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy < r_init * r_init:
                    grid[x, y] = np.random.random() * 0.8 + 0.2
    elif init_type == "ring":
        r_outer = grid_size // 6
        r_inner = grid_size // 10
        for x in range(grid_size):
            for y in range(grid_size):
                dx = x - cx
                dy = y - cy
                dist_sq = dx * dx + dy * dy
                if r_inner * r_inner < dist_sq < r_outer * r_outer:
                    grid[x, y] = np.random.random() * 0.8 + 0.2
    elif init_type == "random_blob":
        r_init = grid_size // 6
        for x in range(grid_size):
            for y in range(grid_size):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy < r_init * r_init:
                    grid[x, y] = np.random.random()
    elif init_type == "multi_blob":
        for ox, oy in [(-20, -20), (20, 20), (-20, 20), (20, -20)]:
            r_init = grid_size // 12
            for x in range(grid_size):
                for y in range(grid_size):
                    dx = x - (cx + ox)
                    dy = y - (cy + oy)
                    if dx * dx + dy * dy < r_init * r_init:
                        grid[x, y] = np.random.random() * 0.8 + 0.2

    # Use fixed seed for reproducibility
    np.random.seed(42)

    frames = []
    activity_history = []
    center_of_mass_history = []

    # Pad kernel to grid size for FFT convolution
    padded_kernel = np.zeros((grid_size, grid_size))
    kh, kw = kernel.shape
    padded_kernel[:kh, :kw] = kernel
    # Center the kernel
    padded_kernel = np.roll(padded_kernel, -kh // 2, axis=0)
    padded_kernel = np.roll(padded_kernel, -kw // 2, axis=1)
    kernel_fft = np.fft.fft2(padded_kernel)

    for step in range(steps):
        # FFT convolution (fast!)
        grid_fft = np.fft.fft2(grid)
        potential = np.real(np.fft.ifft2(grid_fft * kernel_fft))

        # Apply growth function
        growth = growth_function(potential, mu, sigma)

        # Update grid
        grid = np.clip(grid + dt * growth, 0, 1)

        # Record metrics
        activity = float(np.sum(grid > 0.1))
        activity_history.append(activity)

        # Center of mass
        if activity > 0:
            xs, ys = np.where(grid > 0.1)
            if len(xs) > 0:
                com_x = float(np.mean(xs))
                com_y = float(np.mean(ys))
                center_of_mass_history.append((com_x, com_y))

        if return_frames and step % 5 == 0:  # Save every 5th frame
            frames.append(grid.copy())

    # ============================================================
    # COMPUTE METRICS
    # ============================================================

    metrics = {}

    # 1. Survival: did the pattern survive for the full simulation?
    final_activity = activity_history[-1] if activity_history else 0
    initial_activity = activity_history[0] if activity_history else 0

    if final_activity < 10:
        metrics["survived"] = False
        metrics["survival_score"] = 0.0
    elif final_activity > grid_size * grid_size * 0.8:
        # Exploded — filled the grid
        metrics["survived"] = False
        metrics["survival_score"] = 0.1  # Slightly better than dying
    else:
        metrics["survived"] = True
        # Score based on how well it maintained activity
        ratio = final_activity / max(initial_activity, 1)
        metrics["survival_score"] = min(ratio, 1.0)

    # 2. Complexity: Shannon entropy of the final grid
    hist, _ = np.histogram(grid.flatten(), bins=50, range=(0, 1))
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    entropy = -np.sum(hist * np.log2(hist))
    max_entropy = np.log2(50)
    metrics["entropy"] = round(float(entropy), 4)
    metrics["complexity_score"] = round(float(entropy / max_entropy), 4)

    # 3. Movement: did the center of mass move?
    if len(center_of_mass_history) >= 2:
        start = center_of_mass_history[0]
        end = center_of_mass_history[-1]
        displacement = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        metrics["displacement"] = round(displacement, 2)
        # Normalize: max possible displacement is grid diagonal
        max_disp = math.sqrt(2) * grid_size
        metrics["movement_score"] = round(min(displacement / (max_disp * 0.3), 1.0), 4)
    else:
        metrics["displacement"] = 0
        metrics["movement_score"] = 0

    # 4. Stability: variance of activity over last 100 steps
    if len(activity_history) > 100:
        recent = activity_history[-100:]
        mean_activity = np.mean(recent)
        if mean_activity > 0:
            cv = np.std(recent) / mean_activity  # Coefficient of variation
            metrics["activity_cv"] = round(float(cv), 4)
            # Lower CV = more stable. Score decreases with higher CV
            metrics["stability_score"] = round(max(0, 1.0 - cv * 2), 4)
        else:
            metrics["activity_cv"] = 0
            metrics["stability_score"] = 0
    else:
        metrics["activity_cv"] = 0
        metrics["stability_score"] = 0

    # 5. Structure: are there distinct connected components?
    binary = (grid > 0.2).astype(int)
    # Simple connected component estimate using unique mass regions
    labeled = np.zeros_like(binary)
    current_label = 0
    for x in range(grid_size):
        for y in range(grid_size):
            if binary[x, y] == 1 and labeled[x, y] == 0:
                current_label += 1
                # BFS
                queue = [(x, y)]
                while queue:
                    cx_, cy_ = queue.pop(0)
                    if 0 <= cx_ < grid_size and 0 <= cy_ < grid_size:
                        if binary[cx_, cy_] == 1 and labeled[cx_, cy_] == 0:
                            labeled[cx_, cy_] = current_label
                            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                queue.append((cx_ + dx, cy_ + dy))

    num_components = current_label
    # Filter tiny components (noise)
    component_sizes = []
    for i in range(1, current_label + 1):
        size = np.sum(labeled == i)
        if size > 20:  # Minimum size threshold
            component_sizes.append(size)

    metrics["num_structures"] = len(component_sizes)
    metrics["structure_score"] = round(min(len(component_sizes) / 5.0, 1.0), 4)

    # 6. Oscillation: is the activity periodic?
    if len(activity_history) > 200:
        recent = np.array(activity_history[-200:])
        recent_centered = recent - np.mean(recent)
        # Autocorrelation
        autocorr = np.correlate(recent_centered, recent_centered, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        if autocorr[0] > 0:
            autocorr = autocorr / autocorr[0]
            # Find first peak after lag 0
            peaks = []
            for i in range(2, len(autocorr) - 1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.3:
                    peaks.append((i, autocorr[i]))
                    break
            if peaks:
                metrics["oscillation_period"] = peaks[0][0]
                metrics["oscillation_score"] = round(float(peaks[0][1]), 4)
            else:
                metrics["oscillation_period"] = 0
                metrics["oscillation_score"] = 0
        else:
            metrics["oscillation_period"] = 0
            metrics["oscillation_score"] = 0
    else:
        metrics["oscillation_period"] = 0
        metrics["oscillation_score"] = 0

    # COMPOSITE SCORE
    # Weights: survival (25%) + complexity (20%) + movement (20%) + stability (15%) + structure (10%) + oscillation (10%)
    composite = (
        0.25 * metrics.get("survival_score", 0) +
        0.20 * metrics.get("complexity_score", 0) +
        0.20 * metrics.get("movement_score", 0) +
        0.15 * metrics.get("stability_score", 0) +
        0.10 * metrics.get("structure_score", 0) +
        0.10 * metrics.get("oscillation_score", 0)
    )
    metrics["composite_score"] = round(composite, 4)

    # Activity stats
    metrics["final_activity"] = round(final_activity, 0)
    metrics["peak_activity"] = round(float(max(activity_history)), 0)

    if return_frames:
        return metrics, frames
    return metrics


def render_gif(params, filename, steps=STEPS, grid_size=GRID_SIZE):
    """Render a simulation as a GIF."""
    try:
        from PIL import Image
    except ImportError:
        print("PIL not available. Install with: pip install Pillow")
        return

    metrics, frames = simulate(params, steps, grid_size, return_frames=True)

    if not frames:
        print("No frames to render")
        return

    # Create color map (black → blue → cyan → green → yellow → white)
    def value_to_color(v):
        if v < 0.1:
            return (0, 0, 0)
        elif v < 0.3:
            t = (v - 0.1) / 0.2
            return (0, int(50 * t), int(150 * t))
        elif v < 0.5:
            t = (v - 0.3) / 0.2
            return (0, int(50 + 150 * t), int(150 + 50 * t))
        elif v < 0.7:
            t = (v - 0.5) / 0.2
            return (int(100 * t), int(200 + 55 * t), int(100 - 100 * t))
        elif v < 0.9:
            t = (v - 0.7) / 0.2
            return (int(100 + 155 * t), int(255), int(50 * t))
        else:
            t = (v - 0.9) / 0.1
            return (255, 255, int(50 + 205 * t))

    images = []
    scale = 4  # Scale up for visibility

    for frame in frames:
        img = Image.new("RGB", (grid_size * scale, grid_size * scale))
        pixels = img.load()
        for x in range(grid_size):
            for y in range(grid_size):
                color = value_to_color(frame[x, y])
                for sx in range(scale):
                    for sy in range(scale):
                        pixels[y * scale + sy, x * scale + sx] = color
        images.append(img)

    # Save as GIF
    images[0].save(
        filename,
        save_all=True,
        append_images=images[1:],
        duration=100,  # ms per frame
        loop=0
    )
    print(f"Saved GIF: {filename} ({len(images)} frames, {grid_size}x{grid_size})")
    return metrics


def show_baselines():
    """Show known Lenia configurations as baseline."""
    from rules import RULES_LIBRARY

    print("=" * 80)
    print("BASELINE RULES")
    print("=" * 80)

    for name, params in RULES_LIBRARY.items():
        print(f"\n--- {name} ---")
        metrics = simulate(params, steps=300)  # Shorter for baseline
        for k, v in sorted(metrics.items()):
            print(f"  {k}: {v}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py [evaluate|render <name>|baseline]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "baseline":
        show_baselines()

    elif command == "evaluate":
        sys.path.insert(0, ".")
        from rules import CURRENT_RULES, RULES_LIBRARY

        print("=" * 80)
        print("EVALUATING CURRENT RULES")
        print("=" * 80)

        # Evaluate current rules
        for name, params in CURRENT_RULES.items():
            print(f"\n--- {name} ---")
            metrics = simulate(params)
            for k, v in sorted(metrics.items()):
                print(f"  {k}: {v}")

    elif command == "render":
        if len(sys.argv) < 3:
            print("Usage: python prepare.py render <rule_name>")
            sys.exit(1)

        rule_name = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else f"renders/{rule_name}.gif"

        sys.path.insert(0, ".")
        from rules import CURRENT_RULES, RULES_LIBRARY

        # Look in current rules first, then library
        params = CURRENT_RULES.get(rule_name) or RULES_LIBRARY.get(rule_name)
        if not params:
            print(f"Rule '{rule_name}' not found")
            sys.exit(1)

        metrics = render_gif(params, output)
        if metrics:
            print("\nMetrics:")
            for k, v in sorted(metrics.items()):
                print(f"  {k}: {v}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
