#!/usr/bin/env python3
"""Generate the compressed stage-2 composition framework for sections 4–7."""

from __future__ import annotations

import json
import struct
from pathlib import Path

from generate_continuity_sketch_v02 import TPQ, note, note_track, track


BPM = 72
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audio" / "late_arc_sketch_v04"


ZHU = (
    # 0–24: farewell. Her complete arch now contains broader internal waits.
    note(0.5, 0.5, 64, 63), note(1, 1, 67, 67), note(2, 3, 69, 72),
    note(5, 1, 67, 65), note(6, 2, 64, 61),
    note(8, 1, 64, 62), note(9, 1, 67, 67), note(10, 1, 69, 71),
    note(11, 3, 72, 77), note(14, 2, 69, 70), note(16, 2, 67, 65),
    note(18, 2, 64, 60), note(20, 4, 62, 56),
    # 24–48: recognition. The line stays coherent while Liang comes closer.
    note(24, 1, 64, 64), note(25, 1, 67, 68), note(26, 2, 69, 73),
    note(28, 1, 72, 77), note(29, 2, 69, 71), note(31, 1, 67, 66),
    note(32, 2, 64, 63), note(34, 1, 67, 68), note(35, 1, 69, 72),
    note(36, 2, 72, 78), note(38, 2, 69, 72), note(40, 2, 67, 67),
    note(42, 2, 64, 62), note(44, 4, 62, 58),
    # 48–72: marriage proceeds. Her phrase remains but is placed farther apart.
    note(48, 1, 64, 60), note(49, 1, 67, 64), note(50, 3, 69, 68),
    note(53, 1, 67, 62), note(54, 2, 64, 58),
    note(58, 1, 64, 57), note(59, 1, 67, 61), note(60, 3, 69, 65),
    note(63, 1, 72, 69), note(64, 2, 69, 63), note(66, 2, 67, 59),
    note(68, 4, 62, 53),
    # 72–92: grave and final convergence. Complete, slow, and non-triumphant.
    note(72, 1, 64, 56), note(73, 1, 67, 60), note(74, 3, 69, 65),
    note(77, 1, 72, 69), note(78, 2, 69, 63), note(80, 2, 67, 59),
    note(82, 2, 64, 55), note(84, 2, 72, 64), note(86, 2, 69, 60),
    note(88, 2, 67, 56), note(90, 2, 64, 52), note(92, 2, 62, 48),
)


LIANG = (
    # Farewell: he answers with his established grounded line.
    note(4, 2, 57, 60), note(6, 2, 55, 58), note(8, 2, 52, 56),
    note(10, 4, 50, 54), note(14, 2, 52, 56), note(16, 2, 55, 59),
    note(18, 2, 57, 62), note(20, 4, 50, 54),
    # Recognition: for the first time he borrows her E–G–A rising direction,
    # then folds it back into his own descending grammar.
    note(26, 1, 52, 60), note(27, 1, 55, 64), note(28, 2, 57, 69),
    note(30, 1, 60, 72), note(31, 2, 57, 67), note(33, 1, 55, 63),
    note(34, 2, 52, 60), note(36, 1, 55, 64), note(37, 1, 57, 68),
    note(38, 2, 60, 72), note(40, 2, 57, 67), note(42, 2, 55, 62),
    note(44, 4, 50, 55),
    # Wedding/funeral: only the downward opening remains, then he exits at 64.
    note(48, 3, 57, 58), note(51, 2, 55, 55), note(53, 3, 52, 51),
    note(56, 3, 57, 52), note(59, 2, 55, 48), note(61, 3, 50, 43),
    # Grave: not a living return, but the remembered contour approaches Zhu.
    note(82, 2, 50, 42), note(84, 2, 52, 45), note(86, 2, 55, 48),
    note(88, 2, 57, 50), note(90, 2, 60, 49), note(92, 2, 62, 46),
)


# Harmonic centres: A (farewell) -> E/A suspension (recognition) -> alternating
# D and C open fields (ritual) -> D/A open fifth (grave). All remain inside the
# confirmed C-D-E-G-A collection; tension comes from gravity and pacing.
HARMONIES = (
    (0, 4, (45, 52, 55), 30), (4, 4, (38, 45, 52), 29),
    (8, 4, (36, 43, 50), 29), (12, 4, (45, 52, 55), 28),
    (16, 4, (38, 45, 52), 28), (20, 4, (45, 52), 27),
    (24, 4, (40, 45, 50), 29), (28, 4, (45, 52, 55), 30),
    (32, 4, (40, 45, 50), 31), (36, 4, (36, 43, 50), 30),
    (40, 4, (38, 45, 52), 29), (44, 4, (45, 52), 27),
    # Ritual alternation begins without adding percussion.
    (48, 2, (38, 45), 27), (50, 2, (36, 43), 26),
    (52, 2, (38, 45), 26), (54, 2, (36, 43), 25),
    (56, 2, (38, 45), 25), (58, 2, (36, 43), 24),
    (60, 2, (38, 45), 24), (62, 2, (36, 43), 23),
    (64, 4, (38, 45), 23), (68, 4, (36, 43), 22),
    (72, 4, (45, 52), 22), (76, 4, (38, 45), 21),
    (80, 4, (36, 43, 50), 21), (84, 4, (45, 52), 20),
    (88, 6, (38, 45), 19),
)
ACCOMPANIMENT = tuple(
    note(start, duration + 0.15, pitch, velocity)
    for start, duration, pitches, velocity in HARMONIES
    for pitch in pitches
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tempo = round(60_000_000 / BPM)
    meta = track([
        (0, 1, b"\xFF\x51\x03" + tempo.to_bytes(3, "big")),
        (0, 2, b"\xFF\x58\x04\x04\x02\x18\x08"),
    ], "Tempo")
    tracks = [
        meta,
        note_track(ZHU, "Zhu Ying-tai", 0),
        note_track(LIANG, "Liang Shan-bo", 1),
        note_track(ACCOMPANIMENT, "Harmonic thread", 2),
    ]
    midi_path = OUT / "farewell_to_butterflies_v04.mid"
    midi_path.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TPQ) + b"".join(tracks))
    score_path = OUT / "farewell_to_butterflies_v04.json"
    score_path.write_text(json.dumps({
        "bpm": BPM,
        "totalBeats": 98,
        "notes": [
            *({**item.__dict__, "voice": "zhu"} for item in ZHU),
            *({**item.__dict__, "voice": "liang"} for item in LIANG),
            *({**item.__dict__, "voice": "accompaniment"} for item in ACCOMPANIMENT),
        ],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(midi_path)
    print(score_path)


if __name__ == "__main__":
    main()
