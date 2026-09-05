#!/usr/bin/env python3
"""Generate the three confirmed low-cost Liang Zhu MIDI/WAV sketches.

The WAV files use deliberately plain synthesized timbres. They are for checking
motif, timing, counterpoint, and silence—not for judging final instrumentation.
"""

from __future__ import annotations

import math
import random
import struct
import wave
from dataclasses import dataclass
from pathlib import Path


SAMPLE_RATE = 44_100
TICKS_PER_BEAT = 480
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "audio" / "theme_sketches_v01"


@dataclass(frozen=True)
class Note:
    start: float
    duration: float
    pitch: int
    velocity: int
    voice: str


@dataclass(frozen=True)
class Sketch:
    slug: str
    title: str
    bpm: int
    beats: float
    notes: tuple[Note, ...]


VOICE = {
    "zhu": {"channel": 0, "program": 73, "pan": 78},
    "liang": {"channel": 1, "program": 42, "pan": 50},
    "space": {"channel": 2, "program": 48, "pan": 64},
    "pulse": {"channel": 9, "program": 0, "pan": 64},
}


def n(start: float, duration: float, pitch: int, velocity: int, voice: str) -> Note:
    return Note(start, duration, pitch, velocity, voice)


SKETCHES = (
    Sketch(
        slug="a_encounter",
        title="A 相遇：自然接续",
        bpm=68,
        beats=20,
        notes=(
            n(0, 20, 50, 24, "space"), n(0, 20, 57, 18, "space"),
            # Zhu: upbeat, two rises, held high point, no return to D.
            n(0.5, 0.5, 64, 67, "zhu"), n(1.0, 0.5, 67, 70, "zhu"),
            n(1.5, 1.5, 69, 73, "zhu"), n(3.0, 0.5, 72, 67, "zhu"),
            n(3.5, 0.75, 69, 64, "zhu"), n(4.5, 0.5, 67, 61, "zhu"),
            n(5.0, 1.0, 64, 57, "zhu"),
            # Liang accepts Zhu's A and completes a grounded descending phrase.
            n(6.0, 1.0, 57, 65, "liang"), n(7.0, 1.0, 55, 64, "liang"),
            n(8.0, 2.0, 53, 62, "liang"), n(10.0, 1.0, 52, 59, "liang"),
            n(11.0, 3.0, 50, 57, "liang"),
            # First small overlap: they remain independently singable.
            n(12.5, 0.5, 64, 60, "zhu"), n(13.0, 0.5, 67, 62, "zhu"),
            n(13.5, 1.5, 69, 65, "zhu"), n(15.0, 0.5, 72, 60, "zhu"),
            n(15.5, 1.0, 69, 57, "zhu"), n(14.0, 1.0, 57, 58, "liang"),
            n(15.0, 1.0, 55, 57, "liang"), n(16.0, 2.0, 53, 55, "liang"),
            n(18.0, 1.0, 52, 52, "liang"), n(19.0, 1.0, 50, 50, "liang"),
        ),
    ),
    Sketch(
        slug="b_recognition",
        title="B 相认：追上时已无法相合",
        bpm=68,
        beats=24,
        notes=(
            n(0, 8, 50, 20, "space"), n(0, 8, 57, 16, "space"),
            n(8, 8, 52, 21, "space"), n(8, 8, 58, 17, "space"),
            n(16, 5, 52, 23, "space"), n(16, 5, 58, 20, "space"),
            # Zhu's original breath.
            n(0.5, 0.5, 64, 67, "zhu"), n(1.0, 0.5, 67, 70, "zhu"),
            n(1.5, 1.5, 69, 73, "zhu"), n(3.0, 0.5, 72, 66, "zhu"),
            n(3.5, 0.75, 69, 63, "zhu"),
            # Liang begins to borrow her rising direction, first two beats late.
            n(5.5, 0.5, 59, 61, "liang"), n(6.0, 0.5, 62, 64, "liang"),
            n(6.5, 1.5, 64, 67, "liang"), n(8.0, 0.5, 67, 61, "liang"),
            n(8.5, 0.75, 64, 58, "liang"),
            # One-beat chase.
            n(9.5, 0.5, 64, 69, "zhu"), n(10.0, 0.5, 67, 72, "zhu"),
            n(10.5, 1.0, 69, 75, "zhu"), n(11.5, 0.5, 72, 69, "zhu"),
            n(12.0, 0.5, 59, 66, "liang"), n(12.5, 0.5, 62, 69, "liang"),
            n(13.0, 1.0, 64, 72, "liang"), n(14.0, 0.5, 70, 70, "liang"),
            # Half-beat chase; E against B-flat exposes the boundary.
            n(15.0, 0.4, 64, 72, "zhu"), n(15.5, 0.4, 67, 75, "zhu"),
            n(16.0, 0.8, 69, 78, "zhu"), n(16.8, 0.4, 72, 73, "zhu"),
            n(17.25, 0.4, 59, 70, "liang"), n(17.75, 0.4, 62, 73, "liang"),
            n(18.25, 0.8, 64, 76, "liang"), n(19.05, 0.45, 70, 74, "liang"),
            n(19.55, 0.4, 64, 73, "zhu"), n(20.0, 0.4, 67, 75, "zhu"),
            n(20.45, 0.55, 69, 78, "zhu"), n(20.0, 0.45, 59, 72, "liang"),
            n(20.45, 0.55, 64, 75, "liang"),
            # Everything stops before the nominal phrase can resolve.
        ),
    ),
    Sketch(
        slug="c_wedding_funeral",
        title="C 婚丧：人停而礼不停",
        bpm=60,
        beats=20,
        notes=(
            n(0, 12, 50, 18, "space"), n(0, 12, 57, 14, "space"),
            # Even ceremonial pulse; it survives both character voices.
            *(n(float(beat), 0.16, 43, 42 if beat < 12 else 38, "pulse") for beat in range(20)),
            # Zhu: three increasingly incomplete breaths.
            n(0.5, 0.35, 64, 62, "zhu"), n(0.9, 0.35, 67, 64, "zhu"),
            n(1.3, 0.8, 69, 66, "zhu"),
            n(5.0, 0.3, 64, 57, "zhu"), n(5.35, 0.3, 67, 59, "zhu"),
            n(5.7, 0.55, 69, 60, "zhu"),
            n(9.5, 0.25, 64, 49, "zhu"), n(9.8, 0.35, 67, 50, "zhu"),
            # Liang: only the opening of his descent, fading out by beat 12.
            n(2.0, 0.8, 57, 59, "liang"), n(2.8, 0.8, 55, 56, "liang"),
            n(6.0, 0.65, 57, 52, "liang"), n(6.7, 0.65, 55, 49, "liang"),
            n(10.0, 0.45, 57, 43, "liang"), n(10.5, 0.45, 55, 39, "liang"),
        ),
    ),
)


