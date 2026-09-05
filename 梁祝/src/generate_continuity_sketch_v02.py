#!/usr/bin/env python3
"""Generate the v02 piano-reduction continuity sketch: encounter into school days."""

from __future__ import annotations

import struct
import json
import math
from dataclasses import dataclass
from pathlib import Path


TPQ = 480
BPM = 72
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audio" / "continuity_sketch_v02"


@dataclass(frozen=True)
class Note:
    start: float
    duration: float
    pitch: int
    velocity: int


def note(start: float, duration: float, pitch: int, velocity: int) -> Note:
    return Note(start, duration, pitch, velocity)


# Zhu: a complete arch. It begins away from the tonal centre, reaches one clear
# high point, and returns gently rather than remaining artificially unresolved.
ZHU = (
    note(2, 1, 64, 66), note(3, 1, 67, 69), note(4, 2, 69, 73),
    note(6, 1, 67, 68), note(7, 1, 64, 64), note(8, 2, 62, 62),
    note(10, 1, 64, 66), note(11, 1, 67, 71), note(12, 1, 69, 75),
    note(13, 2, 72, 80), note(15, 1, 69, 72), note(16, 2, 67, 69),
    note(18, 1, 64, 64), note(19, 3, 62, 61),
    # The same identity returns without being fragmented; the changed bass is
    # what turns encounter into the warmer school-days section.
    note(34, 1, 64, 64), note(35, 1, 67, 68), note(36, 2, 69, 72),
    note(38, 1, 67, 67), note(39, 1, 64, 63), note(40, 2, 62, 61),
    note(42, 1, 64, 65), note(43, 1, 67, 69), note(44, 2, 69, 74),
    note(46, 2, 72, 78), note(48, 2, 69, 71), note(50, 2, 67, 67),
    note(52, 2, 64, 63), note(54, 2, 62, 60),
    note(56, 1, 64, 62), note(57, 1, 67, 65), note(58, 2, 69, 68),
    note(60, 1, 67, 63), note(61, 1, 64, 60), note(62, 2, 62, 57),
)


# Liang: a grounded, mostly stepwise phrase. It overlaps Zhu's arrival by two
# beats so that the hand-off feels like recognition, not a cut to a new cue.
LIANG = (
    note(20, 2, 57, 64), note(22, 1, 55, 62), note(23, 1, 52, 60),
    note(24, 2, 50, 59), note(26, 1, 52, 61), note(27, 1, 55, 64),
    note(28, 2, 57, 68), note(30, 2, 55, 64), note(32, 1, 52, 60),
    note(33, 3, 50, 58), note(36, 1, 52, 60), note(37, 1, 55, 63),
    note(38, 2, 57, 67), note(40, 4, 62, 70),
    # In the shared section he keeps his own descending direction underneath.
    note(44, 2, 57, 59), note(46, 2, 55, 58), note(48, 2, 52, 56),
    note(50, 2, 50, 55), note(52, 2, 52, 57), note(54, 2, 55, 59),
    note(56, 2, 57, 61), note(58, 2, 55, 59), note(60, 2, 52, 56),
    note(62, 2, 50, 54),
)


# Slow harmonic fields provide continuity. The pitch collection stays C-D-E-G-A;
# only the perceived centre shifts gradually from D toward G.
HARMONIES = (
    (0, (38, 45, 52)), (4, (36, 43, 50)), (8, (38, 45, 52)),
    (12, (43, 50, 57)), (16, (36, 43, 50)), (20, (38, 45, 52)),
    (24, (43, 50, 57)), (28, (36, 43, 50)), (32, (43, 50, 57)),
    (36, (45, 52, 55)), (40, (36, 43, 50)), (44, (43, 50, 57)),
    (48, (45, 52, 55)), (52, (36, 43, 50)), (56, (43, 50, 57)),
    (60, (38, 45, 52)),
)
ACCOMPANIMENT = tuple(
    note(start, 4.15, pitch, 34 if pitch < 48 else 30)
    for start, pitches in HARMONIES
    for pitch in pitches
)


def vlq(value: int) -> bytes:
    buffer = value & 0x7F
    out = bytearray()
    while value >> 7:
        value >>= 7
        buffer = (buffer << 8) | ((value & 0x7F) | 0x80)
    while True:
        out.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            return bytes(out)


def track(events: list[tuple[int, int, bytes]], name: str) -> bytes:
    name_bytes = name.encode("utf-8")
    events.append((0, 0, b"\xFF\x03" + vlq(len(name_bytes)) + name_bytes))
    payload = bytearray()
    previous = 0
    for tick, order, event in sorted(events, key=lambda item: (item[0], item[1])):
        payload.extend(vlq(tick - previous))
        payload.extend(event)
        previous = tick
    payload.extend(b"\x00\xFF\x2F\x00")
    return b"MTrk" + struct.pack(">I", len(payload)) + payload


def note_track(notes: tuple[Note, ...], name: str, channel: int) -> bytes:
    pedal_end = math.ceil(max(item.start + item.duration for item in notes)) + 1
    events: list[tuple[int, int, bytes]] = [
        (0, 1, bytes([0xC0 | channel, 0])),
        (0, 2, bytes([0xB0 | channel, 64, 96])),  # sustain pedal
        (pedal_end * TPQ, 0, bytes([0xB0 | channel, 64, 0])),
    ]
    for item in notes:
        start = round(item.start * TPQ)
        end = round((item.start + item.duration * 0.98) * TPQ)
        events.append((start, 4, bytes([0x90 | channel, item.pitch, item.velocity])))
        events.append((end, 3, bytes([0x80 | channel, item.pitch, 0])))
    return track(events, name)


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
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TPQ)
    path = OUT / "encounter_to_school_v02.mid"
    path.write_bytes(header + b"".join(tracks))
    print(path)
    score_path = OUT / "encounter_to_school_v02.json"
    score_path.write_text(json.dumps({
        "bpm": BPM,
        "totalBeats": 64,
        "notes": [
            *({**item.__dict__, "voice": "zhu"} for item in ZHU),
            *({**item.__dict__, "voice": "liang"} for item in LIANG),
            *({**item.__dict__, "voice": "accompaniment"} for item in ACCOMPANIMENT),
        ],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(score_path)


if __name__ == "__main__":
    main()
