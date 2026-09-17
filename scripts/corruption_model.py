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

SOURCES = [
    ("IoT Sensor Network",
     ["500-node cluster", "LoRaWAN / Wi-Fi 6", "ZigBee / NB-IoT"],
     dict(fill="#D3E9E4", edge="#2E8B8B")),
    ("NIST P-256 Key Infrastructure",
     ["Merkle cert. store", r"$O(\log N)$ membership proofs",
      r"$sk_i$ / $pk_i$ provisioned"],
     dict(fill="#E4D7F0", edge="#7A4FA3")),
    ("Dolev\u2013Yao Adversary $\\mathcal{A}$",
     ["Eavesdrop / inject / replay", "Commodity SDR", "No valid key material"],
     dict(fill="#F6D6D2", edge="#C0392B")),
]
STAGE1 = ("1 \u2014 Packet Ingestion", [
    r"Sensor reads $(\varphi,\lambda,\rho)$",
    r"Assemble $P_i=(\varphi,\lambda,\rho,t,v)$",
    r"ECDSA sign at node",
    r"Forward to edge gateway",
], dict(fill="#FBE7B8", edge="#B8860B"))
STAGE2 = ("2 \u2014 Corruption Scenarios", [
    "GPS coordinate falsification",
    "Sensor payload injection",
    r"Packet replay ($v_i$ stale)",
    "Sybil identity injection",
], dict(fill="#F6D2CE", edge="#C0504D"))
STAGE3 = ("3 \u2014 GESP Defences", [
    r"ECDSA $\sigma_i$ verification",
    r"Freshness window $\Delta_t=30$ s",
    r"Sequence-no monotonicity",
    r"Mahalanobis $D^2>\chi^2$; $|z|>3\sigma$",
], dict(fill="#D5EAD5", edge="#3E8E4E"))
STAGE4 = ("4 \u2014 Validate & Store", [
    r"Peer-consensus tally ($\tau=2/3$)",
    r"Accept if $A_i\leq 0.5$",
    "Append to PostGIS store",
    "Write immutable audit log",
], dict(fill="#CFE2F3", edge="#2E6DA4"))

STORE_TITLE = "Validated Spatial Data Store"
STORE_ITEMS = [
    ("Signed Packets", r"WGS-84 $(\varphi,\lambda,\rho,t,v)$ · 64-byte sig",
     dict(fill="#CFE2F3", edge="#2E6DA4")),
    ("Spatial Index", "PostGIS / R-tree \u00b7 geohash keys",
     dict(fill="#D3E9E4", edge="#2E8B8B")),
    ("Provenance", "node ID \u00b7 pk fingerprint \u00b7 verdict",
     dict(fill="#F5E6C8", edge="#B8860B")),
    ("Audit Log", "append-only \u00b7 tamper-evident",
     dict(fill="#D5EAD5", edge="#3E8E4E")),
]

W_IN, H_IN = 15.0, 6.4
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