def variable_length(value: int) -> bytes:
    buffer = value & 0x7F
    out = bytearray()
    while value >> 7:
        value >>= 7
        buffer <<= 8
        buffer |= (value & 0x7F) | 0x80
    while True:
        out.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            break
    return bytes(out)


def midi_track(events: list[tuple[int, int, bytes]]) -> bytes:
    payload = bytearray()
    last_tick = 0
    for tick, order, event in sorted(events, key=lambda item: (item[0], item[1])):
        payload.extend(variable_length(tick - last_tick))
        payload.extend(event)
        last_tick = tick
    payload.extend(b"\x00\xFF\x2F\x00")
    return b"MTrk" + struct.pack(">I", len(payload)) + payload


def write_midi(sketch: Sketch, path: Path) -> None:
    tempo = round(60_000_000 / sketch.bpm)
    meta = [
        (0, 0, b"\xFF\x03" + bytes([len(sketch.title.encode())]) + sketch.title.encode()),
        (0, 1, b"\xFF\x51\x03" + tempo.to_bytes(3, "big")),
        (0, 2, b"\xFF\x58\x04\x04\x02\x18\x08"),
    ]
    tracks = [midi_track(meta)]
    for voice_name, spec in VOICE.items():
        channel = spec["channel"]
        events = [
            (0, 0, bytes([0xC0 | channel, spec["program"]])),
            (0, 1, bytes([0xB0 | channel, 10, spec["pan"]])),
        ]
        for note in (item for item in sketch.notes if item.voice == voice_name):
            start = round(note.start * TICKS_PER_BEAT)
            end = round((note.start + note.duration) * TICKS_PER_BEAT)
            midi_pitch = 76 if voice_name == "pulse" else note.pitch
            events.append((start, 2, bytes([0x90 | channel, midi_pitch, note.velocity])))
            events.append((end, 1, bytes([0x80 | channel, midi_pitch, 0])))
        tracks.append(midi_track(events))
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TICKS_PER_BEAT)
    path.write_bytes(header + b"".join(tracks))


