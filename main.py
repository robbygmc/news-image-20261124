#!/usr/bin/env python3
"""Copy the bundled newspaper image to the output directory.

Reads entry.png from the directory holding this script and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), verifying the PNG header,
its 1024x1024 size, the 1 MiB limit, and that the copy is byte-identical.
Standard library only; no network.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1048576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not out_dir:
        fail("MAKEFUN_OUTPUT_DIR is set but empty")
    if os.path.isfile(out_dir):
        fail(f"MAKEFUN_OUTPUT_DIR {out_dir!r} is a file, not a directory")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        fail(f"cannot create output directory {out_dir!r}: {exc}")
    dest = os.path.join(out_dir, "entry.png")

    with open(source, "rb") as fh:
        data = fh.read()

    if len(data) > MAX_BYTES:
        fail(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    if data[:8] != PNG_MAGIC:
        fail("entry.png does not start with the PNG magic bytes")
    if len(data) < 24:
        fail("entry.png is too short to hold a PNG header")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail(f"entry.png is {width}x{height}, expected 1024x1024")

    with open(dest, "wb") as fh:
        fh.write(data)

    with open(dest, "rb") as fh:
        copied = fh.read()
    if hashlib.sha256(copied).hexdigest() != hashlib.sha256(data).hexdigest():
        fail("copied entry.png does not match the source bytes")

    print(f"wrote {dest} ({len(data)} bytes, sha256 "
          f"{hashlib.sha256(data).hexdigest()})")


if __name__ == "__main__":
    main()