def draw_box(cx, cy, w, h, header, body, fill, edge,
             hfs=10.0, bfs=8.3, gap_hd=0.10, header_left=False):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.09",
        linewidth=1.5, edgecolor=edge, facecolor=fill, mutation_aspect=1.0, zorder=3))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body) * LB if body else 0)
    top = cy + block_h/2
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
    """Orthogonal connector: horizontal -> vertical -> horizontal (0/90 only)."""
    ax.plot([x0, xm], [y0, y0], color=color, lw=lw, solid_capstyle="projecting", zorder=2)
    ax.plot([xm, xm], [y0, y1], color=color, lw=lw, solid_capstyle="projecting", zorder=2)
    ax.add_patch(FancyArrowPatch((xm, y1), (x1, y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=2))

A_cx, A_w, A_h = 1.65, 2.9, 1.25
A_centers = [4.70, 3.15, 1.60]
for (hdr, body, col), cy in zip(SOURCES, A_centers):
    draw_box(A_cx, cy, A_w, A_h, hdr, body, col["fill"], col["edge"], hfs=9.6, bfs=8.0)

B_cx, C_cx, ST_w, ST_h = 5.55, 9.55, 3.0, 1.60
top_cy, bot_cy = 4.00, 1.75
draw_box(B_cx, top_cy, ST_w, ST_h, *[STAGE1[0], STAGE1[1]],
         fill=STAGE1[2]["fill"], edge=STAGE1[2]["edge"], hfs=10.0, bfs=8.3, header_left=True)
draw_box(B_cx, bot_cy, ST_w, ST_h, STAGE2[0], STAGE2[1],
         STAGE2[2]["fill"], STAGE2[2]["edge"], hfs=10.0, bfs=8.3, header_left=True)
draw_box(C_cx, top_cy, ST_w, ST_h, STAGE3[0], STAGE3[1],
         STAGE3[2]["fill"], STAGE3[2]["edge"], hfs=10.0, bfs=8.3, header_left=True)
draw_box(C_cx, bot_cy, ST_w, ST_h, STAGE4[0], STAGE4[1],
         STAGE4[2]["fill"], STAGE4[2]["edge"], hfs=10.0, bfs=8.3, header_left=True)

D_x0, D_x1, D_y0, D_y1 = 11.62, 14.55, 1.00, 5.20
ax.add_patch(FancyBboxPatch((D_x0, D_y0), D_x1-D_x0, D_y1-D_y0,
    boxstyle="round,pad=0.02,rounding_size=0.10",
    linewidth=1.6, edgecolor="#5A6B7B", facecolor="#EEF1F5", mutation_aspect=1.0, zorder=1))
ax.text((D_x0+D_x1)/2, 4.90, STORE_TITLE, ha="center", va="center",
        fontsize=10.5, fontweight="bold", color="#41505E", zorder=4)
D_cx, D_w, D_h = (D_x0+D_x1)/2, 2.62, 0.72
D_centers = [4.26, 3.36, 2.46, 1.56]
for (hdr, sub, col), cy in zip(STORE_ITEMS, D_centers):
    draw_box(D_cx, cy, D_w, D_h, hdr, [sub], col["fill"], col["edge"],
             hfs=9.0, bfs=7.6, gap_hd=0.05)

arrow(A_cx + A_w/2 + 0.02, 4.50, B_cx - ST_w/2 - 0.02, 4.50)
arrow(A_cx + A_w/2 + 0.02, 3.50, B_cx - ST_w/2 - 0.02, 3.50)
arrow(A_cx + A_w/2 + 0.02, 1.60, B_cx - ST_w/2 - 0.02, 1.60,
      color="#C0392B", lw=1.6)
ax.text((A_cx + A_w/2 + B_cx - ST_w/2)/2, 1.60 + 0.16, "inject / replay",
        ha="center", va="bottom", fontsize=8.0, style="italic", color="#C0392B", zorder=4)

arrow(B_cx + ST_w/2 + 0.02, 4.00, C_cx - ST_w/2 - 0.02, 4.00)

elbow_hvh(B_cx + ST_w/2 + 0.02, bot_cy, C_cx - ST_w/2 - 0.02, 3.50,
          xm=(B_cx + ST_w/2 + C_cx - ST_w/2)/2, color="#C0504D", lw=1.4)

arrow(C_cx, top_cy - ST_h/2 - 0.02, C_cx, bot_cy + ST_h/2 + 0.02)

arrow(C_cx + ST_w/2 + 0.02, bot_cy, D_x0 - 0.02, bot_cy)

ax.text(W_IN/2, H_IN - 0.28,
        "Spatial Data-Corruption Model: Dolev\u2013Yao Attack Scenarios and Data Flow",
        ha="center", va="center", fontsize=13.5, fontweight="bold", color="#1a1a1a")
ax.text(W_IN/2, 0.26,
        "Signed packets are ingested, subjected to Dolev\u2013Yao corruption "
        "scenarios, screened by the GESP defence stack, and only validated "
        "packets are written to the spatial data store.",
        ha="center", va="center", fontsize=8.6, color="#444444")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_corruption_model.pdf"))
fig.savefig(os.path.join(outdir, "fig_corruption_model.png"), dpi=600)
plt.close(fig)
print("wrote fig_corruption_model.{png,pdf} to", os.path.abspath(outdir))

