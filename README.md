# FC 27 PS5 Backport – Language Pack / Commentary Download Resets Fix

**Fix for EA SPORTS FC 27 (PPSA34015) on jailbroken PS5 backports: Turkish, Spanish, Dutch, Polish, German, Italian, Arabic, Japanese, Korean, Chinese and Portuguese commentary languages "download" via R3, then reset to "Download" again after restarting the game.**

One file, 72 bytes, no DLC unlocker needed. Tested on PS5 with kstuff + ShadowMount.

---

## Symptoms

- In **Settings → Audio**, you press **R3** on a commentary language and choose **Yes**.
- The game says the language pack was downloaded, and the commentary works **for that session**.
- After closing and reopening the game, the language shows **"Download"** again.
- This happens for **every language except English and French**.
- Setting up **dlc_emu / the DLC unlocker** or adding entries to `dlc_emu.ini` does **not** help.

## Affected

| | |
|---|---|
| Game | EA SPORTS FC 27 |
| Title ID | PPSA34015 |
| Version | v01.000.004 (other versions: use the script; it searches by name) |
| Setup | PS5 backport dump (BP 4.xx+), kstuff, ShadowMount, fakelib (`libScePlayGo` stub + `dlc_emu`) |

## Root cause

FC 27 runs on Frostbite, whose **StreamInstall** system gives every install package a type. The types are defined in **`Patch/layout.toc`**:

| Type | Meaning | Languages |
|---|---|---|
| `alwaysInstalled` | Always present; checked through PlayGo on every boot | English, French |
| `launchOptional` | Optional; installed on user request | **All other commentary languages** |

On retail hardware, the PS5 system remembers which `launchOptional` packages you downloaded. In a backport environment that state does not persist, so it is lost on every launch and the game asks you to download again.

The language data (`Data/Ps5/commentaryfull_tur_tr.toc`, etc.) is **already in the dump**; nothing is actually downloaded.

### What it is NOT (verified with logging builds)

