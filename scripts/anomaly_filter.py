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

COMP1 = ("Coordinate Consistency Filter", [
    "Mahalanobis distance test",
    r"$D_M^2>\chi^2_{2,0.99}\approx9.21$",
    r"History window $W\geq30$ GPS pairs",
    r"Weight $w_c=0.7$",
], dict(fill="#E4D7F0", edge="#7A4FA3"))
COMP2 = ("Sensor Payload Filter", [
    r"Z-score on rolling window $W$",
    r"$z=|\rho_i-\mu_{\mathrm{roll}}|/\sigma_{\mathrm{roll}}>3\sigma$",
    r"Soft flag $\rightarrow$ consensus vote",
    r"Weight $w_s=0.3$",
], dict(fill="#F6D6D2", edge="#C0392B"))
INPUT = ("Input GPS Packet", [
    r"$(\varphi_i,\lambda_i,\rho_i,t_i,v_i)$",
    "500-node cluster",
], dict(fill="#D3E9E4", edge="#2E8B8B"))
COMPOSITE = ("Composite Score & Consensus Tally", [
    r"$A_i=0.7\,c_{\mathrm{coord}}+0.3\,c_{\mathrm{sensor}}$",
    r"If $A_i>0.5$: cast negative vote",
    r"Geo-weighted tally $\sum(\mathrm{vote}/\mathrm{dist})$",
    r"Accept if approval $\geq\tau=2/3$",
    r"Byzantine-tolerant $K<n/3$",
    "PostGIS store of validated packets",
], dict(fill="#E9E3C4", edge="#8A7D2A"))
VALID = ("GESP-Validated Spatial Packet", [
    "IoT node: Class-1 / nRF9160",
    r"64-byte ECDSA $\sigma$ (NIST P-256)",
    r"WGS-84 $(\varphi,\lambda)$ · payload $\rho_i$",
    r"Timestamp $t_i$ · seq $v_i$",
    "Forwarded to Cloud GIS",
], dict(fill="#CFE2F3", edge="#2E6DA4"))
OUTPUTS = [
    ("ACCEPTED",    r"$\rightarrow$ Cloud GIS", 3.75, dict(fill="#D5EAD5", edge="#3E8E4E")),
    ("QUARANTINED", "Byzantine node",           2.55, dict(fill="#F6D6D2", edge="#C0392B")),
    ("FLAGGED",     "Soft anomaly",             1.55, dict(fill="#FBE0C6", edge="#D9822B")),
]

W_IN, H_IN = 15.5, 5.7
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

def draw_box(cx, cy, w, h, header, body, fill, edge, hfs=9.5, bfs=8.0,
             gap_hd=0.08, header_left=False, top_align=False):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.07",
        linewidth=1.4, edgecolor=edge, facecolor=fill, mutation_aspect=1.0, zorder=3))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body)*LB if body else 0)
    top = (cy + h/2 - 0.14) if top_align else (cy + block_h/2)
    xb = (cx - w/2 + 0.15) if header_left else cx
    ha = "left" if header_left else "center"
    ax.text(xb, top - HH/2, header, ha=ha, va="center",
            fontsize=hfs, fontweight="bold", color=edge, zorder=4)
    y = top - HH - gap_hd
    for line in body:
        ax.text(xb, y - LB/2, line, ha=ha, va="center",
                fontsize=bfs, color="#1a1a1a", zorder=4)
        y -= LB

def arrow(x0, y0, x1, y1, color="#333333", lw=1.6, ms=15):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=2))

def elbow_hvh(x0, y0, x1, y1, xm, color="#333333", lw=1.6, ms=15):
    ax.plot([x0, xm], [y0, y0], color=color, lw=lw, solid_capstyle="projecting", zorder=2)
    ax.plot([xm, xm], [y0, y1], color=color, lw=lw, solid_capstyle="projecting", zorder=2)
    ax.add_patch(FancyArrowPatch((xm, y1), (x1, y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=2))

INP = (0.30, 2.05)
CMP = (2.65, 5.75)
CMPO = (6.35, 9.45)
VAL = (10.05, 12.55)
OUT_cx, OUT_w = 13.90, 1.80

draw_box((INP[0]+INP[1])/2, 2.80, INP[1]-INP[0], 0.95, INPUT[0], INPUT[1],
         INPUT[2]["fill"], INPUT[2]["edge"], hfs=9.3, bfs=8.2)
draw_box((CMP[0]+CMP[1])/2, 3.85, CMP[1]-CMP[0], 1.35, COMP1[0], COMP1[1],
         COMP1[2]["fill"], COMP1[2]["edge"], header_left=True)
draw_box((CMP[0]+CMP[1])/2, 1.75, CMP[1]-CMP[0], 1.35, COMP2[0], COMP2[1],
         COMP2[2]["fill"], COMP2[2]["edge"], header_left=True)

draw_box((CMPO[0]+CMPO[1])/2, 2.80, CMPO[1]-CMPO[0], 2.60, COMPOSITE[0], COMPOSITE[1],
         COMPOSITE[2]["fill"], COMPOSITE[2]["edge"], header_left=True, top_align=True)
draw_box((VAL[0]+VAL[1])/2, 2.80, VAL[1]-VAL[0], 2.60, VALID[0], VALID[1],
         VALID[2]["fill"], VALID[2]["edge"], header_left=True, top_align=True)

for name, sub, y, col in OUTPUTS:
    draw_box(OUT_cx, y, OUT_w, 0.78, name, [sub], col["fill"], col["edge"],
             hfs=9.2, bfs=8.0, gap_hd=0.05)

elbow_hvh(INP[1]+0.02, 2.80, CMP[0]-0.02, 3.85, xm=2.35, color="#666666", lw=1.3)
elbow_hvh(INP[1]+0.02, 2.80, CMP[0]-0.02, 1.75, xm=2.35, color="#666666", lw=1.3)

arrow(CMP[1]+0.02, 3.85, CMPO[0]-0.02, 3.85)
arrow(CMP[1]+0.02, 1.75, CMPO[0]-0.02, 1.75)

arrow(CMPO[1]+0.02, 2.80, VAL[0]-0.02, 2.80)

for name, sub, y, col in OUTPUTS:
    arrow(VAL[1]+0.02, y, OUT_cx - OUT_w/2 - 0.02, y, color=col["edge"], lw=1.6)

ax.text(W_IN/2, H_IN - 0.28,
        "GESP Dual-Component Spatial Anomaly Filter Architecture",
        ha="center", va="center", fontsize=13.5, fontweight="bold", color="#1a1a1a")
ax.text(W_IN/2, 0.32,
        r"Coordinate anomaly $w_c=0.7$ · payload anomaly $w_s=0.3$ · "
        r"96.5% detection at $K=20$% · false-positive rate < 1.2%",
        ha="center", va="center", fontsize=8.6, color="#444444")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_anomaly_filter.pdf"))
fig.savefig(os.path.join(outdir, "fig_anomaly_filter.png"), dpi=600)
plt.close(fig)
print("wrote fig_anomaly_filter.{png,pdf} to", os.path.abspath(outdir))

