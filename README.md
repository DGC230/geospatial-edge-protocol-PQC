# GESP — Geospatial Edge Stability Protocol

A lightweight edge-authentication protocol that protects the integrity of
GPS-tagged spatial data packets flowing from Class-1 IoT sensor nodes to a
cloud GIS backend. GESP combines three components that run entirely on the
edge gateway and require no changes to existing cloud GIS stacks:

1. **ECDSA P-256 packet signing** binding WGS-84 coordinates, sensor payload,
   timestamp and sequence number into a 64-byte signature.
2. **Geo-weighted peer consensus** cross-validating coordinate and payload
   claims among spatially proximate nodes.
3. **A dual-component spatial anomaly filter** (Mahalanobis coordinate test +
   Z-score payload test) combined into a composite score.

The protocol is evaluated with a SimPy discrete-event Monte Carlo simulation of
up to 500 nodes under coordinate-spoofing, data-injection and packet-replay
attacks.

## Repository layout

```
GESP/
├── src/                            protocol reference implementation
│   ├── script1_gesp_signing.py     packet serialisation, ECDSA signing, edge verification
│   ├── script2_gesp_anomaly.py     Mahalanobis + Z-score anomaly filter, consensus tally
│   └── script3_gesp_simulation.py  SimPy Monte Carlo harness (detection / FP / latency)
├── scripts/                        one script per figure (matplotlib)
├── requirements.txt
├── LICENSE
└── README.md
```

## Installation

Python 3.10 or newer is recommended.

```
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the protocol code

Each script in `src/` is standalone and includes a small self-test in its
`__main__` block:

```
python src/script1_gesp_signing.py     # signs a packet; shows accept / tamper / replay / stale verdicts
python src/script2_gesp_anomaly.py     # runs the anomaly filter and a consensus tally on sample data
python src/script3_gesp_simulation.py  # sweeps K/N per attack and prints detection, FP and latency
```

`script3_gesp_simulation.py` also exposes `GESPSimulation` and a `sweep(...)`
helper that return `SimResult` records for programmatic use.

## Regenerating the figures

Each script in `scripts/` writes a 600-dpi PNG and a vector PDF
(`fig_<name>.png`, `fig_<name>.pdf`) into the directory given as the first
argument (default: current directory):

```
python scripts/architecture.py out/
python scripts/results.py out/
```

The figure scripts request the *Nimbus Sans* text face and the *STIX Sans*
math set. If those fonts are not installed, matplotlib substitutes its
defaults; the layout is unchanged but glyphs will differ slightly. On Debian
or Ubuntu, `fonts-urw-base35` provides Nimbus Sans.

## Requirements

`cryptography`, `numpy`, `scipy`, `simpy`, `matplotlib` (see
`requirements.txt`).

## License

Released under the MIT License — see `LICENSE`.
