from pathlib import Path
import numpy as np
import pandas as pd


def generate_flight_data(filename: Path, n_points: int = 600):
    np.random.seed(42)
    time_series = np.linspace(0, 120, n_points)
    
    altitude = 1000 + 50 * np.sin(time_series / 10) + np.random.normal(0, 2, n_points)
    vibration = 0.5 + 0.1 * np.sin(time_series * 2) + np.random.normal(0, 0.05, n_points)
    vibration[175:200] += np.random.uniform(0.8, 1.5, 25)
    battery_v = 24.0 - (time_series * 0.03) + np.random.normal(0, 0.02, n_points)

    df = pd.DataFrame({
        "timestamp_sec": np.round(time_series, 2),
        "altitude_m": np.round(altitude, 2),
        "vibration_g": np.round(vibration, 4),
        "battery_voltage": np.round(battery_v, 2),
    })
    
    filename.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filename, index=False)


if __name__ == "__main__":
    generate_flight_data(Path("data/flight_log.csv"))
