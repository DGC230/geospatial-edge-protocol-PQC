import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.fontset": "stixsans",
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})

ENTITIES = [
    ("Node Registry", "#3E8E4E", [
        ("PK", "node_id"),
        ("", "cluster_id · link_type"),
        ("", "pk_fingerprint (P-256)"),
        ("", "role (sensor / gateway)"),
        ("", "provisioned_at"),
    ]),
    ("Spatial Packet", "#2E6DA4", [
        ("PK", "packet_id"),
        ("FK", "node_id"),
        ("", "gps_lat · gps_lon (WGS-84)"),
        ("", r"payload $\rho$ · timestamp $t$"),
        ("", r"seq_no $v$"),
    ]),
    ("Verification", "#7A4FA3", [
        ("PK", "verify_id"),
        ("FK", "packet_id"),
        ("", "ecdsa_sig (64-byte)"),
        ("", r"sig_valid · fresh ($\Delta_t\leq30$ s)"),
        ("", "seq_monotonic"),
    ]),
    ("Validation Verdict", "#C8912B", [
        ("PK", "verdict_id"),
        ("FK", "packet_id"),
        ("", r"mahalanobis $D^2$ · z-score"),
        ("", r"anomaly_score $A_i$"),
        ("", r"consensus ($\tau=2/3$) · result"),
    ]),
]
RELATIONS = ["1:N", "1:1", "1:1"]

W_IN, H_IN = 14.9, 4.2
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

EW, EH = 2.9, 1.70
CY = 2.30
HB = 0.34
FLINE = 0.205
ML = 0.35
STEP = 3.75
centers = [ML + EW/2 + i*STEP for i in range(4)]

def draw_entity(cx, name, edge, fields):
    x0, y1 = cx - EW/2, CY + EH/2

    ax.add_patch(FancyBboxPatch((cx-EW/2, CY-EH/2), EW, EH,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.4, edgecolor=edge, facecolor="white", zorder=3))

    ax.add_patch(Rectangle((cx-EW/2+0.06, y1-HB-0.01), EW-0.12, HB,
        facecolor=edge, edgecolor="none", zorder=4))
    ax.text(cx, y1-0.01-HB/2, name, ha="center", va="center", color="white",
            fontsize=9.6, fontweight="bold", zorder=5)

    y = y1 - HB - 0.15
    xL = cx - EW/2 + 0.16
    for tag, txt in fields:
        if tag:
            ax.text(xL, y, tag, ha="left", va="center", fontsize=7.3,
                    fontweight="bold", color=edge, zorder=5)
        ax.text(xL + 0.44, y, txt, ha="left", va="center", fontsize=8.0,
                color="#1a1a1a", zorder=5)
        y -= FLINE

for cx, (name, edge, fields) in zip(centers, ENTITIES):
    draw_entity(cx, name, edge, fields)

def relation(x0, x1, y, label):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>",
        mutation_scale=13, linewidth=1.4, color="#666666",
        shrinkA=0, shrinkB=0, zorder=2))
    ax.text((x0+x1)/2, y, label, ha="center", va="center",
            fontsize=8.2, fontweight="bold", color="#333333",
            bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="#999999", lw=0.8),
            zorder=6)

for i in range(3):
    relation(centers[i] + EW/2 + 0.02, centers[i+1] - EW/2 - 0.02, CY, RELATIONS[i])

ax.text(W_IN/2, H_IN - 0.28,
        "Relational Schema of the GESP Validated Spatial Data Store",
        ha="center", va="center", fontsize=13.0, fontweight="bold", color="#1a1a1a")
ax.text(W_IN/2, 0.40,
        "PK \u2014 primary key   \u00b7   FK \u2014 foreign key   \u00b7   "
        "1:N / 1:1 \u2014 relationship cardinality",
        ha="center", va="center", fontsize=8.6, color="#555555")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_dataset_structure.pdf"))
fig.savefig(os.path.join(outdir, "fig_dataset_structure.png"), dpi=600)
plt.close(fig)
print("wrote fig_dataset_structure.{png,pdf} to", os.path.abspath(outdir))

