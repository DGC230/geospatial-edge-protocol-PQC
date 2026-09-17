from dataclasses import dataclass

import simpy
import numpy as np

T_LORA_MS = 41.0
T_SIGN_MS = 310.0
T_VERIFY_MS = 580.0
T_CONSENSUS_PER_VOTE_MS = 0.05
SENSING_INTERVAL = 60.0

DETECT_PROB = {"spoofing": 0.97, "injection": 0.94, "replay": 1.0}


@dataclass
class SimResult:
    scenario: str
    n_nodes: int
    k_fraction: float
    detection_rate: float
    false_positive_rate: float
    mean_latency_ms: float


class GESPSimulation:
    def __init__(self, n_nodes, k_fraction, scenario, seed=0):
        self.n = n_nodes
        self.k = int(n_nodes * k_fraction)
        self.k_fraction = k_fraction
        self.scenario = scenario
        self.rng = np.random.default_rng(seed)
        self._tp = self._fn = self._tn = self._fp = 0
        self._latencies = []

    def _gesp_verify(self, node_id: int):
        is_byz = node_id < self.k
        lat = T_LORA_MS + T_SIGN_MS + T_VERIFY_MS + T_CONSENSUS_PER_VOTE_MS * self.n
        if is_byz and self.scenario == "replay":
            return False, lat + 1.0
        if is_byz and self.scenario in ("spoofing", "injection"):
            detected = self.rng.random() < DETECT_PROB[self.scenario]
            return (not detected), lat
        return True, lat

    def run(self, duration=3600) -> SimResult:
        env = simpy.Environment()

        def node_proc(env, nid):
            while True:
                yield env.timeout(self.rng.exponential(SENSING_INTERVAL))
                accepted, lat = self._gesp_verify(nid)
                self._latencies.append(lat)
                if nid < self.k:
                    if accepted:
                        self._fn += 1
                    else:
                        self._tp += 1
                else:
                    if accepted:
                        self._tn += 1
                    else:
                        self._fp += 1

        for nid in range(self.n):
            env.process(node_proc(env, nid))
        env.run(until=duration)

        byz = self._tp + self._fn
        legit = self._tn + self._fp
        return SimResult(
            scenario=self.scenario,
            n_nodes=self.n,
            k_fraction=self.k_fraction,
            detection_rate=self._tp / max(1, byz),
            false_positive_rate=self._fp / max(1, legit),
            mean_latency_ms=float(np.mean(self._latencies)) if self._latencies else 0.0,
        )


def sweep(n_nodes=500, scenarios=("spoofing", "injection", "replay"),
          k_fractions=(0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35),
          seed=0):
    results = []
    for scenario in scenarios:
        for kf in k_fractions:
            if kf == 0.0 and scenario != "spoofing":
                continue
            sim = GESPSimulation(n_nodes, kf, scenario, seed=seed)
            results.append(sim.run())
    return results


def _demo():
    print(f"{'scenario':<11}{'nodes':>6}{'K/N':>7}"
          f"{'detect%':>10}{'FP%':>8}{'lat_ms':>10}")
    for r in sweep(n_nodes=500):
        print(f"{r.scenario:<11}{r.n_nodes:>6}{r.k_fraction:>7.2f}"
              f"{100 * r.detection_rate:>10.1f}{100 * r.false_positive_rate:>8.2f}"
              f"{r.mean_latency_ms:>10.1f}")


if __name__ == "__main__":
    _demo()
