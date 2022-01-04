#!/usr/bin/python3

from __future__ import annotations

import argparse

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.GlobalConfig import GlobalConfig
from py_mips_disasm.mips.MipsText import Text
from py_mips_disasm.mips.MipsData import Data
from py_mips_disasm.mips.MipsRodata import Rodata
from py_mips_disasm.mips.MipsContext import Context

from mips.MipsFileCode import FileCode
from mips.ZeldaTables import DmaEntry, contextReadVariablesCsv, contextReadFunctionsCsv, getDmaAddresses

from mips.ZeldaOffsets import codeVramStart, codeDataStart, codeRodataStart

GlobalConfig.REMOVE_POINTERS = False
GlobalConfig.IGNORE_BRANCHES = False
GlobalConfig.IGNORE_04 = False
GlobalConfig.IGNORE_06 = False
GlobalConfig.IGNORE_80 = False
GlobalConfig.WRITE_BINARY = False
GlobalConfig.ASM_COMMENT = True
GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
# GlobalConfig.TRUST_USER_FUNCTIONS = True
# GlobalConfig.DISASSEMBLE_UNKNOWN_INSTRUCTIONS = args.disasm_unknown
# GlobalConfig.VERBOSE = args.verbose
# GlobalConfig.QUIET = args.quiet

def readCodeSplitsCsv():
    code_splits_file = readCsv("csvsplits/code_text.csv")

    header = code_splits_file[0][3::3]
    splits = { h: dict() for h in header }

    for i in range(2, len(code_splits_file)):
        row = code_splits_file[i]
        filename1, filename2, _, *data = row
        name = filename1 or filename2
        if name == "":
            continue

        for i in range(len(header)):
            h = header[i]
            if h == "":
                continue
            offset, vram, size = data[i*3:(i+1)*3]
            try:
                offset = int(offset, 16)
            except:
                continue

            try:
                size = int(size, 16)
            except:
                size = -1

            splits[h][name] = (offset, size)
    return splits

parser = argparse.ArgumentParser()
choices = ["oot", "mm"]
parser.add_argument("game", help="Game to comapre.", choices=choices)
parser.add_argument("version", help="Select which baserom folder will be used.")
args = parser.parse_args()


CODE = "code"
VERSION = args.version

palMqDbg_Code_array = readVersionedFileAsBytearrray(CODE, args.game, VERSION)

codeSplits = readCodeSplitsCsv()
context = Context()
context.readFunctionMap(VERSION)
contextReadVariablesCsv(context, args.game, VERSION)
contextReadFunctionsCsv(context, args.game, VERSION)

palMqDbg_filesStarts = list()
if VERSION in codeSplits:
    for codeFilename, (offset, size) in codeSplits[VERSION].items():
        palMqDbg_filesStarts.append((offset, size, codeFilename))
else:
    palMqDbg_filesStarts.append((0, len(palMqDbg_Code_array), "start_dummy_000000"))
palMqDbg_filesStarts.append((codeDataStart.get(VERSION, 0xFFFFFFFF), 0, "end"))

palMqDbg_filesStarts.sort()

palMqDbg_texts: List[Text] = []
i = 0
while i < len(palMqDbg_filesStarts) - 1:
    start, size, filename = palMqDbg_filesStarts[i]
    nextStart, _, _ = palMqDbg_filesStarts[i+1]

    end = start + size
    if size < 0:
        end = nextStart

    if end < nextStart:
        palMqDbg_filesStarts.insert(i+1, (end, -1, f"file_{toHex(end, 6)}"))

    text = Text(palMqDbg_Code_array[start:end], filename, VERSION, context)
    text.offset = start
    text.vRamStart = codeVramStart.get(args.game, {}).get(VERSION, -1)

    text.analyze()

    palMqDbg_texts.append(text)
    i += 1

section_data = Data(palMqDbg_Code_array[codeDataStart.get(VERSION, -1):codeRodataStart.get(VERSION, -1)], CODE, VERSION, context)
section_rodata = Rodata(palMqDbg_Code_array[codeRodataStart.get(VERSION, -1):], CODE, VERSION, context)

section_data.vRamStart = codeVramStart.get(args.game, {}).get(VERSION, -1) + codeDataStart.get(args.game, {}).get(VERSION, -1)
section_rodata.vRamStart = codeVramStart.get(args.game, {}).get(VERSION, -1) + codeRodataStart.get(args.game, {}).get(VERSION, -1)

section_data.analyze()
section_rodata.analyze()

totalFunctions = 0
for text in palMqDbg_texts:
    print(text.filename, f" functions: {len(text.functions)} ")
    totalFunctions += len(text.functions)
    if len(text.fileBoundaries) > 0:
        print("boundaries:", len(text.fileBoundaries))

        for i in range(len(text.fileBoundaries)-1):
            start = text.fileBoundaries[i]
            end = text.fileBoundaries[i+1]

            functionsInBoundary = 0
            for func in text.functions:
                funcOffset = func.vram - codeVramStart.get(args.game, {}).get(VERSION, -1)
                if start <= funcOffset < end:
                    functionsInBoundary += 1
            print("\t", toHex(start, 6)[2:], toHex(end-start, 3)[2:], "\t functions:", functionsInBoundary)


        start = text.fileBoundaries[-1]
        end = text.size + text.offset

        functionsInBoundary = 0
        for func in text.functions:
            funcOffset = func.vram - codeVramStart.get(args.game, {}).get(VERSION, -1)
            if start <= funcOffset < end:
                functionsInBoundary += 1
        print("\t", toHex(start, 6)[2:], toHex(end-start, 3)[2:], "\t functions:", functionsInBoundary)

    print()

print(f"Total functions found: {totalFunctions}\n")

OUTPUT_FOLDER = "splits"

new_file_folder = os.path.join(OUTPUT_FOLDER, VERSION, CODE)
shutil.rmtree(new_file_folder, ignore_errors=True)
print(f"Writing files to {new_file_folder}")
os.makedirs(new_file_folder, exist_ok=True)
for text in palMqDbg_texts:
    new_file_path = os.path.join(new_file_folder, text.filename)

    # print(f"Writing file {new_file_path}")
    text.saveToFile(new_file_path)

section_data.saveToFile(new_file_folder)
section_rodata.saveToFile(new_file_folder)
