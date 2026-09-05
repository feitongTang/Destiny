#!/usr/bin/env python3
"""Generate the v03 continuity sketch: warm school days into farewell."""

from __future__ import annotations

import json
import struct
from pathlib import Path

from generate_continuity_sketch_v02 import Note, TPQ, note, note_track, track


BPM = 72
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audio" / "transition_sketch_v03"


ZHU = (
    # Warm school-days statement: continuous arch, already recognisable from v02.
    note(0.5, 0.5, 64, 65), note(1, 1, 67, 69), note(2, 2, 69, 73),
    note(4, 1, 67, 68), note(5, 1, 64, 64), note(6, 2, 62, 61),
    note(8, 1, 64, 65), note(9, 1, 67, 70), note(10, 1, 69, 74),
    note(11, 2, 72, 79), note(13, 1, 69, 72), note(14, 2, 67, 68),
    note(16, 1, 64, 64), note(17, 1, 67, 68), note(18, 2, 69, 72),
    note(20, 1, 67, 67), note(21, 1, 64, 63), note(22, 2, 62, 60),
    note(24, 1, 67, 67), note(25, 1, 69, 72), note(26, 2, 72, 77),
    note(28, 2, 69, 70), note(30, 2, 67, 65),
    # Transition: note lengths broaden. The line does not break; it begins to wait.
    note(32, 1, 64, 62), note(33, 1, 67, 66), note(34, 3, 69, 70),
    note(37, 1, 67, 64), note(38, 2, 64, 60),
    # Farewell: a complete sentence with more space inside it, not clipped notes.
    note(40, 1, 64, 61), note(41, 1, 67, 65), note(42, 3, 69, 70),
    note(45, 1, 67, 63), note(46, 2, 64, 59),
    note(48, 1, 64, 60), note(49, 1, 67, 65), note(50, 1, 69, 69),
    note(51, 3, 72, 75), note(54, 2, 69, 68), note(56, 2, 67, 64),
    note(58, 2, 64, 59), note(60, 4, 62, 55),
)


LIANG = (
    # Liang enters inside Zhu's phrase and maintains his calmer downward gravity.
    note(4, 2, 57, 61), note(6, 1, 55, 59), note(7, 1, 52, 57),
    note(8, 2, 50, 56), note(10, 1, 52, 58), note(11, 1, 55, 61),
    note(12, 2, 57, 65), note(14, 2, 55, 61), note(16, 1, 52, 58),
    note(17, 3, 50, 56), note(20, 1, 52, 58), note(21, 1, 55, 61),
    note(22, 2, 57, 65), note(24, 2, 55, 61), note(26, 2, 52, 58),
    note(28, 4, 50, 55),
    # He continues to answer in complete long lines as the colour cools.
    note(32, 4, 50, 54), note(36, 2, 52, 56), note(38, 2, 55, 59),
    note(40, 2, 57, 62), note(42, 2, 55, 60), note(44, 2, 52, 57),
    note(46, 4, 50, 55), note(50, 2, 52, 57), note(52, 2, 55, 60),
    note(54, 2, 57, 63), note(56, 2, 55, 60), note(58, 2, 52, 57),
    note(60, 4, 50, 54),
)


# The first half is G-centred and warm. At beat 28, A becomes the pivot; after
# beat 40 the same five notes settle toward D. Fewer chord tones create distance.
HARMONIES = (
    (0, (43, 50, 57)), (4, (36, 43, 50)), (8, (43, 50, 57)),
    (12, (38, 45, 52)), (16, (43, 50, 57)), (20, (36, 43, 50)),
    (24, (43, 50, 57)), (28, (45, 52, 55)), (32, (45, 52)),
    (36, (45, 50)), (40, (38, 45, 52)), (44, (36, 43, 50)),
    (48, (45, 52, 55)), (52, (38, 45)), (56, (36, 43, 50)),
    (60, (38, 45, 52)),
)
ACCOMPANIMENT = tuple(
    note(start, 4.15, pitch, 33 if start < 32 else 28)
    for start, pitches in HARMONIES
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
    midi_path = OUT / "school_to_farewell_v03.mid"
    midi_path.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TPQ) + b"".join(tracks))
    score_path = OUT / "school_to_farewell_v03.json"
    score_path.write_text(json.dumps({
        "bpm": BPM,
        "totalBeats": 64,
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