def oscillator(phase: float, voice: str) -> float:
    sine = math.sin(phase)
    if voice == "zhu":
        return 0.82 * sine + 0.18 * math.sin(2 * phase)
    if voice == "liang":
        return 0.76 * sine + 0.16 * math.sin(0.5 * phase) + 0.08 * math.sin(3 * phase)
    return sine


def envelope(t: float, duration: float, voice: str) -> float:
    if voice == "pulse":
        return math.exp(-30 * t)
    attack = 0.035 if voice != "space" else 0.25
    release = 0.18 if voice != "space" else 0.45
    a = min(1.0, t / attack)
    r = min(1.0, max(0.0, duration - t) / release)
    return a * r


def write_wav(sketch: Sketch, path: Path) -> None:
    seconds_per_beat = 60.0 / sketch.bpm
    total_seconds = sketch.beats * seconds_per_beat + 0.8
    sample_count = math.ceil(total_seconds * SAMPLE_RATE)
    left = [0.0] * sample_count
    right = [0.0] * sample_count
    rng = random.Random(20260904)
    gains = {"zhu": 0.18, "liang": 0.20, "space": 0.055, "pulse": 0.11}
    pans = {"zhu": 0.62, "liang": 0.38, "space": 0.5, "pulse": 0.5}
    for note in sketch.notes:
        start_seconds = note.start * seconds_per_beat
        duration_seconds = note.duration * seconds_per_beat
        start_sample = round(start_seconds * SAMPLE_RATE)
        end_sample = min(sample_count, round((start_seconds + duration_seconds) * SAMPLE_RATE))
        frequency = 440.0 * (2 ** ((note.pitch - 69) / 12))
        gain = gains[note.voice] * (note.velocity / 80)
        pan = pans[note.voice]
        for index in range(start_sample, end_sample):
            t = (index - start_sample) / SAMPLE_RATE
            env = envelope(t, duration_seconds, note.voice)
            if note.voice == "pulse":
                value = (0.6 * math.sin(2 * math.pi * frequency * t) + 0.4 * (rng.random() * 2 - 1))
            else:
                value = oscillator(2 * math.pi * frequency * t, note.voice)
            value *= gain * env
            left[index] += value * math.sqrt(1 - pan)
            right[index] += value * math.sqrt(pan)
    peak = max(max(abs(x) for x in left), max(abs(x) for x in right), 1e-9)
    scale = 0.88 / peak
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for l_sample, r_sample in zip(left, right):
            frames.extend(struct.pack("<hh", int(l_sample * scale * 32767), int(r_sample * scale * 32767)))
        wav.writeframes(frames)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for sketch in SKETCHES:
        write_midi(sketch, OUTPUT_DIR / f"{sketch.slug}.mid")
        write_wav(sketch, OUTPUT_DIR / f"{sketch.slug}.wav")
        print(f"generated {sketch.slug}: {sketch.beats * 60 / sketch.bpm:.1f}s")


if __name__ == "__main__":
    main()