- **Not dlc_emu.** With the logging build of [drakmor/dlc_emu](https://github.com/drakmor/dlc_emu), the game makes **zero** AppContent or entitlement calls for languages.
- **Not the PlayGo stub.** With the logging build of [drakmor/pgo_stub](https://github.com/drakmor/pgo_stub) 0.5, every language and chunk is already reported as installed. Pressing "Yes" calls `scePlayGoPrefetchOptionalChunk(type=0, mask=0x0000100000000000)` (Turkish), and the call succeeds.
- **Not a read-only `/app0`.** The folder dump is writable.

## The fix

In `Patch/layout.toc`, change the 36 language packages from **`launchOptional` to `alwaysInstalled`**. The game then treats them like English and French and checks them through PlayGo, which reports them as installed.

Two bytes change per package:

```
06 "alwaysInstalled\0" 00  →  01
06 "launchOptional\0"  01  →  00
```

`layout.toc` is a Frostbite DbObject file. The first `0x22C` bytes are a signature header (`00 D1 CE 01`) and the rest is plain data. The header is left untouched, and the PS5 accepts the modified file.

## Usage

### Option A – Script (recommended)

Requires Python 3. The script finds packages **by name**, not by fixed offsets, creates a `layout.toc.orig` backup, and changes nothing if you run it a second time.

```bash
# Preview (writes nothing)
python fc_lang_patch.py "PPSA34015-app/Patch/layout.toc" --dry-run

# Patch all languages
python fc_lang_patch.py "PPSA34015-app/Patch/layout.toc"

# Turkish only
python fc_lang_patch.py "PPSA34015-app/Patch/layout.toc" --only tur_tr,tr
```

Then copy the game folder back to your PS5 or rebuild your image, and launch the game. Your chosen commentary language now persists.

### Option B – Hex editor (v01.000.004 only)

Back up `Patch/layout.toc`, open it in a hex editor (HxD, etc.), and for each row in the table below set the `alwaysInstalled` byte **00→01** and the `launchOptional` byte **01→00**. The file size must stay **105,269 bytes**.

<details>
<summary><b>Byte offset table (72 bytes)</b></summary>

| # | Package | Language | `alwaysInstalled` | `launchOptional` |
|---:|---|---|---|---|
| 1 | `commentarylaunch_tur_tr` | Turkish | `0x03C98` | `0x03F0B` |
| 2 | `commentaryfull_tur_tr` | Turkish | `0x03FE3` | `0x04265` |
| 3 | `commentarylaunch_kor_kr` | Korean | `0x04341` | `0x045B4` |
| 4 | `commentaryfull_kor_kr` | Korean | `0x0468B` | `0x0490D` |
| 5 | `commentarylaunch_chs_cn` | Simplified Chinese | `0x049E8` | `0x04C5B` |
| 6 | `commentaryfull_chs_cn` | Simplified Chinese | `0x04D3D` | `0x04FD9` |
| 7 | `commentarylaunch_spa_mx` | Spanish (Mexico) | `0x050BF` | `0x05332` |
| 8 | `commentaryfull_spa_mx` | Spanish (Mexico) | `0x0540D` | `0x056A9` |
| 9 | `commentarylaunch_spa_es` | Spanish | `0x05788` | `0x059FB` |
| 10 | `commentaryfull_spa_es` | Spanish | `0x05AD3` | `0x05D6F` |
| 11 | `commentarylaunch_por_br` | Portuguese (Brazil) | `0x05E4B` | `0x060BE` |
| 12 | `commentaryfull_por_br` | Portuguese (Brazil) | `0x061A2` | `0x0643E` |
| 13 | `commentarylaunch_pol_pl` | Polish | `0x06526` | `0x06799` |
| 14 | `commentaryfull_pol_pl` | Polish | `0x06870` | `0x06B0C` |
| 15 | `commentarylaunch_jpn_jp` | Japanese | `0x06BE7` | `0x06E5A` |
| 16 | `commentaryfull_jpn_jp` | Japanese | `0x06F33` | `0x071CF` |
| 17 | `commentarylaunch_ita_it` | Italian | `0x072AC` | `0x0751F` |
| 18 | `commentaryfull_ita_it` | Italian | `0x075F7` | `0x07893` |
| 19 | `commentarylaunch_ger_de` | German | `0x0796F` | `0x07BE2` |
| 20 | `commentaryfull_ger_de` | German | `0x07CB9` | `0x07F55` |
| 21 | `commentarylaunch_dut_nl` | Dutch | `0x08030` | `0x082A3` |
| 22 | `commentaryfull_dut_nl` | Dutch | `0x08379` | `0x08615` |
| 23 | `commentarylaunch_ara_sa` | Arabic | `0x086EF` | `0x08962` |
| 24 | `commentaryfull_ara_sa` | Arabic | `0x08A3B` | `0x08CD7` |
| 25 | `installpackage_05/cn` | Simplified Chinese | `0x10929` | `0x10DA8` |
| 26 | `installpackage_05/it` | Italian | `0x10E88` | `0x112FD` |
| 27 | `installpackage_05/ko` | Korean | `0x113D3` | `0x11847` |
| 28 | `installpackage_05/ar` | Arabic | `0x1191C` | `0x11D92` |
| 29 | `installpackage_05/de` | German | `0x1239E` | `0x12812` |
| 30 | `installpackage_05/es` | Spanish | `0x128E7` | `0x12D5C` |
| 31 | `installpackage_05/pl` | Polish | `0x13384` | `0x137F8` |
| 32 | `installpackage_05/tr` | Turkish | `0x138CD` | `0x13D42` |
| 33 | `installpackage_05/mx` | Spanish (Mexico) | `0x13E18` | `0x14290` |
| 34 | `installpackage_05/nl` | Dutch | `0x14369` | `0x147F8` |
| 35 | `installpackage_05/br` | Portuguese (Brazil) | `0x148CC` | `0x14D4D` |
| 36 | `installpackage_05/ja` | Japanese | `0x14E2F` | `0x152A5` |

Turkish only: rows **1, 2, 32**.
</details>

### Verify

| File | MD5 |
|---|---|
| Original `Patch/layout.toc` (v01.000.004) | `52ecb17265a24fe95d7f982490f6ecf9` |
| Patched (all 36 packages) | `6991edcd7fd58ba93f35136f137bca21` |

```powershell
Get-FileHash .\layout.toc -Algorithm MD5
```

### Revert

Rename `layout.toc.orig` back to `layout.toc`.

## Notes

- `Data/layout.toc` does not need changing; the game uses the version in `Patch/`.
- Only `Patch/layout.toc` is modified. `eboot.bin`, `fakelib` and `dlc_emu.ini` stay untouched.
- The same approach likely applies to other Frostbite FC backports (FC 25, FC 26) with the same symptom. Run with `--dry-run` first.
- This repository contains **no game files**, only a patch script and documentation. You need your own dump.

## Credits

- [drakmor](https://github.com/drakmor): `pgo_stub` (PlayGo stub) and `dlc_emu`, whose logging builds made the diagnosis possible.
- DecKerr97: FC 27 backport.

## Keywords

FC 27 language pack not saving · FC 27 commentary download every time · FC 27 Turkish commentary PS5 · FC 27 Spanish commentary backport · R3 audio settings language download reset · PPSA34015 language fix · PS5 backport language DLC · dlc-emu language not working · launchOptional alwaysInstalled layout.toc · Frostbite StreamInstall PlayGo optional chunk · EA FC 27 Türkçe spiker · FC 27 Türkçe dil paketi sürekli indir
