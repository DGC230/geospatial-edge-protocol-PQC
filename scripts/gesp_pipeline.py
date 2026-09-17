import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.fontset": "stixsans",
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})

STAGES = [
    dict(header="IoT Sensor Node",
         body=[r"WGS-84 GPS fix $(\varphi,\lambda)$",
               r"Sensor payload $\rho$",
               "nRF9160 SiP \u2013 Cortex-M33"],
         fill="#FBE7B8", edge="#B8860B"),
    dict(header="Packet Assembly",
         body=[r"$P=(\varphi,\lambda,\rho,t,v)$",
               r"Unix timestamp $t$",
               r"Sequence number $v$"],
         fill="#CFE2F3", edge="#2E6DA4"),
    dict(header="ECDSA P-256 Signing",
         body=[r"$h=\mathrm{SHA\text{-}256}(P)$",
               r"$\sigma=\mathrm{Sign}(sk,h)$",
               "64-byte sig \u00b7 LoRaWAN"],
         fill="#E4D7F0", edge="#7A4FA3"),
    dict(header="GESP Edge Gateway",
         body=[r"Verify $\sigma$ (pk store)",
               r"Freshness $|t-t_{\mathrm{now}}|\leq 30$ s",
               r"Seq $v>\mathrm{last\_seq}[n]$"],
         fill="#FBE0C6", edge="#D9822B"),
    dict(header="Anomaly + Consensus",
         body=[r"Mahalanobis $D^2>\chi^2_{2,0.99}$",
               r"Z-score $|z|>3\sigma$",
               r"Peer votes $\geq\tau=2/3$"],
         fill="#D9D2EC", edge="#5A4AA0"),
    dict(header="Cloud GIS Store",
         body=["Validated WGS-84",
               "OGC WFS / WMS / WCS",
               "SensorThings API"],
         fill="#D5EAD5", edge="#3E8E4E"),
]
QUAR = dict(header="Quarantine / Drop",
            body=[r"Invalid $\sigma$, stale, or replay",
                  r"$A_i>0.5$ or votes $<\tau$"],
            fill="#F6D6D2", edge="#C0392B")

W_IN, H_IN = 14.4, 5.5
ML = MR = 0.34
GAP = 0.30
ARROW_LEN = 1.10
N = len(STAGES)

gaps = [GAP] * (N - 2) + [ARROW_LEN]
box_w = (W_IN - ML - MR - sum(gaps)) / N
box_h = 1.34
row_cy = 3.55

centers = []
x = ML + box_w / 2
for i in range(N):
    centers.append(x)
    if i < N - 1:
        x += box_w + gaps[i]

FS_HEAD, FS_BODY = 11.5, 9.2
LH = FS_BODY * 1.16 / 72.0
HH = FS_HEAD * 1.16 / 72.0
GAP_HD = 0.12

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN)
ax.axis("off")

def draw_box(cx, cy, w, h, spec, hfs=FS_HEAD, bfs=FS_BODY):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=1.5, edgecolor=spec["edge"], facecolor=spec["fill"],
        mutation_aspect=1.0, zorder=2))
    block_h = HH + GAP_HD + len(spec["body"]) * LH
    top = cy + block_h / 2
    ax.text(cx, top - HH / 2, spec["header"], ha="center", va="center",
            fontsize=hfs, fontweight="bold", color=spec["edge"], zorder=3)
    y = top - HH - GAP_HD
    for line in spec["body"]:
        ax.text(cx, y - LH / 2, line, ha="center", va="center",
                fontsize=bfs, color="#1a1a1a", zorder=3)
        y -= LH

for cx, spec in zip(centers, STAGES):
    draw_box(cx, row_cy, box_w, box_h, spec)

quar_h = 0.92
quar_cx = centers[4]
quar_cy = row_cy - box_h / 2 - ARROW_LEN - quar_h / 2
draw_box(quar_cx, quar_cy, box_w, quar_h, QUAR, hfs=10.5, bfs=8.8)

def arrow(x0, y0, x1, y1, color="#333333", lw=1.6):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=15,
        linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=1))

OFF = 0.015
for i in range(N - 1):
    arrow(centers[i] + box_w / 2 + OFF, row_cy,
          centers[i + 1] - box_w / 2 - OFF, row_cy)

mid_x = (centers[4] + box_w / 2 + centers[5] - box_w / 2) / 2
ax.text(mid_x, row_cy + 0.17, "accept", ha="center", va="bottom",
        fontsize=8.4, style="italic", color="#3E8E4E", zorder=3)

y_bot_5 = row_cy - box_h / 2
y_top_q = quar_cy + quar_h / 2
arrow(quar_cx, y_bot_5 - OFF, quar_cx, y_top_q + OFF, color="#C0392B", lw=1.6)
ax.text(quar_cx + 0.12, (y_bot_5 + y_top_q) / 2, "reject",
        ha="left", va="center", fontsize=8.4, style="italic",
        color="#C0392B", zorder=3)

ax.text(W_IN / 2, H_IN - 0.30,
        "GESP End-to-End Processing Pipeline: IoT Sensor Node to Cloud GIS",
        ha="center", va="center", fontsize=13.5, fontweight="bold",
        color="#1a1a1a")
ax.text(W_IN / 2, 0.30,
        "Forward-only validation path: packets clearing signature, freshness, "
        "sequence, anomaly and consensus gates are forwarded to the cloud GIS; "
        "all others are quarantined.",
        ha="center", va="center", fontsize=8.6, color="#444444")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_gesp_pipeline.pdf"))
fig.savefig(os.path.join(outdir, "fig_gesp_pipeline.png"), dpi=600)
plt.close(fig)
print("wrote fig_gesp_pipeline.{png,pdf} to", os.path.abspath(outdir))

