#!/usr/bin/python3

from __future__ import annotations

import argparse
import os
import sys
import struct
from multiprocessing import Pool, cpu_count, Manager
from typing import Dict, List
import zlib


ROM_FILE_NAME = 'baserom.z64'
ROM_FILE_NAME_V = 'baserom_{}.z64'
FILE_TABLE_OFFSET = {
    "NTSC 0.9":     0x07430, # a.k.a. NTSC 1.0 RC
    "NTSC 1.0":     0x07430,
    "NTSC 1.1":     0x07430,
    "PAL 1.0":      0x07950,
    "NTSC 1.2":     0x07960,
    "PAL 1.1":      0x07950,
    "JP GC":        0x07170,
    "JP MQ":        0x07170,
    "USA GC":       0x07170,
    "USA MQ":       0x07170,
    "PAL GC DBG1":  0x12F70,
    "PAL MQ DBG":   0x12F70,
    "PAL GC DBG2":  0x12F70,
    "PAL GC":       0x07170,
    "PAL MQ":       0x07170,
    "JP GC CE":     0x07170, # Zelda collection
    "IQUE CN":      0x0B7A0,
    "IQUE TW":      0x0B240,
    "GATEWAY":      0x0AC80, # fake

    # MM
    "MM JP 1.0":    0x1C110,
    "MM JP 1.1":    0x1C050,
    "MM USA DEMO":  0x1AB50,
    "MM USA":       0x1A500,
    "MM PAL 1.0":   0x1A650,
    "MM PAL DBG":   0x24F60,
    "MM PAL 1.1":   0x1A8D0,
    "MM USA GC":    0x1AE90,
    "MM PAL GC":    0x1AE90,
    "MM JP GC":     0x1AE90,
}
FILE_TABLE_OFFSET["NTSC J 0.9"]   = FILE_TABLE_OFFSET["NTSC 0.9"]
FILE_TABLE_OFFSET["NTSC J 1.0"]   = FILE_TABLE_OFFSET["NTSC 1.0"]
FILE_TABLE_OFFSET["NTSC J 1.1"]   = FILE_TABLE_OFFSET["NTSC 1.1"]
FILE_TABLE_OFFSET["NTSC J 1.2"]   = FILE_TABLE_OFFSET["NTSC 1.2"]
FILE_TABLE_OFFSET["PAL WII 1.1"]  = FILE_TABLE_OFFSET["PAL 1.1"]

FILE_NAMES: Dict[str, List[str] | None] = {
    "NTSC 0.9":     None,
    "NTSC 1.0":     None,
    "NTSC 1.1":     None,
    "PAL 1.0":      None,
    "NTSC 1.2":     None,
    "PAL 1.1":      None,
    "JP GC":        None,
    "JP MQ":        None,
    "USA GC":       None,
    "USA MQ":       None,
    "PAL GC DBG1":  None,
    "PAL GC DBG2":  None,
    "PAL MQ DBG":   None,
    "PAL GC":       None,
    "PAL MQ":       None,
    "JP GC CE":     None, # Zelda collector's edition
    "IQUE CN":      None,
    "IQUE TW":      None,
    "GATEWAY":      None, # fake

    # MM
    "MM JP 1.0":    None,
    "MM JP 1.1":    None,
    "MM USA DEMO":  None,
    "MM USA":       None,
    "MM PAL 1.0":   None,
    "MM PAL DBG":   None,
    "MM PAL 1.1":   None,
    "MM USA GC":    None,
    "MM PAL GC":    None,
    "MM JP GC":     None,
}
FILE_NAMES["NTSC J 0.9"]  = FILE_NAMES["NTSC 0.9"]
FILE_NAMES["NTSC J 1.0"]  = FILE_NAMES["NTSC 1.0"]
FILE_NAMES["NTSC J 1.1"]  = FILE_NAMES["NTSC 1.1"]
FILE_NAMES["NTSC J 1.2"]  = FILE_NAMES["NTSC 1.2"]
FILE_NAMES["PAL WII 1.1"] = FILE_NAMES["PAL 1.1"]

romData: bytes = None
Edition = "" # "pal_mq"
Version = "" # "PAL MQ"


def readFile(filepath):
    with open(filepath) as f:
        return [x.strip() for x in f.readlines()]

