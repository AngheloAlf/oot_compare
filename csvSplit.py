#!/usr/bin/python3

from __future__ import annotations

import argparse

from py_mips_disasm.mips.Utils import *

from mips.MipsSplitEntry import readSplitsFromCsv

def split_fileSplits(game: str, seg: str):
    sections = ["text", "data", "rodata", "bss"]

    tablePerVersion = dict()

    for section in sections:
        csvPath = os.path.join(game, "tables", f"{seg}.{section}.csv")

        if not os.path.exists(csvPath):
            continue

        splits = readSplitsFromCsv(csvPath)
        # print(splits)

        for version, files in splits.items():
            # print(version)

            if version not in tablePerVersion:
                tablePerVersion[version] = []
            else:
                tablePerVersion[version].append("\n")
            tablePerVersion[version].append(f"offset,vram,.{section}\n")

            auxList = []

            for filename, splitData in files.items():
                # print("\t", filename, splitData)
                if splitData.offset < 0 or splitData.vram < 0 or splitData.filename == "":
                    continue
                auxList.append((splitData.offset, splitData.vram, splitData.size, splitData.filename))

            # fake extra to avoid problems
            auxList.append((0xFFFFFF, 0x80FFFFFF, 0, "end"))

            # Reading from the file may not be sorted by offset
            auxList.sort()

            i = 0
            while i < len(auxList) - 1:
                offset, vram, size, filename = auxList[i]
                nextOffset, _, _, _ = auxList[i+1]

                end = offset + size
                if size <= 0:
                    end = nextOffset

                if end < nextOffset:
                    # Adds missing files
                    auxList.insert(i+1, (end, vram + (end - offset), -1, f"file_{end:06X}"))

                tablePerVersion[version].append(f"{offset:X},{vram:X},{filename}\n")

                i += 1


    for version, lines in tablePerVersion.items():
        with open(os.path.join(game, version, "tables", f"files_{seg}.csv"), "w") as f:
            f.writelines(lines)



def main():
    description = ""

    epilog = f"""\
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to extract.", choices=choices)
    parser.add_argument("seg", help="") # TODO
    args = parser.parse_args()

    split_fileSplits(args.game, args.seg)


if __name__ == "__main__":
    main()