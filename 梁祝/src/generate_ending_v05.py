#!/usr/bin/env python3
"""Generate the short v05 ending test with Liang's line returning to rest."""

from __future__ import annotations

import json
import struct
from pathlib import Path

from generate_continuity_sketch_v02 import TPQ, note, note_track, track
from generate_late_arc_v04 import ACCOMPANIMENT as V04_ACCOMPANIMENT
from generate_late_arc_v04 import ZHU as V04_ZHU


BPM = 72
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audio" / "ending_sketch_v05"
SOURCE_BEAT = 72


def shifted(notes):
    return tuple(
        note(item.start - SOURCE_BEAT, item.duration, item.pitch, item.velocity)
        for item in notes
        if item.start >= SOURCE_BEAT
    )


ZHU = shifted(V04_ZHU)
ACCOMPANIMENT = shifted(V04_ACCOMPANIMENT)

# The old line rose continuously D-E-G-A-C-D. The revision crests on A, turns
# back through G and E, then settles on D in the original low register.
LIANG = (
    note(10, 2, 50, 42), note(12, 2, 52, 45), note(14, 2, 55, 48),
    note(16, 2, 57, 50), note(18, 1, 55, 49), note(19, 1, 52, 47),
    note(20, 2, 50, 44),
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
        note_track(LIANG, "Liang Shan-bo memory", 1),
        note_track(ACCOMPANIMENT, "Harmonic thread", 2),
    ]
    midi_path = OUT / "ending_return_to_rest_v05.mid"
    midi_path.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TPQ) + b"".join(tracks))
    score_path = OUT / "ending_return_to_rest_v05.json"
    score_path.write_text(json.dumps({
        "bpm": BPM,
        "totalBeats": 26,
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
