"""Draws the two animated GIFs shown in README.md.

Run:  uv run --with pillow python docs/readme/make_gifs.py
Out:  docs/readme/how-it-works.gif   (one voice turn: you -> SFU -> STT -> LLM -> TTS -> you)
      docs/readme/how-we-build.gif   (intent -> spec -> plan -> build -> tested)

Colors have a meaning: cyan = your voice, white = text, yellow = the agent's voice.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
S = 2  # draw at 2x size, then shrink: gives smooth edges
FRAME_MS = 40  # 25 frames per second

BG = (11, 15, 20)
CARD = (20, 26, 34)
BOX = (15, 20, 27)
EDGE = (46, 56, 68)
LANE = (40, 49, 60)
TEXT = (236, 240, 244)
MUTED = (132, 145, 160)
CYAN = (31, 213, 249)  # your voice (audio)
WHITE = (236, 240, 244)  # text
YELLOW = (250, 214, 72)  # the agent's voice (audio)
VIOLET = (167, 139, 250)  # the LLM "thinking"
GREEN = (74, 222, 128)  # approved / done

FADE = 8  # frames for a fade in or out


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def font(kind: str, size: int):
    files = {
        "bold": ("Avenir Next.ttc", 0),
        "demi": ("Avenir Next.ttc", 2),
        "regular": ("Avenir Next.ttc", 7),
        "mono": ("Menlo.ttc", 0),
        "monob": ("Menlo.ttc", 1),
    }
    name, index = files[kind]
    try:
        return ImageFont.truetype(f"/System/Library/Fonts/{name}", size * S, index=index)
    except OSError:  # not on a Mac: fall back to Pillow's built-in font
        return ImageFont.load_default(size * S)


class Canvas:
    """A frame we draw on with 1x coordinates; it is stored at 2x."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (w * S, h * S), BG)
        self.d = ImageDraw.Draw(self.img)

    def rr(self, box, r, fill=None, outline=None, width=1.0):
        x0, y0, x1, y1 = box
        self.d.rounded_rectangle(
            (x0 * S, y0 * S, x1 * S, y1 * S), r * S, fill=fill, outline=outline,
            width=max(1, round(width * S)),
        )

    def glow(self, box, r, color, level):
        if level <= 0.01:
            return
        for i in range(5, 0, -1):
            off = i * 2.4
            c = mix(BG, color, level * 0.32 * (1 - i / 6))
            x0, y0, x1, y1 = box
            self.rr((x0 - off, y0 - off, x1 + off, y1 + off), r + off, outline=c, width=2.6)

    def circle(self, c, r, fill=None, outline=None, width=1.0):
        x, y = c
        self.d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S),
                       fill=fill, outline=outline, width=max(1, round(width * S)))

    def line(self, pts, fill, width=2.0):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=max(1, round(width * S)),
                    joint="curve")

    def head(self, tip, dx, dy, color, size=7.0):
        """An arrow head at `tip`, pointing in direction (dx, dy)."""
        x, y = tip
        n = math.hypot(dx, dy)
        dx, dy = dx / n, dy / n
        px, py = -dy, dx
        pts = [(x, y), (x - dx * size + px * size * 0.6, y - dy * size + py * size * 0.6),
               (x - dx * size - px * size * 0.6, y - dy * size - py * size * 0.6)]
        self.d.polygon([(a * S, b * S) for a, b in pts], fill=color)

    def text(self, xy, s, f, fill, anchor="la"):
        self.d.text((xy[0] * S, xy[1] * S), s, font=f, fill=fill, anchor=anchor)

    def text_width(self, s, f):
        return self.d.textlength(s, font=f) / S

    def done(self) -> Image.Image:
        return self.img.resize((self.w, self.h), Image.LANCZOS)


def point_on(path, t):
    """The point at fraction t (0..1) along a polyline."""
    segs = list(zip(path, path[1:]))
    lengths = [math.dist(a, b) for a, b in segs]
    goal = max(0.0, min(1.0, t)) * sum(lengths)
    for (a, b), length in zip(segs, lengths):
        if goal <= length or length == 0:
            k = goal / length if length else 0
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        goal -= length
    return path[-1]


def packet(cv: Canvas, path, t, color):
    """A glowing dot with a short tail, moving along `path`."""
    for i in range(4, 0, -1):
        tt = t - i * 0.035
        if tt >= 0:
            cv.circle(point_on(path, tt), 6 - 1.1 * i, fill=mix(BG, color, 0.65 - 0.13 * i))
    p = point_on(path, t)
    cv.circle(p, 12, fill=mix(BG, color, 0.16))
    cv.circle(p, 8.5, fill=mix(BG, color, 0.35))
    cv.circle(p, 6, fill=color)


