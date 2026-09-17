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

SENSOR = ("Sensor Node", [r"WGS-84 GPS fix $(\varphi,\lambda)$",
                          r"Sensor payload $\rho$",
                          "Class-1 SiP (nRF9160)"],
          dict(fill="#D3E9E4", edge="#2E8B8B"))
CLOUD = ("Cloud GIS Layer", ["WGS-84 validated packets",
                             "PostGIS spatial store",
                             r"WFS · WMS · WCS",
                             "SensorThings API"],
         dict(fill="#D5EAD5", edge="#3E8E4E"))

TIER1 = ("IoT Sensing Layer — Tier 1", dict(cont="#EDE7F6", cedge="#7A4FA3",
                                            bfill="#E4D7F0", bedge="#7A4FA3"), [
    ("LoRaWAN",     r"868 MHz · SF7–SF12"),
    ("Wi-Fi 6",     r"802.11ax · 2.4/5 GHz"),
    ("ZigBee 3.0",  r"2.4 GHz mesh"),
    ("NB-IoT",      r"licensed cellular"),
])
TIER2 = ("Edge Computation Layer — Tier 2", dict(cont="#FBF1DC", cedge="#C8912B",
                                                 bfill="#FBE0C6", bedge="#D9822B"), [
    ("ECDSA Verify",   r"$\sigma$ · freshness $\Delta_t=30$ s"),
    ("Peer Consensus", r"geo-weighted · $\tau=2/3$, $K<n/3$"),
    ("Anomaly Filter", r"Mahalanobis $D^2>\chi^2$ · $|z|>3\sigma$"),
    ("Packet Dispatch", r"validated $\rightarrow$ cloud · OGC"),
])

W_IN, H_IN = 14.5, 5.8
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

def draw_box(cx, cy, w, h, header, body, fill, edge, hfs=9.5, bfs=8.2, gap_hd=0.09):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.07",
        linewidth=1.4, edgecolor=edge, facecolor=fill, mutation_aspect=1.0, zorder=3))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body)*LB if body else 0)
    top = cy + block_h/2
    ax.text(cx, top - HH/2, header, ha="center", va="center",
            fontsize=hfs, fontweight="bold", color=edge, zorder=4)
    y = top - HH - gap_hd
    for line in body:
        ax.text(cx, y - LB/2, line, ha="center", va="center",
                fontsize=bfs, color="#1a1a1a", zorder=4)
        y -= LB

def arrow(x0, y0, x1, y1, color="#333333", lw=1.8, ms=17):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=2))

SENS = (0.30, 2.50)
T1   = (3.20, 6.70)
T2   = (7.40, 10.90)
CLD  = (11.60, 14.20)
CONT_Y0, CONT_Y1 = 0.75, 5.05
MIDY = (CONT_Y0 + CONT_Y1) / 2
HDR_Y = 4.80

draw_box((SENS[0]+SENS[1])/2, MIDY, SENS[1]-SENS[0], 2.4, SENSOR[0], SENSOR[1],
         SENSOR[2]["fill"], SENSOR[2]["edge"], hfs=10.0, bfs=8.4)
draw_box((CLD[0]+CLD[1])/2, MIDY, CLD[1]-CLD[0], 2.8, CLOUD[0], CLOUD[1],
         CLOUD[2]["fill"], CLOUD[2]["edge"], hfs=10.0, bfs=8.4)

def draw_tier(x0, x1, spec):
    title, th, boxes = spec
    ax.add_patch(FancyBboxPatch((x0, CONT_Y0), x1-x0, CONT_Y1-CONT_Y0,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=1.5, edgecolor=th["cedge"], facecolor=th["cont"],
        linestyle="--", mutation_aspect=1.0, zorder=1))
    ax.text((x0+x1)/2, HDR_Y, title, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=th["cedge"], zorder=4)
    cx = (x0+x1)/2; bw = (x1-x0) - 0.5
    top, bot = 4.45, 0.85; n = len(boxes); h = 0.72
    gap = (top - bot - n*h)/(n-1)
    centers = [top - h/2 - i*(h+gap) for i in range(n)]
    for (hdr, sub), cy in zip(boxes, centers):
        draw_box(cx, cy, bw, h, hdr, [sub], th["bfill"], th["bedge"],
                 hfs=9.3, bfs=8.0, gap_hd=0.05)

draw_tier(*T1, TIER1)
draw_tier(*T2, TIER2)

arrow(SENS[1]+0.02, MIDY, T1[0]-0.02, MIDY)
arrow(T1[1]+0.02,  MIDY, T2[0]-0.02, MIDY)
arrow(T2[1]+0.02,  MIDY, CLD[0]-0.02, MIDY)

ax.text(W_IN/2, H_IN - 0.26,
        r"IoT-GIS Three-Tier Architecture: Sensor Node $\rightarrow$ Edge Gateway $\rightarrow$ Cloud GIS",
        ha="center", va="center", fontsize=13.0, fontweight="bold", color="#1a1a1a")
ax.text(W_IN/2, 0.26,
        "Heterogeneous IoT sensing links feed the edge GESP validation layer; "
        "only validated packets reach the cloud GIS. Sub-8.5% latency overhead.",
        ha="center", va="center", fontsize=8.6, color="#444444")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_iot_gis_architecture.pdf"))
fig.savefig(os.path.join(outdir, "fig_iot_gis_architecture.png"), dpi=600)
plt.close(fig)
print("wrote fig_iot_gis_architecture.{png,pdf} to", os.path.abspath(outdir))

