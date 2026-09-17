import numpy as np
from scipy.stats import chi2

CHI2_CRIT = chi2.ppf(0.99, df=2)


def coord_anomaly(history: np.ndarray, lat: float, lon: float):
    mu = history.mean(axis=0)
    cov = np.cov(history, rowvar=False) + np.eye(2) * 1e-9
    diff = np.array([lat, lon]) - mu
    d2 = float(diff @ np.linalg.inv(cov) @ diff)
    return d2 > CHI2_CRIT, d2


def sensor_anomaly(history: np.ndarray, val: float):
    mu, std = history.mean(), history.std() + 1e-9
    z = abs(val - mu) / std
    return z > 3.0, z


def composite_score(coord_flag: bool, sensor_flag: bool,
                    w_c: float = 0.7, w_s: float = 0.3) -> float:
    return w_c * float(coord_flag) + w_s * float(sensor_flag)


def consensus_tally(votes: dict, coords: dict,
                    cand_id: int, tau: float = 2 / 3) -> bool:
    cand_lat, cand_lon = coords[cand_id]
    weighted_sum = 0.0
    weight_total = 0.0
    for voter_id, (vote, v_lat, v_lon) in votes.items():
        dist = np.hypot(v_lat - cand_lat, v_lon - cand_lon) + 1e-9
        weight = 1.0 / dist
        weighted_sum += weight * vote
        weight_total += weight
    approval_fraction = weighted_sum / weight_total
    return approval_fraction >= tau


def _demo():
    rng = np.random.default_rng(0)
    coord_hist = np.column_stack([
        rng.normal(41.0082, 0.0005, 60),
        rng.normal(28.9784, 0.0005, 60),
    ])
    sensor_hist = rng.normal(17.0, 0.4, 60)

    ok_flag, d2 = coord_anomaly(coord_hist, 41.0083, 28.9785)
    print(f"legit coord   -> anomaly={ok_flag}  D2={d2:.2f}  crit={CHI2_CRIT:.2f}")
    bad_flag, d2 = coord_anomaly(coord_hist, 41.2000, 29.1000)
    print(f"spoofed coord -> anomaly={bad_flag}  D2={d2:.2f}")

    s_flag, z = sensor_anomaly(sensor_hist, 17.2)
    print(f"legit reading -> anomaly={s_flag}  z={z:.2f}")
    s_flag, z = sensor_anomaly(sensor_hist, 25.0)
    print(f"injected read -> anomaly={s_flag}  z={z:.2f}")

    print(f"composite A_i -> {composite_score(bad_flag, True):.2f}")

    coords = {1: (41.00, 28.97), 2: (41.01, 28.98), 3: (41.02, 28.99),
              4: (41.03, 29.00)}
    votes = {2: (0, 41.01, 28.98), 3: (0, 41.02, 28.99), 4: (0, 41.03, 29.00)}
    print("consensus (all reject) -> accepted =", consensus_tally(votes, coords, 1))


if __name__ == "__main__":
    _demo()
