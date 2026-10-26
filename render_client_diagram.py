#!/usr/bin/env python3
"""Render the client-specific architecture diagram for Upwork #40.

Flow is taken verbatim from the #40 submit-ready packet (screening answer 2/3):
Firecrawl fetchers over 2 subreddits / 2 forums / blog -> topic inbox ->
Telegram bot pick-list -> draft -> feedback/revise loop in the Telegram
thread -> image step (source-post image by default, else OpenAI image API)
-> approval gate (same gate) -> queue at fixed slots -> publisher wraps the
client's existing LinkedIn publishing scripts -> append-only log.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 2748, 1180
BG = (13, 17, 23)
BOX = (22, 32, 46)
BOX_EDGE = (88, 166, 255)
GATE = (46, 36, 16)
GATE_EDGE = (240, 180, 60)
TXT = (230, 237, 243)
SUB = (160, 175, 190)
ARROW = (120, 180, 240)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def font(sz, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, sz)

F_TITLE = font(54, True)
F_BOX = font(40, True)
F_SUB = font(30)
F_SMALL = font(27)

d.text((60, 36), "Social-media orchestrator — v1 architecture (LinkedIn first)", fill=TXT, font=F_TITLE)
d.text((60, 104), "Client-specific build plan for Upwork #40 — every step from the proposal's screening answer 2", fill=SUB, font=F_SUB)

def box(x, y, w, h, title, lines, gate=False):
    fill = GATE if gate else BOX
    edge = GATE_EDGE if gate else BOX_EDGE
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=fill, outline=edge, width=4)
    d.text((x + 24, y + 18), title, fill=TXT, font=F_BOX)
    ty = y + 74
    for ln in lines:
        d.text((x + 24, ty), ln, fill=SUB, font=F_SUB)
        ty += 40
    return (x, y, w, h)

def arrow(x1, y1, x2, y2, label=None):
    d.line([x1, y1, x2, y2], fill=ARROW, width=6)
    d.polygon([(x2, y2), (x2 - 22, y2 - 11), (x2 - 22, y2 + 11)], fill=ARROW)
    if label:
        d.text(((x1 + x2) / 2 - 60, y1 - 44), label, fill=SUB, font=F_SMALL)

BW, BH = 560, 190
# Row 1
b1 = box(60, 200, BW, BH, "Sources", ["2 subreddits · 2 forums", "· blog feed"])
b2 = box(740, 200, BW, BH, "Firecrawl fetchers", ["per-source adapters", "dedupe / normalize"])
b3 = box(1420, 200, BW, BH, "Topic inbox", ["every candidate topic", "lands in one inbox"])
b4 = box(2100, 200, 580, BH, "Telegram bot — pick-list", ["bot sends you the pick-list;", "you pick, not produce"])
arrow(620, 295, 740, 295)
arrow(1300, 295, 1420, 295)
arrow(1980, 295, 2100, 295)

# Row 2 (right to left)
b5 = box(2100, 520, 580, BH, "Draft + revise loop", ["draft written, feedback and", "revisions in the same thread"])
b6 = box(1420, 520, BW, BH, "Image step", ["source-post image by default", "else OpenAI image API"])
b7 = box(740, 520, BW, BH, "Approval gate", ["same gate approves text +", "image — nothing bypasses it"], gate=True)
b8 = box(60, 520, BW, BH, "Queue", ["approved posts wait at", "your fixed publish slots"])
# down from Telegram to draft loop
d.line([2390, 390, 2390, 520], fill=ARROW, width=6)
d.polygon([(2390, 520), (2379, 498), (2401, 498)], fill=ARROW)
arrow(2100, 615, 1980, 615)
arrow(1420, 615, 1300, 615)
arrow(740, 615, 620, 615)
# revise loop-back: draft back up to Telegram thread
d.line([2160, 520, 2160, 440], fill=ARROW, width=4)
d.text((1740, 452), "feedback / revise — same Telegram thread", fill=SUB, font=F_SMALL)

# Row 3
b9 = box(60, 840, BW, BH, "Publisher", ["wraps your existing LinkedIn", "scripts — not rewritten"])
b10 = box(740, 840, BW, BH, "LinkedIn", ["posts publish at the", "queued slots"])
b11 = box(1420, 840, 1260, BH, "Append-only event log", ["fetch · pick · draft · approve · publish —", "'did it go out?' is always answerable"])
d.line([340, 710, 340, 840], fill=ARROW, width=6)
d.polygon([(340, 840), (329, 818), (351, 818)], fill=ARROW)
arrow(620, 935, 740, 935)
arrow(1300, 935, 1420, 935)

d.text((60, 1080), "Python on Hetzner · pre-commit + GitHub Actions from the first commit · channel #2 = one new publisher module, not a rebuild", fill=SUB, font=F_SUB)

img.save("/home/hatch/workspace/agent-venture/shop-sample-orchestrator/architecture-diagram-client.png")
print("saved")