def readFilelists():
    FILE_NAMES["PAL MQ DBG"] = readFile("filelists/filelist_pal_mq_dbg.txt")
    FILE_NAMES["PAL MQ"] = readFile("filelists/filelist_pal_mq.txt")
    FILE_NAMES["USA MQ"] = readFile("filelists/filelist_usa_mq.txt")
    FILE_NAMES["NTSC 1.0"] = readFile("filelists/filelist_ntsc_1.0.txt")
    FILE_NAMES["PAL 1.0"] = readFile("filelists/filelist_pal_1.0.txt")
    FILE_NAMES["JP GC CE"] = readFile("filelists/filelist_jp_gc_ce.txt")
    FILE_NAMES["IQUE CN"] = readFile("filelists/filelist_ique_cn.txt")

    FILE_NAMES["JP MQ"] = FILE_NAMES["USA MQ"]

    FILE_NAMES["USA GC"] = FILE_NAMES["JP GC CE"]
    FILE_NAMES["JP GC"] = FILE_NAMES["USA GC"]
    FILE_NAMES["PAL GC"] = FILE_NAMES["PAL MQ"]

    FILE_NAMES["PAL 1.1"] = FILE_NAMES["PAL 1.0"]

    FILE_NAMES["PAL GC DBG1"] = FILE_NAMES["PAL MQ DBG"]
    FILE_NAMES["PAL GC DBG2"] = FILE_NAMES["PAL MQ DBG"]

    FILE_NAMES["IQUE TW"] = FILE_NAMES["IQUE CN"]

    FILE_NAMES["NTSC 0.9"] = FILE_NAMES["NTSC 1.0"]
    FILE_NAMES["NTSC 1.1"] = FILE_NAMES["NTSC 1.0"]
    FILE_NAMES["NTSC 1.2"] = FILE_NAMES["NTSC 1.0"]

    FILE_NAMES["NTSC J 0.9"]  = FILE_NAMES["NTSC 0.9"]
    FILE_NAMES["NTSC J 1.0"]  = FILE_NAMES["NTSC 1.0"]
    FILE_NAMES["NTSC J 1.1"]  = FILE_NAMES["NTSC 1.1"]
    FILE_NAMES["NTSC J 1.2"]  = FILE_NAMES["NTSC 1.2"]
    FILE_NAMES["PAL WII 1.1"] = FILE_NAMES["PAL 1.1"]

    FILE_NAMES["GATEWAY"] = FILE_NAMES["IQUE CN"]

    # MM
    FILE_NAMES["MM JP 1.0"] = readFile("filelists/filelist_mm_jp_1.0.txt")
    FILE_NAMES["MM USA DEMO"] = readFile("filelists/filelist_mm_usa_demo.txt")
    FILE_NAMES["MM USA"] = readFile("filelists/filelist_mm_usa.txt")
    FILE_NAMES["MM PAL DBG"] = readFile("filelists/filelist_mm_pal_dbg.txt")
    FILE_NAMES["MM USA GC"] = readFile("filelists/filelist_mm_usa_gc.txt")
    FILE_NAMES["MM PAL GC"] = readFile("filelists/filelist_mm_pal_gc.txt")
    FILE_NAMES["MM JP GC"] = readFile("filelists/filelist_mm_jp_gc.txt")

    FILE_NAMES["MM JP 1.1"] = FILE_NAMES["MM JP 1.0"]
    FILE_NAMES["MM PAL 1.0"] = FILE_NAMES["MM PAL DBG"]
    FILE_NAMES["MM PAL 1.1"] = FILE_NAMES["MM PAL 1.0"]

def initialize_worker(rom_data: bytes, dmaTable: dict):
    global romData
    global globalDmaTable
    romData = rom_data
    globalDmaTable = dmaTable

def read_uint32_be(offset):
    return struct.unpack('>I', romData[offset:offset+4])[0]

def write_output_file(name, offset, size):
    try:
        with open(name, 'wb') as f:
            f.write(romData[offset:offset+size])
    except IOError:
        print('failed to write file ' + name)
        sys.exit(1)


def decompressZlib(data: bytearray) -> bytearray:
    decomp = zlib.decompressobj(-zlib.MAX_WBITS)
    output = bytearray()
    output.extend(decomp.decompress(data))
    while decomp.unconsumed_tail:
        output.extend(decomp.decompress(decomp.unconsumed_tail))
    output.extend(decomp.flush())
    return output

def writeBytearrayToFile(filepath: str, array_of_bytes: bytearray):
    with open(filepath, mode="wb") as f:
       f.write(array_of_bytes)

def readFileAsBytearray(filepath: str) -> bytearray:
    if not os.path.exists(filepath):
        return bytearray(0)
    with open(filepath, mode="rb") as f:
        return bytearray(f.read())


