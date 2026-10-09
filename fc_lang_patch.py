#!/usr/bin/env python3
"""
FC 27 (PPSA34015) dil paketi kalicilik yamasi / language pack persistence patch.

Patch/layout.toc icindeki "launchOptional" paketleri "alwaysInstalled" yapar.
Flips every "launchOptional" install chunk in Patch/layout.toc to "alwaysInstalled".

Kullanim / Usage:
    python fc_lang_patch.py "E:/homebrew/PPSA34015-app/Patch/layout.toc"
    python fc_lang_patch.py layout.toc --dry-run
    python fc_lang_patch.py layout.toc --only tur_tr,tr     (sadece Turkce / Turkish only)
"""
import argparse
import os
import re
import shutil
import sys

ALWAYS = b"\x06alwaysInstalled\x00"   # 0x06 = bool tipi / bool type
LAUNCH = b"\x06launchOptional\x00"
NAME = re.compile(rb"\x07name\x00.superbundlelayout/")


def entries(data):
    starts = [m.start() for m in NAME.finditer(data)]
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(data)
        name_start = s + 7  # \x07 + "name\x00" + uzunluk baytı / length byte
        name = data[name_start:data.index(b"\x00", name_start)].decode("latin1")
        a = data.find(ALWAYS, s, e)
        l = data.find(LAUNCH, s, e)
        if a >= 0 and l >= 0:
            yield name, a + len(ALWAYS), l + len(LAUNCH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("toc")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="virgulle ayrilmis ad parcalari / comma-separated name fragments")
    args = ap.parse_args()

    data = bytearray(open(args.toc, "rb").read())
    if data[:4] != b"\x00\xd1\xce\x01":
        sys.exit("Beklenmeyen baslik / unexpected header: " + data[:4].hex())

    only = [x.strip() for x in args.only.split(",")] if args.only else None
    changed = []
    for name, a_off, l_off in entries(bytes(data)):
        if data[l_off] != 1 or data[a_off] != 0:
            continue
        if only and not any(name.endswith("_" + o) or name.endswith("/" + o) for o in only):
            continue
        data[a_off], data[l_off] = 1, 0
        changed.append((name, a_off, l_off))

    for name, a_off, l_off in changed:
        print(f"{name:45s} alwaysInstalled@0x{a_off:05X} 0->1  launchOptional@0x{l_off:05X} 1->0")
    print(f"{len(changed)} paket / packages, {len(changed) * 2} bayt / bytes")

    if args.dry_run or not changed:
        return
    orig = args.toc + ".orig"
    if not os.path.exists(orig):
        shutil.copy2(args.toc, orig)
        print("Yedek / backup:", orig)
    open(args.toc, "wb").write(data)
    print("Yazildi / written:", args.toc)


if __name__ == "__main__":
    main()
