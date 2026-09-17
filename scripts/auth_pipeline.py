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

SENSORS = [
    ("Seismic Node",  "MEMS 3-axis accel. \u00b7 LoRaWAN"),
    ("GPS Node",      "WGS-84 position fix \u00b7 NB-IoT"),
    ("Hydro Sensor",  "River / flood stage \u00b7 LoRaWAN"),
    ("AgriSen Node",  "Soil moisture + temp. \u00b7 ZigBee"),
    ("Air Sensor",    "PM2.5 air quality \u00b7 Wi-Fi 6"),
    ("SubSen Node",   "Structural tilt \u00b7 NB-IoT"),
    ("TMP Sensor",    "Ambient temperature \u00b7 LoRaWAN"),
]
STAGE1 = ("Stage 1 \u2014 Packet Signing (Sensor Node)", [
    r"Build $P_i=(\varphi_i,\lambda_i,\rho_i,t_i,v_i)$",
    r"$h_i=\mathrm{SHA\text{-}256}(P_i)$",
    r"$\sigma_i=\mathrm{ECDSA.Sign}(sk_i,h_i)$",
    r"Frame $F_i=P_i\,\|\,\sigma_i\,\|\,\mathrm{ID}_i$  ($\leq$222 B)",
])
STAGE2 = ("Stage 2 \u2014 Verification (Edge Gateway)", [
    r"Verify $\sigma_i$ with $pk_i$ (Merkle store)",
    r"Freshness $|t_{\mathrm{now}}-t_i|\leq\Delta_t=30$ s",
    r"Sequence $v_i>\mathrm{last\_seq}[n_i]$",
    "Reject on UNKNOWN / INVALID / STALE / REPLAY",
])
STAGE3 = ("Stage 3 \u2014 Aggregation & Dispatch", [
    r"Peer-consensus tally ($\tau=2/3$, geo-weighted)",
    r"Anomaly $A_i=0.7\,c_{\mathrm{coord}}+0.3\,c_{\mathrm{sensor}}$",
    r"Forward to Cloud GIS if $A_i\leq 0.5$",
])
VALID = ("Validated Spatial Data", [
    "Signed WGS-84 packets",
    "64-byte ECDSA signatures",
    "PostGIS spatial store",
])
CLOUD = ("Cloud GIS Ingest", [
    "OGC WFS / WMS / WCS",
    "SensorThings API",
])

C_SENS  = dict(fill="#D3E9E4", edge="#2E8B8B")
C_CONT  = dict(fill="#EAF2FB", edge="#2E6DA4")
C_STAGE = dict(fill="#F7DDD9", edge="#C0504D")
C_VALID = dict(fill="#F5E6C8", edge="#B8860B")
C_CLOUD = dict(fill="#D5EAD5", edge="#3E8E4E")

W_IN, H_IN = 14.4, 6.6

def lh(fs):
    return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN)
ax.axis("off")

def draw_box(cx, cy, w, h, header, body, fill, edge,
             hfs=10.0, bfs=8.3, gap_hd=0.11, header_left=False):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.09",
        linewidth=1.5, edgecolor=edge, facecolor=fill,
        mutation_aspect=1.0, zorder=3))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body) * LB if body else 0)
    top = cy + block_h / 2
    if header_left:
        ax.text(cx - w / 2 + 0.14, top - HH / 2, header, ha="left", va="center",
                fontsize=hfs, fontweight="bold", color=edge, zorder=4)
        xb = cx - w / 2 + 0.14; ha = "left"
    else:
        ax.text(cx, top - HH / 2, header, ha="center", va="center",
                fontsize=hfs, fontweight="bold", color=edge, zorder=4)
        xb = cx; ha = "center"
    y = top - HH - gap_hd
    for line in body:
        ax.text(xb, y - LB / 2, line, ha=ha, va="center",
                fontsize=bfs, color="#1a1a1a", zorder=4)
        y -= LB

def arrow(x0, y0, x1, y1, color="#333333", lw=1.6, ms=15):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color,
        shrinkA=0, shrinkB=0, zorder=2))

cont_x0, cont_x1 = 5.15, 9.95
cont_y0, cont_y1 = 0.75, 5.62
cont_cy = (cont_y0 + cont_y1) / 2
ax.add_patch(FancyBboxPatch(
    (cont_x0, cont_y0), cont_x1 - cont_x0, cont_y1 - cont_y0,
    boxstyle="round,pad=0.02,rounding_size=0.10",
    linewidth=1.6, edgecolor=C_CONT["edge"], facecolor=C_CONT["fill"],
    mutation_aspect=1.0, zorder=1))
ax.text((cont_x0 + cont_x1) / 2, 5.34, "ECDSA P-256 Authentication Pipeline",
        ha="center", va="center", fontsize=11.5, fontweight="bold",
        color=C_CONT["edge"], zorder=4)

st_cx = (cont_x0 + cont_x1) / 2
st_w = 4.35
st_h = 1.16
st_centers = [4.47, 3.09, 1.71]
for (hdr, body), cy in zip([STAGE1, STAGE2, STAGE3], st_centers):
    draw_box(st_cx, cy, st_w, st_h, hdr, body,
             C_STAGE["fill"], C_STAGE["edge"], hfs=9.6, bfs=8.2, header_left=True)

L_cx, L_w = 1.62, 2.74
L_h = 0.52
L_centers = [5.36 - i * 0.74 for i in range(len(SENSORS))]
ax.text(L_cx, 5.98, "Heterogeneous IoT sensor nodes", ha="center", va="center",
        fontsize=8.8, style="italic", color="#555555", zorder=4)
for (name, sub), cy in zip(SENSORS, L_centers):
    draw_box(L_cx, cy, L_w, L_h, name, [sub],
             C_SENS["fill"], C_SENS["edge"], hfs=9.3, bfs=7.7, gap_hd=0.05)

R_cx, R_w = 12.55, 2.78
draw_box(R_cx, 4.05, R_w, 1.30, VALID[0], VALID[1],
         C_VALID["fill"], C_VALID["edge"], hfs=10.0, bfs=8.5)
draw_box(R_cx, 2.05, R_w, 1.15, CLOUD[0], CLOUD[1],
         C_CLOUD["fill"], C_CLOUD["edge"], hfs=10.0, bfs=8.5)

for cy in L_centers:
    arrow(L_cx + L_w / 2 + 0.02, cy, cont_x0 - 0.02, cont_cy,
          color="#9AA0A6", lw=1.0, ms=11)

arrow(cont_x1 + 0.02, 4.05, R_cx - R_w / 2 - 0.02, 4.05)

arrow(R_cx, 4.05 - 1.30 / 2 - 0.02, R_cx, 2.05 + 1.15 / 2 + 0.02)

ax.text(W_IN / 2, H_IN - 0.28,
        "ECDSA P-256 Authentication Pipeline for IoT Spatial Data Packets",
        ha="center", va="center", fontsize=13.5, fontweight="bold", color="#1a1a1a")
ax.text(W_IN / 2, 0.28,
        "Heterogeneous IoT sensor nodes emit spatially referenced packets that "
        "are signed, verified, consensus-checked, and dispatched to the cloud GIS.",
        ha="center", va="center", fontsize=8.6, color="#444444")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_auth_pipeline.pdf"))
fig.savefig(os.path.join(outdir, "fig_auth_pipeline.png"), dpi=600)
plt.close(fig)
print("wrote fig_auth_pipeline.{png,pdf} to", os.path.abspath(outdir))