def ExtractFunc(i):
    versionName = FILE_NAMES[Version][i]
    if versionName == "":
        print(f"Skipping {i} because it doesn't have a name.")
        return
    filename = f'baserom_{Edition}/' + versionName
    entryOffset = FILE_TABLE_OFFSET[Version] + 16 * i

    virtStart = read_uint32_be(entryOffset + 0)
    virtEnd   = read_uint32_be(entryOffset + 4)
    physStart = read_uint32_be(entryOffset + 8)
    physEnd   = read_uint32_be(entryOffset + 12)

    if physStart == 0xFFFFFFFF and physEnd == 0xFFFFFFFF: # file deleted
        if (virtEnd - virtStart) == 0:
            return
        physStart = virtStart
        physEnd = 0
        compressed = False
        size = virtEnd - virtStart
    if physEnd == 0:  # uncompressed
        compressed = False
        size = virtEnd - virtStart
    else:             # compressed
        compressed = True
        size = physEnd - physStart

    globalDmaTable[versionName].append(virtStart)
    globalDmaTable[versionName].append(virtEnd)
    globalDmaTable[versionName].append(physStart)
    globalDmaTable[versionName].append(physEnd)

    print('extracting ' + filename + " (0x%08X, 0x%08X)" % (virtStart, virtEnd))
    write_output_file(filename, physStart, size)
    if compressed:
        # print(f"decompressing {filename}")
        if Edition in ("ique_cn", "ique_tw"):
            data = readFileAsBytearray(filename)
            decompressed = decompressZlib(data)
            writeBytearrayToFile(filename, decompressed)
        else:
            exit_code = os.system('tools/yaz0 -d ' + filename + ' ' + filename)
            if exit_code != 0:
                pass
                #os.remove(filename)
                # exit(exit_code)

#####################################################################

def printBuildData(rom_data: bytes):
    buildDataOffset = FILE_TABLE_OFFSET[Version] - 16*3
    buildTeam = ""
    i = 0
    while rom_data[buildDataOffset + i] != 0:
        buildTeam += chr(rom_data[buildDataOffset + i])
        i += 1

    while rom_data[buildDataOffset + i] == 0:
        i += 1

    buildDate = ""
    while rom_data[buildDataOffset + i] != 0:
        buildDate += chr(rom_data[buildDataOffset + i])
        i += 1

    i += 1

    buildMakeOption = ""
    while rom_data[buildDataOffset + i] != 0:
        buildMakeOption += chr(rom_data[buildDataOffset + i])
        i += 1

    print("========================================")
    print(f"| Build team:   {buildTeam}".ljust(39) + "|")
    print(f"| Build date:   {buildDate}".ljust(39) + "|")
    #print(f"| Make Option:  {buildMakeOption}".ljust(39) + "|")
    print("========================================")

def extract_rom(j):
    print("Reading filelists...")
    readFilelists()

    file_names_table = FILE_NAMES[Version]
    if file_names_table is None:
        print(f"'{Edition}' is not supported yet because the filelist is missing.")
        sys.exit(2)

    try:
        os.mkdir(f'baserom_{Edition}')
    except:
        pass

    filename = ROM_FILE_NAME_V.format(Edition)
    if not os.path.exists(filename):
        print(f"{filename} not found. Defaulting to {ROM_FILE_NAME}")
        filename = ROM_FILE_NAME

    # read baserom data
    try:
        with open(filename, 'rb') as f:
            rom_data = f.read()
    except IOError:
        print('Failed to read file ' + filename)
        sys.exit(1)

    manager = Manager()
    dmaTable = manager.dict()
    for name in file_names_table:
        dmaTable[name] = manager.list()

    # extract files
    if j:
        num_cores = cpu_count()
        print("Extracting baserom with " + str(num_cores) + " CPU cores.")
        with Pool(num_cores, initialize_worker, (rom_data, dmaTable)) as p:
            p.map(ExtractFunc, range(len(file_names_table)))
    else:
        initialize_worker(rom_data, dmaTable)
        for i in range(len(file_names_table)):
            ExtractFunc(i)

    printBuildData(rom_data)

    filetable = f'baserom_{Edition}/dma_addresses.txt'
    print(f"Creating {filetable}")
    with open(filetable, "w") as f:
        for filename, data in dmaTable.items():
            f.write(",".join([filename] + list(map(str, data))) + "\n")

def main():
    description = "Extracts files from the rom. Will try to read the rom 'baserom_version.z64', or 'baserom.z64' if that doesn't exists."

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    choices = [x.lower().replace(" ", "_") for x in FILE_TABLE_OFFSET]
    parser.add_argument("edition", help="Select the version of the game to extract.", choices=choices, default="pal_mq_dbg", nargs='?')
    parser.add_argument("-j", help="Enables multiprocessing.", action="store_true")
    args = parser.parse_args()

    global Edition
    global Version

    Edition = args.edition
    Version = Edition.upper().replace("_", " ")

    extract_rom(args.j)

if __name__ == "__main__":
    main()
