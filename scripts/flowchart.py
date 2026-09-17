import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.fontset": "stixsans",
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})

C_START = dict(fill="#D5EAD5", edge="#3E8E4E")
C_PROC  = dict(fill="#E2E9F2", edge="#45699A")
C_DEC   = dict(fill="#FBEBC8", edge="#B8901F")
C_DROP  = dict(fill="#F6D6D2", edge="#C0392B")
C_FLAG  = dict(fill="#FBE0C6", edge="#D9822B")
C_QUAR  = dict(fill="#E4D7F0", edge="#7A4FA3")
TCOL = {"drop": C_DROP, "flag": C_FLAG, "quar": C_QUAR}
YES_C, NO_C = "#3E8E4E", "#C0392B"

spine = [
 dict(kind="start", head="START", body=[r"Sensor packet $F_i$ received"], h=0.54),
 dict(kind="proc",  head="Verify ECDSA signature", body=[r"$\sigma_i$   (NIST P-256)"], h=0.62),
 dict(kind="dec",   head="Valid signature?", body=[], h=0.84,
      down="YES", right="NO", term="DROP & LOG", tc="drop"),
 dict(kind="proc",  head="Check timestamp freshness",
      body=[r"$|t_i - t_{\mathrm{now}}| \leq \Delta t$"], h=0.62),
 dict(kind="dec",   head="Timestamp fresh?", body=[], h=0.84,
      down="YES", right="NO", term="REPLAY REJECT", tc="drop"),
 dict(kind="proc",  head="Check sequence number",
      body=[r"$v_i > v_i^{\mathrm{prev}}$"], h=0.62),
 dict(kind="dec",   head="Seq-number valid?", body=[], h=0.84,
      down="YES", right="NO", term="DROP & LOG", tc="drop"),
 dict(kind="proc",  head="Spatial anomaly filter",
      body=[r"Mahalanobis $D^2$ test"], h=0.62),
 dict(kind="dec",   head="Anomaly score", body=[r"$A_i > 0.5$?"], h=0.90,
      down="NO", right="YES", term="SOFT FLAG", tc="flag"),
 dict(kind="proc",  head="Peer consensus ballot",
      body=[r"($\geq 2/3$ weighted votes)"], h=0.62),
 dict(kind="dec",   head="Consensus passed?", body=[], h=0.84,
      down="YES", right="NO", term="QUARANTINE", tc="quar"),
 dict(kind="term",  head="ACCEPT", body=["forward to GIS cloud"], h=0.58),
]

XS, XT = 2.55, 6.05
PROC_W, DEC_W, SE_W, TERM_W = 2.65, 2.35, 2.65, 1.95
GAP, TOP_M, BOT_M = 0.28, 0.62, 0.32
W_IN = 7.5

def lh(fs): return fs * 1.16 / 72.0
total = sum(e["h"] for e in spine) + (len(spine)-1)*GAP
H_IN = total + TOP_M + BOT_M

cur = H_IN - TOP_M
for e in spine:
    e["cy"] = cur - e["h"]/2
    cur -= (e["h"] + GAP)

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

def draw_box(cx, cy, w, h, header, body, fill, edge, hfs=8.4, bfs=7.8,
             gap_hd=0.05, stadium=False, hcolor=None):
    rs = h*0.46 if stadium else 0.06
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rs}",
        linewidth=1.4, edgecolor=edge, facecolor=fill, mutation_aspect=1.0, zorder=4))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body)*LB if body else 0)
    top = cy + block_h/2
    ax.text(cx, top - HH/2, header, ha="center", va="center", fontsize=hfs,
            fontweight="bold", color=hcolor or edge, zorder=5)
    y = top - HH - gap_hd
    for line in body:
        ax.text(cx, y - LB/2, line, ha="center", va="center",
                fontsize=bfs, color="#1a1a1a", zorder=5)
        y -= LB

def draw_diamond(cx, cy, w, h, lines, fill, edge, fs=8.2):
    ax.add_patch(Polygon([(cx, cy+h/2), (cx+w/2, cy), (cx, cy-h/2), (cx-w/2, cy)],
        closed=True, linewidth=1.4, edgecolor=edge, facecolor=fill, zorder=4))
    LB = lh(fs); top = cy + (len(lines)*LB)/2
    for i, line in enumerate(lines):
        ax.text(cx, top - LB/2 - i*LB, line, ha="center", va="center",
                fontsize=fs, fontweight="bold", color="#333333", zorder=5)

def varrow(x, y0, y1, color="#444444", lw=1.5, ms=14):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=3))
def harrow(x0, x1, y, color="#444444", lw=1.5, ms=14):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=3))

for e in spine:
    k = e["kind"]
    if k == "dec":
        lines = [e["head"]] + e["body"]
        draw_diamond(XS, e["cy"], DEC_W, e["h"], lines, C_DEC["fill"], C_DEC["edge"])
    elif k == "proc":
        draw_box(XS, e["cy"], PROC_W, e["h"], e["head"], e["body"],
                 C_PROC["fill"], C_PROC["edge"], hcolor="#2f527d")
    else:
        draw_box(XS, e["cy"], SE_W, e["h"], e["head"], e["body"],
                 C_START["fill"], C_START["edge"], stadium=True, hfs=9.0)

for a, b in zip(spine[:-1], spine[1:]):
    y0 = a["cy"] - a["h"]/2
    y1 = b["cy"] + b["h"]/2
    varrow(XS, y0, y1)
    if a["kind"] == "dec":
        col = YES_C if a["down"] == "YES" else NO_C
        ax.text(XS + 0.13, (y0+y1)/2, a["down"], ha="left", va="center",
                fontsize=7.4, fontweight="bold", color=col, zorder=6)

for e in spine:
    if e["kind"] != "dec":
        continue
    col = TCOL[e["tc"]]
    draw_box(XT, e["cy"], TERM_W, 0.56, e["term"], [], col["fill"], col["edge"], hfs=8.6)
    x0 = XS + DEC_W/2
    harrow(x0, XT - TERM_W/2, e["cy"], color=col["edge"])
    lc = YES_C if e["right"] == "YES" else NO_C
    ax.text((x0 + XT - TERM_W/2)/2, e["cy"] + 0.12, e["right"], ha="center",
            va="bottom", fontsize=7.4, fontweight="bold", color=lc, zorder=6)

ax.text(W_IN/2, H_IN - TOP_M/2, "GESP Packet-Validation Decision Flow",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#1a1a1a")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig2_flowchart.pdf"))
fig.savefig(os.path.join(outdir, "fig2_flowchart.png"), dpi=600)
plt.close(fig)
print(f"wrote fig2_flowchart.png,pdf  (H_IN={H_IN:.2f}) to", os.path.abspath(outdir))

