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

RED, REDF   = "#C0392B", "#F6D6D2"
TEAL, TEALF = "#2E8B8B", "#D3E9E4"
ORA, ORAF   = "#D9822B", "#FBE0C6"
BLU, BLUF   = "#2E6DA4", "#CFE2F3"
SLATE       = "#46617E"
GREEN       = "#3E8E4E"
NOTEF, NOTEE = "#FCF3D9", "#D9B44A"
B1, B2, B3  = "#F2EFF9", "#EEF5F3", "#F6F1EA"

W_IN, H_IN = 13.2, 9.4
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

NX = {"ni": 1.55, "nj": 3.35, "nk": 5.15, "nl": 6.95, "gw": 9.35, "cloud": 11.75}
LL_TOP, LL_BOT = 8.31, 1.75

def draw_box(cx, cy, w, h, header, body, fill, edge, hfs=9.0, bfs=7.8,
             gap_hd=0.05, ls="solid"):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.5, edgecolor=edge, facecolor=fill, linestyle=ls,
        mutation_aspect=1.0, zorder=5))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body)*LB if body else 0)
    top = cy + block_h/2
    ax.text(cx, top-HH/2, header, ha="center", va="center",
            fontsize=hfs, fontweight="bold", color=edge, zorder=6)
    y = top - HH - gap_hd
    for line in body:
        ax.text(cx, y-LB/2, line, ha="center", va="center",
                fontsize=bfs, color="#333333", zorder=6)
        y -= LB

def note(cx, cy, text, w=None, fs=7.8):
    lines = text.split("\n")
    LB = lh(fs)
    if w is None:
        w = max(len(l) for l in lines)*fs*0.60/72 + 0.30
    h = len(lines)*LB + 0.18
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.1, edgecolor=NOTEE, facecolor=NOTEF, mutation_aspect=1.0, zorder=6))
    top = cy + len(lines)*LB/2
    for i, l in enumerate(lines):
        ax.text(cx, top-LB/2-i*LB, l, ha="center", va="center",
                fontsize=fs, color="#5b4a1a", zorder=7)

def msg(y, xf, xt, label, color):
    ax.add_patch(FancyArrowPatch((xf, y), (xt, y), arrowstyle="-|>",
        mutation_scale=15, linewidth=1.7, color=color, shrinkA=0, shrinkB=0, zorder=4))
    ax.text((xf+xt)/2, y+0.11, label, ha="center", va="bottom",
            fontsize=7.7, color=color, zorder=7,
            bbox=dict(boxstyle="round,pad=0.12", fc="#FCFCFC", ec="none"))

BANDS = [(5.65, 8.20, B1, "PHASE 1  ·  BROADCAST", "#6A4C93"),
         (4.15, 5.65, B2, "PHASE 2  ·  VOTE", "#2E8B8B"),
         (1.75, 4.15, B3, "PHASE 3  ·  TALLY & ACCEPT", "#B5722A")]
for y0, y1, c, lab, lc in BANDS:
    ax.add_patch(Rectangle((0.30, y0), W_IN-0.60, y1-y0, facecolor=c,
                           edgecolor="none", zorder=0))
    ax.text(0.48, y1-0.03, lab, ha="left", va="top", fontsize=9.2,
            fontweight="bold", color=lc, zorder=2,
            bbox=dict(boxstyle="round,pad=0.14", fc=c, ec="none"))

for key, x in NX.items():
    ax.plot([x, x], [LL_BOT, LL_TOP], color=(RED if key == "ni" else "#AAAAAA"),
            lw=1.2, linestyle=(0, (5, 4)), zorder=1)

HY = 8.63
draw_box(NX["ni"], HY, 1.62, 0.66, "Node $n_i$", ["(Byzantine)"], REDF, RED, ls="--")
for key in ("nj", "nk", "nl"):
    nm = {"nj": "Node $n_j$", "nk": "Node $n_k$", "nl": "Node $n_l$"}[key]
    draw_box(NX[key], HY, 1.62, 0.66, nm, ["(Legitimate)"], TEALF, TEAL)
draw_box(NX["gw"], HY, 1.62, 0.66, "Edge GW", [], ORAF, ORA)
draw_box(NX["cloud"], HY, 1.62, 0.66, "GIS Cloud", [], BLUF, BLU)

note(NX["ni"], 7.66, "Spatial data ingested", fs=7.6)
msg(7.28, NX["ni"], NX["nj"], "$F_i^*$ [SPOOFED]", RED)
msg(6.96, NX["ni"], NX["nk"], "$F_i^*$", RED)
msg(6.64, NX["ni"], NX["nl"], "$F_i^*$", RED)
msg(6.32, NX["nj"], NX["gw"], "$F_j$ [authentic]", TEAL)
msg(6.03, NX["nk"], NX["gw"], "$F_k$ [authentic]", TEAL)
msg(5.74, NX["nl"], NX["gw"], "$F_l$ [authentic]", TEAL)

msg(5.32, NX["nj"], NX["gw"], r"$V_{ji}=0$   (coord. anomaly)", SLATE)
msg(4.89, NX["nk"], NX["gw"], r"$V_{ki}=0$   (Mahalanobis $D^2>\chi^2$)", SLATE)
msg(4.46, NX["nl"], NX["gw"], r"$V_{li}=0$   (seq. mismatch)", SLATE)

note(NX["gw"], 3.68, r"Weighted tally:  0/3 approvals < $\tau=2/3$", fs=7.8)
msg(3.05, NX["gw"], NX["ni"], "QUARANTINE $n_i$", RED)
note(NX["gw"], 2.48, "$F_j$ approved  (3/3 votes)", fs=7.8)
msg(1.98, NX["gw"], NX["cloud"], "Validated stream", GREEN)

ax.text(W_IN/2, H_IN-0.24,
        "GESP Byzantine-Consensus Round: Spoofed-Packet Rejection",
        ha="center", va="center", fontsize=14, fontweight="bold", color="#1a1a1a")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig3_consensus.pdf"))
fig.savefig(os.path.join(outdir, "fig3_consensus.png"), dpi=600)
plt.close(fig)
print("wrote fig3_consensus.png,pdf to", os.path.abspath(outdir))

