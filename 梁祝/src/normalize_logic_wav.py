#!/usr/bin/env python3
"""Convert a Logic Float32 WAV render to normalized 16-bit PCM WAV."""

from __future__ import annotations

import argparse
import struct
import wave
from pathlib import Path


def read_float_wav(path: Path) -> tuple[int, int, tuple[float, ...]]:
    raw = path.read_bytes()
    position = 12
    fmt = None
    audio = None
    while position + 8 <= len(raw):
        chunk_id = raw[position:position + 4]
        size = struct.unpack_from("<I", raw, position + 4)[0]
        payload = raw[position + 8:position + 8 + size]
        if chunk_id == b"fmt ":
            fmt = payload
        elif chunk_id == b"data":
            audio = payload
        position += 8 + size + (size & 1)
    if fmt is None or audio is None:
        raise ValueError("missing fmt or data chunk")
    format_code, channels, sample_rate = struct.unpack_from("<HHI", fmt, 0)
    if format_code == 0xFFFE:
        format_code = struct.unpack_from("<H", fmt, 24)[0]
    if format_code != 3:
        raise ValueError(f"expected Float32 WAV, got format {format_code}")
    return channels, sample_rate, struct.unpack("<" + "f" * (len(audio) // 4), audio)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--peak", type=float, default=0.82)
    args = parser.parse_args()
    channels, sample_rate, samples = read_float_wav(args.source)
    source_peak = max(abs(value) for value in samples)
    if source_peak == 0:
        raise ValueError("source render is silent")
    scale = args.peak / source_peak
    pcm = bytearray()
    for value in samples:
        normalized = max(-1.0, min(1.0, value * scale))
        pcm.extend(struct.pack("<h", round(normalized * 32767)))
    with wave.open(str(args.destination), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm)
    print(args.destination)


if __name__ == "__main__":
    main()
