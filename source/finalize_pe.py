#!/usr/bin/env python3
"""Add Worker Workwear VERSIONINFO metadata and a valid PE checksum."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

VERSION = (1, 1, 0, 0)
LANG_ID = 0x0409
CODEPAGE = 1200


def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) & ~(boundary - 1)


def utf16z(text: str) -> bytes:
    return text.encode("utf-16le") + b"\x00\x00"


def vi_block(
    key: str,
    *,
    value: bytes = b"",
    value_is_text: bool = False,
    children: list[bytes] | None = None,
    block_type: int = 0,
    value_length: int | None = None,
) -> bytes:
    children = children or []
    body = bytearray(b"\x00" * 6)
    body += utf16z(key)
    while len(body) % 4:
        body.append(0)
    if value:
        body += value
        while len(body) % 4:
            body.append(0)
    for child in children:
        body += child
    if value_length is None:
        value_length = len(value) // 2 if value_is_text else len(value)
    struct.pack_into("<HHH", body, 0, len(body), value_length, block_type)
    return bytes(body)


def make_version_info() -> bytes:
    a, b, c, d = VERSION
    fixed = struct.pack(
        "<13I",
        0xFEEF04BD,
        0x00010000,
        (a << 16) | b,
        (c << 16) | d,
        (a << 16) | b,
        (c << 16) | d,
        0x0000003F,
        0,
        0x00040004,
        0x00000002,
        0,
        0,
        0,
    )
    strings = {
        "CompanyName": "Ultimate-Universe",
        "FileDescription": "Worker Workwear - TesmioLoader Plugin",
        "FileVersion": "1.1.0.0",
        "InternalName": "worker_workwear",
        "OriginalFilename": "worker_workwear.dll",
        "ProductName": "Worker Workwear",
        "ProductVersion": "1.1.0",
    }
    entries = [
        vi_block(key, value=utf16z(text), value_is_text=True, block_type=1)
        for key, text in strings.items()
    ]
    string_table = vi_block(
        "040904B0", children=entries, block_type=1, value_length=0
    )
    string_info = vi_block(
        "StringFileInfo", children=[string_table], block_type=1, value_length=0
    )
    translation = struct.pack("<HH", LANG_ID, CODEPAGE)
    var = vi_block(
        "Translation", value=translation, block_type=0,
        value_length=len(translation)
    )
    var_info = vi_block(
        "VarFileInfo", children=[var], block_type=1, value_length=0
    )
    return vi_block(
        "VS_VERSION_INFO", value=fixed, block_type=0,
        value_length=len(fixed), children=[string_info, var_info]
    )


def make_resource_section(section_rva: int) -> bytes:
    version = make_version_info()
    root_off, type_off, name_off, data_off = 0, 24, 48, 72
    version_off = align(88, 4)
    out = bytearray(version_off)

    def directory(offset: int, entry_id: int, child: int, is_dir: bool) -> None:
        struct.pack_into("<IIHHHH", out, offset, 0, 0, 0, 0, 0, 1)
        struct.pack_into(
            "<II", out, offset + 16, entry_id,
            child | (0x80000000 if is_dir else 0)
        )

    directory(root_off, 16, type_off, True)
    directory(type_off, 1, name_off, True)
    directory(name_off, LANG_ID, data_off, False)
    struct.pack_into(
        "<IIII", out, data_off, section_rva + version_off,
        len(version), CODEPAGE, 0
    )
    out += version
    return bytes(out)


def pe_checksum(data: bytes, checksum_offset: int) -> int:
    buf = bytearray(data)
    buf[checksum_offset:checksum_offset + 4] = b"\x00\x00\x00\x00"
    checksum = 0
    padded = bytes(buf) + b"\x00" * ((4 - len(buf) % 4) % 4)
    for offset in range(0, len(padded), 4):
        checksum = (checksum & 0xFFFFFFFF) + struct.unpack_from(
            "<I", padded, offset
        )[0] + (checksum >> 32)
        if checksum > 0xFFFFFFFF:
            checksum = (checksum & 0xFFFFFFFF) + (checksum >> 32)
    checksum = (checksum & 0xFFFF) + (checksum >> 16)
    checksum += checksum >> 16
    return ((checksum & 0xFFFF) + len(buf)) & 0xFFFFFFFF


def finalize(path: Path) -> None:
    data = bytearray(path.read_bytes())
    if data[:2] != b"MZ":
        raise SystemExit("Not a PE file")
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_off:pe_off + 4] != b"PE\x00\x00":
        raise SystemExit("Invalid PE signature")

    coff_off = pe_off + 4
    machine, section_count, _, _, _, opt_size, _ = struct.unpack_from(
        "<HHIIIHH", data, coff_off
    )
    if machine != 0x8664:
        raise SystemExit("Expected x86-64 PE")
    opt_off = coff_off + 20
    if struct.unpack_from("<H", data, opt_off)[0] != 0x20B:
        raise SystemExit("Expected PE32+")

    section_alignment = struct.unpack_from("<I", data, opt_off + 0x20)[0]
    file_alignment = struct.unpack_from("<I", data, opt_off + 0x24)[0]
    size_headers = struct.unpack_from("<I", data, opt_off + 0x3C)[0]
    section_table = opt_off + opt_size
    sections = []
    first_raw = len(data)
    for index in range(section_count):
        off = section_table + index * 40
        name = bytes(data[off:off + 8]).rstrip(b"\x00")
        virtual_size, rva, raw_size, raw_ptr = struct.unpack_from(
            "<IIII", data, off + 8
        )
        sections.append((name, virtual_size, rva, raw_size, raw_ptr))
        if raw_ptr:
            first_raw = min(first_raw, raw_ptr)

    if any(name == b".rsrc" for name, *_ in sections):
        raise SystemExit("DLL already contains .rsrc")
    new_header = section_table + section_count * 40
    if new_header + 40 > min(size_headers, first_raw):
        raise SystemExit("No room for another PE section header")

    last = max(sections, key=lambda item: item[2])
    new_rva = align(
        last[2] + max(last[1], last[3]), section_alignment
    )
    resource = make_resource_section(new_rva)
    raw_size = align(len(resource), file_alignment)
    raw_ptr = align(len(data), file_alignment)
    if len(data) < raw_ptr:
        data += b"\x00" * (raw_ptr - len(data))
    data += resource
    data += b"\x00" * (raw_size - len(resource))

    header = struct.pack(
        "<8sIIIIIIHHI", b".rsrc\x00\x00\x00", len(resource), new_rva,
        raw_size, raw_ptr, 0, 0, 0, 0, 0x40000040
    )
    data[new_header:new_header + 40] = header
    struct.pack_into("<H", data, coff_off + 2, section_count + 1)
    size_init = struct.unpack_from("<I", data, opt_off + 0x08)[0]
    struct.pack_into("<I", data, opt_off + 0x08, size_init + raw_size)
    struct.pack_into(
        "<I", data, opt_off + 0x38,
        align(new_rva + len(resource), section_alignment)
    )
    struct.pack_into(
        "<II", data, opt_off + 0x70 + 2 * 8, new_rva, len(resource)
    )
    # Replace GNU ld's legacy defaults with a conventional x64 Windows floor.
    struct.pack_into("<HH", data, opt_off + 0x28, 6, 0)
    struct.pack_into("<HH", data, opt_off + 0x30, 6, 0)
    checksum_off = opt_off + 0x40
    struct.pack_into("<I", data, checksum_off, 0)
    checksum = pe_checksum(bytes(data), checksum_off)
    struct.pack_into("<I", data, checksum_off, checksum)
    path.write_bytes(data)
    print(
        f"Finalized {path.name}: resource RVA 0x{new_rva:X}, "
        f"checksum 0x{checksum:08X}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dll", nargs="?", default="worker_workwear.dll")
    args = parser.parse_args()
    finalize(Path(args.dll))


if __name__ == "__main__":
    main()