def save_gif(frames: list[Image.Image], path: Path):
    # One shared palette for every frame, so colors don't flicker between frames.
    sample = frames[:: max(1, len(frames) // 24)]
    w, h = sample[0].size
    sheet = Image.new("RGB", (w, h * len(sample)))
    for i, f in enumerate(sample):
        sheet.paste(f, (0, i * h))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    gif = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    gif[0].save(path, save_all=True, append_images=gif[1:], duration=FRAME_MS, loop=0,
                optimize=False, disposal=1)
    print(f"wrote {path.relative_to(OUT.parent.parent)}  ({len(frames)} frames, "
          f"{path.stat().st_size // 1024} KB)")


def levels(steps, k, j, name):
    """How 'lit up' element `name` is (0..1) at frame j of step k, and its color."""
    cur, prev = steps[k], steps[k - 1]  # step -1 = last step, so the loop is smooth
    now, before = name in cur["active"], name in prev["active"]
    t = ease(j / FADE)
    if now and before:
        return 1.0, mix(prev["accent"].get(name, prev["color"]), cur["accent"].get(name, cur["color"]), t)
    if now:
        return t, cur["accent"].get(name, cur["color"])
    if before:
        return 1 - t, prev["accent"].get(name, prev["color"])
    return 0.0, cur["color"]


# --------------------------------------------------------------------------------------
# GIF 1: one voice turn
# --------------------------------------------------------------------------------------

W1, H1 = 1000, 440
YOU = (40, 120, 230, 300)
SFU = (340, 120, 560, 300)
AGENT = (660, 66, 960, 340)
PILLS = {"stt": (690, 119, 940, 177), "llm": (690, 191, 940, 249), "tts": (690, 263, 940, 321)}
TOP, BOT, SIDE = 148, 292, 922
TOP_A = [(230, TOP), (340, TOP)]
TOP_B = [(560, TOP), (690, TOP)]
BACK = [(690, BOT), (230, BOT)]
TEXT_1 = [(SIDE, 160), (SIDE, 208)]
TEXT_2 = [(SIDE, 232), (SIDE, 280)]

TURN = [
    dict(frames=50, active={"you", "top_a"}, color=CYAN, accent={},
         title="You speak",
         body=("Your microphone audio travels to the LiveKit server over WebRTC.", "regular", MUTED)),
    dict(frames=40, active={"sfu", "top_b"}, color=CYAN, accent={},
         title="The SFU forwards it",
         body=("No mixing, no re-encoding: a fast copy goes straight to the agent.", "regular", MUTED)),
    dict(frames=42, active={"stt"}, color=CYAN, accent={},
         title="STT, the ears: speech becomes text",
         body=('"Book a cleaning for Tuesday"', "mono", WHITE)),
    dict(frames=42, active={"llm"}, color=VIOLET, accent={},
         title="LLM, the brain: it writes a reply",
         body=('"Sure! Tuesday at 10 am works."', "mono", WHITE)),
    dict(frames=38, active={"tts"}, color=YELLOW, accent={},
         title="TTS, the voice: text becomes speech",
         body=("The reply is turned into the agent's audio track.", "regular", MUTED)),
    dict(frames=50, active={"sfu", "bot_b", "bot_a"}, color=YELLOW, accent={},
         title="Back through the SFU",
         body=("The agent's voice is forwarded to you, again with no mixing.", "regular", MUTED)),
    dict(frames=56, active={"you"}, color=YELLOW, accent={},
         title="You hear the answer",
         body=("One full turn takes about half a second.", "regular", MUTED)),
]


def turn_packets(k, p):
    if k == 0 and p >= 0.3:
        yield TOP_A, ease((p - 0.3) / 0.7), CYAN
    if k == 1 and p <= 0.6:
        yield TOP_B, ease(p / 0.6), CYAN
    if k == 3 and p <= 0.4:
        yield TEXT_1, ease(p / 0.4), WHITE
    if k == 4 and p <= 0.4:
        yield TEXT_2, ease(p / 0.4), WHITE
    if k == 5 and p <= 0.9:
        yield BACK, ease(p / 0.9), YELLOW


def draw_turn_frame(k, j, f_total) -> Image.Image:
    cv = Canvas(W1, H1)
    step = TURN[k]
    p = j / step["frames"]
    lv = {n: levels(TURN, k, j, n) for n in
          ["you", "sfu", "stt", "llm", "tts", "top_a", "top_b", "bot_a", "bot_b"]}

    # Header + color legend
    cv.text((40, 30), "ONE VOICE TURN", font("monob", 12), MUTED, "lm")
    x = 960
    for label, color in reversed([("your voice", CYAN), ("text", WHITE), ("agent's voice", YELLOW)]):
        x -= cv.text_width(label, font("mono", 12))
        cv.text((x, 30), label, font("mono", 12), MUTED, "lm")
        cv.circle((x - 10, 30), 4, fill=color)
        x -= 34

    # Draw order matters: glows first, then the roads, then the boxes on top.
    for name, box in [("you", YOU), ("sfu", SFU)]:
        cv.glow(box, 16, lv[name][1], lv[name][0])
    cv.rr(AGENT, 18, fill=BOX, outline=EDGE, width=1.2)
    for name, box in PILLS.items():
        cv.glow(box, 12, lv[name][1], lv[name][0])

    # Lanes (the roads between the boxes)
    for name, pts, color, direction in [
        ("top_a", TOP_A, CYAN, 1), ("top_b", TOP_B, CYAN, 1),
        ("bot_b", [(690, BOT), (560, BOT)], YELLOW, -1), ("bot_a", [(340, BOT), (230, BOT)], YELLOW, -1),
    ]:
        a = lv[name][0]
        c = mix(LANE, color, 0.25 + 0.75 * a)
        cv.line(pts, c, 2)
        cv.head(pts[-1], direction, 0, c, 8)
    cv.text((285, TOP - 13), "your voice", font("mono", 11), mix(MUTED, CYAN, lv["top_a"][0]), "mm")
    cv.text((285, BOT + 14), "agent's voice", font("mono", 11), mix(MUTED, YELLOW, lv["bot_a"][0]), "mm")

    # You
    a, color = lv["you"]
    cv.rr(YOU, 16, fill=CARD, outline=mix(EDGE, color, a), width=1.5)
    person = mix((70, 82, 96), color, a * 0.9)
    cv.circle((135, 178), 19, fill=person)
    cv.d.pieslice(((100) * S, (204) * S, (170) * S, (262) * S), 180, 360, fill=person)
    if a > 0.02:  # sound bars: speaking (cyan) or hearing (yellow)
        for i in range(4):
            h = 5 + 13 * abs(math.sin(f_total * 0.33 + i * 1.3)) * a
            bx = 168 + i * 8
            cv.line([(bx, 178 - h), (bx, 178 + h)], mix(CARD, color, a), 3)
    cv.text((135, 252), "You", font("demi", 18), TEXT, "mm")
    cv.text((135, 276), "browser or phone", font("mono", 11), MUTED, "mm")

    # LiveKit server (SFU)
    a, color = lv["sfu"]
    cv.rr(SFU, 16, fill=CARD, outline=mix(EDGE, color, a), width=1.5)
    center = (450, 182)
    sats = [(408, 160), (492, 160), (408, 204), (492, 204)]
    for i, s in enumerate(sats):
        pulse = a * (0.5 + 0.5 * math.sin(f_total * 0.3 - i * 0.9))
        cv.line([center, s], mix(LANE, color, 0.2 + 0.8 * pulse), 2)
        cv.circle(s, 6, fill=mix((70, 82, 96), color, pulse))
    cv.circle(center, 13, fill=mix((70, 82, 96), color, a), outline=CARD, width=3)
    cv.text((450, 252), "LiveKit server", font("demi", 18), TEXT, "mm")
    cv.text((450, 276), "SFU, in Docker", font("mono", 11), MUTED, "mm")

    # Voice agent (its box was drawn before the roads)
    cv.text((680, 92), "Voice agent", font("demi", 15), TEXT, "lm")
    cv.text((940, 92), "LiveKit Agents", font("mono", 11), MUTED, "rm")
    info = {"stt": ("STT", "the ears", "speech → text"),
            "llm": ("LLM", "the brain", "text → reply"),
            "tts": ("TTS", "the voice", "reply → speech")}
    for name, box in PILLS.items():
        a, color = lv[name]
        cy = (box[1] + box[3]) / 2
        cv.rr(box, 12, fill=CARD, outline=mix(EDGE, color, a), width=1.5)
        short, role, does = info[name]
        cv.text((708, cy - 9), short, font("bold", 18), mix(TEXT, color, a), "lm")
        cv.text((708 + cv.text_width(short, font("bold", 18)) + 10, cy - 9), role,
                font("demi", 14), MUTED, "lm")
        cv.text((708, cy + 13), does, font("mono", 11), MUTED, "lm")
    for y0, y1 in [(177, 191), (249, 263)]:  # small arrows between the pills
        cv.line([(SIDE, y0 + 1), (SIDE, y1 - 3)], EDGE, 2)
        cv.head((SIDE, y1 - 1), 0, 1, EDGE, 5)

    # Moving packets
    for path, t, color in turn_packets(k, p):
        packet(cv, path, t, color)

    # Caption
    cv.line([(40, 362), (960, 362)], LANE, 1)
    fade = ease(j / FADE)
    accent = step["color"]
    cv.circle((58, 401), 16, fill=mix(BG, accent, 0.16 * fade), outline=mix(BG, accent, fade), width=1.5)
    cv.text((58, 401), str(k + 1), font("bold", 15), mix(BG, accent, fade), "mm")
    cv.text((90, 390), step["title"], font("demi", 19), mix(BG, TEXT, fade), "lm")
    body, kind, body_color = step["body"]
    cv.text((90, 416), body, font(kind, 15 if kind == "regular" else 14), mix(BG, body_color, fade), "lm")
    for i in range(len(TURN)):  # progress dots
        x = 852 + i * 16
        if i == k:
            cv.rr((x - 4, 397, x + 12, 405), 4, fill=accent)
        else:
            cv.circle((x + (12 if i > k else 0), 401), 4, fill=EDGE if i > k else mix(EDGE, TEXT, 0.4))
    return cv.done()


def make_turn_gif():
    frames, total = [], 0
    for k, step in enumerate(TURN):
        for j in range(step["frames"]):
            frames.append(draw_turn_frame(k, j, total))
            total += 1
    save_gif(frames, OUT / "how-it-works.gif")


# --------------------------------------------------------------------------------------
# GIF 2: how every feature is built
# --------------------------------------------------------------------------------------

W2, H2 = 1000, 300
CARD_W, GAP, CARD_Y = 148, 55, (64, 196)  # gaps wide enough for the "approve" label
CARDS = [
    ("intent.md", "what & why,", "in your words",
     "Intent: what and why", "You say what you want, in your own words."),
    ("spec.md", "how it must", "behave",
     "Spec: how it must behave", "A sample session, the must-dos, and what is out of scope."),
    ("plan.md", "files, order", "and tests",
     "Plan: made in read-only plan mode", "Which files change, in what order, and which tests prove it."),
    ("Build", "code + tests,", "step by step",
     "Build: code + tests", "Step by step. The real test output is pasted into the plan."),
    ("Tested", "you try it,", "plan closes",
     "Tested: you try it yourself", "Only then is the plan closed. A new feature starts a new intent."),
]
WORK, APPROVE, LAST, HOLD, RESET = 42, 24, 52, 34, 14


def build_timeline():
    """A list of (kind, card index, frames)."""
    t = []
    for i in range(len(CARDS)):
        t.append(("work", i, LAST if i == len(CARDS) - 1 else WORK))
        if i < len(CARDS) - 1:
            t.append(("approve", i, APPROVE))
    t += [("hold", -1, HOLD), ("reset", -1, RESET)]
    return t


def card_box(i):
    x = 20 + i * (CARD_W + GAP)
    return (x, CARD_Y[0], x + CARD_W, CARD_Y[1])


def check(cv, c, color, size=1.0):
    x, y = c
    cv.line([(x - 5 * size, y), (x - 1.5 * size, y + 4 * size), (x + 6 * size, y - 5 * size)], color, 2.4)


def lock(cv, c, color):
    x, y = c
    cv.d.arc(((x - 4) * S, (y - 8) * S, (x + 4) * S, (y + 1) * S), 180, 360, fill=color, width=round(1.8 * S))
    cv.rr((x - 6, y - 3, x + 6, y + 6), 2, fill=color)


def draw_build_frame(seg_index, j, timeline) -> Image.Image:
    cv = Canvas(W2, H2)
    kind, idx, frames = timeline[seg_index]
    p = j / frames
    reset = 1 - ease(p) if kind == "reset" else 1.0

    # How far along is each card / gate? (active 0..1, done 0..1, approved 0..1)
    start = {}
    pos = 0
    for n, (kd, i, fr) in enumerate(timeline):
        start[(kd, i)] = (pos, fr)
        pos += fr
    now = start[(kind, idx)][0] + j

    def progress(key):
        s, fr = start[key]
        return ease((now - s) / fr)

    def active(i):
        s, _ = start[("work", i)]
        end = start[("approve", i)][0] + start[("approve", i)][1] if i < len(CARDS) - 1 \
            else start[("work", i)][0] + start[("work", i)][1]
        if now < s:
            return 0.0
        if now < end:
            return ease((now - s) / FADE)
        return 1 - ease((now - end) / FADE)

    def done(i):
        end = (start[("approve", i)][0] + start[("approve", i)][1]) if i < len(CARDS) - 1 \
            else start[("work", i)][0] + start[("work", i)][1]
        return ease((now - end) / FADE) * reset if now >= end else 0.0

    def approved(i):
        s, fr = start[("approve", i)]
        return (ease((now - s) / (fr * 0.5)) if now >= s else 0.0) * reset

    cv.text((20, 30), "HOW EVERY FEATURE IS BUILT", font("monob", 12), MUTED, "lm")
    cv.text((980, 30), "each step writes a file, and you approve it", font("mono", 12), MUTED, "rm")

    # Glows first, so nothing drawn later is hidden by them
    for i in range(len(CARDS)):
        cv.glow(card_box(i), 14, GREEN if i == len(CARDS) - 1 else CYAN, active(i) * reset)

    # Connectors and gates
    for i in range(len(CARDS) - 1):
        x0 = card_box(i)[2]
        x1 = card_box(i + 1)[0]
        gx, gy = (x0 + x1) / 2, 130
        ap = approved(i)
        c = mix(LANE, GREEN, ap)
        cv.line([(x0, gy), (gx - 13, gy)], c, 2)
        cv.line([(gx + 13, gy), (x1 - 2, gy)], c, 2)
        cv.head((x1 - 1, gy), 1, 0, c, 6)
        cv.circle((gx, gy), 13, fill=mix(CARD, GREEN, 0.18 * ap), outline=mix(EDGE, GREEN, ap), width=1.5)
        if ap > 0.5:
            check(cv, (gx, gy), mix(CARD, GREEN, (ap - 0.5) * 2), 0.9)
        else:
            lock(cv, (gx, gy + 1), mix(MUTED, CARD, ap * 2))

    # Cards
    for i, (title, sub1, sub2, _, _) in enumerate(CARDS):
        box = card_box(i)
        a = active(i) * reset
        dn = done(i)
        accent = GREEN if i == len(CARDS) - 1 else CYAN
        edge = mix(mix(EDGE, mix(EDGE, GREEN, 0.7), dn), accent, a)
        cv.rr(box, 14, fill=CARD, outline=edge, width=1.5)
        x = box[0] + 16
        cv.text((x, 86), f"STEP {i + 1}", font("mono", 11), mix(MUTED, accent, a), "lm")
        cv.text((x, 116), title, font("demi", 19), TEXT, "lm")
        cv.text((x, 148), sub1, font("regular", 14), MUTED, "lm")
        cv.text((x, 168), sub2, font("regular", 14), MUTED, "lm")
        if dn > 0.01:
            cv.circle((box[2] - 20, 86), 9, fill=mix(CARD, GREEN, 0.25 * dn))
            check(cv, (box[2] - 20, 86), mix(CARD, GREEN, dn), 0.6)

    # "approve" labels under the gates, drawn last so the cards can't cover them
    for i in range(len(CARDS) - 1):
        gx = (card_box(i)[2] + card_box(i + 1)[0]) / 2
        cv.text((gx, 156), "approve", font("mono", 10), mix(MUTED, GREEN, approved(i)), "mm")

    # Caption
    cv.line([(20, 214), (980, 214)], LANE, 1)
    fade = ease(j / FADE)
    if kind == "work":
        title, body = CARDS[idx][3], CARDS[idx][4]
        badge, accent = str(idx + 1), (GREEN if idx == len(CARDS) - 1 else CYAN)
    elif kind == "approve":
        title, body = "You approve", "Nothing moves to the next step until you say yes."
        badge, accent = "", GREEN
    else:
        title, body = "Done: tested and closed", "Then the next feature starts again at step 1."
        badge, accent = "", GREEN
        fade = fade * reset
    cv.circle((38, 253), 16, fill=mix(BG, accent, 0.16 * fade), outline=mix(BG, accent, fade), width=1.5)
    if badge:
        cv.text((38, 253), badge, font("bold", 15), mix(BG, accent, fade), "mm")
    else:
        check(cv, (38, 253), mix(BG, accent, fade), 0.9)
    cv.text((68, 242), title, font("demi", 19), mix(BG, TEXT, fade), "lm")
    cv.text((68, 268), body, font("regular", 15), mix(BG, MUTED, fade), "lm")
    return cv.done()


def make_build_gif():
    timeline = build_timeline()
    frames = []
    for n, (_, _, fr) in enumerate(timeline):
        for j in range(fr):
            frames.append(draw_build_frame(n, j, timeline))
    save_gif(frames, OUT / "how-we-build.gif")


if __name__ == "__main__":
    make_turn_gif()
    make_build_gif()
