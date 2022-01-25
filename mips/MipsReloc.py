#!/usr/bin/python3

from __future__ import annotations

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.GlobalConfig import GlobalConfig
from py_mips_disasm.mips.MipsFileBase import FileBase
from py_mips_disasm.mips.MipsSection import Section
from py_mips_disasm.mips.MipsContext import Context


class RelocEntry:
    sectionNames = {
        #0: ".bss",
        1: ".text",
        2: ".data",
        3: ".rodata",
        4: ".bss", # ?
    }
    relocationsNames = {
        2: "R_MIPS_32",
        4: "R_MIPS_26",
        5: "R_MIPS_HI16",
        6: "R_MIPS_LO16",
    }

    def __init__(self, entry: int):
        self.sectionId = entry >> 30
        self.relocType = (entry >> 24) & 0x3F
        self.offset = entry & 0x00FFFFFF

    @property
    def reloc(self):
        return (self.sectionId << 30) | (self.relocType << 24) | (self.offset)

    def getSectionName(self) -> str:
        return RelocEntry.sectionNames.get(self.sectionId, str(self.sectionId))

    def getTypeName(self) -> str:
        return RelocEntry.relocationsNames.get(self.relocType, str(self.relocType))

    def __str__(self) -> str:
        section = self.getSectionName()
        reloc = self.getTypeName()
        return f"{section} {reloc} {hex(self.offset)}"
    def __repr__(self) -> str:
        return self.__str__()

class Reloc(Section):
    def __init__(self, array_of_bytes: bytearray, filename: str, version: str, context: Context):
        super().__init__(array_of_bytes, filename, version, context)

        self.textSize = self.words[0]
        self.dataSize = self.words[1]
        self.rodataSize = self.words[2]
        self.bssSize = self.words[3]
        self.relocCount = self.words[4]

        self.tail = self.words[self.relocCount+5:-1]

        self.seekup = self.words[-1]

        self.entries: List[RelocEntry] = list()
        for word in self.words[5:self.relocCount+5]:
            self.entries.append(RelocEntry(word))

    @property
    def nRelocs(self):
        return len(self.entries)

    def compareToFile(self, other_file: FileBase):
        result = super().compareToFile(other_file)
        # TODO
        return result

    def blankOutDifferences(self, other_file: FileBase) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        # TODO ?
        # super().blankOutDifferences(File)
        return False

    def removePointers(self) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        # TODO ?
        #super().removePointers()
        return False

    def saveToFile(self, filepath: str):
        super().saveToFile(filepath + ".reloc")

        if self.size == 0:
            return

        with open(filepath + ".reloc.s", "w") as f:
            offset = 0
            currentVram = self.getVramOffset(offset)

            f.write(".include \"macro.inc\"\n")
            f.write("\n")
            f.write("# assembler directives\n")
            f.write(".set noat      # allow manual use of $at\n")
            f.write(".set noreorder # don't insert nops after branches\n")
            f.write(".set gp=64     # allow use of 64-bit general purpose registers\n")
            f.write("\n")
            f.write(".section .ovl\n")
            f.write("\n")
            f.write(".balign 16\n")

            f.write(f"glabel {self.filename}OverlayInfo\n")

            f.write(f"/* %05X %08X %08X */  .word _{self.filename}SegmentTextSize # {self.textSize}\n" % (offset + self.commentOffset + 0x0, currentVram + 0x0, self.textSize))
            f.write(f"/* %05X %08X %08X */  .word _{self.filename}SegmentDataSize # {self.dataSize}\n" % (offset + self.commentOffset + 0x4, currentVram + 0x4, self.dataSize))
            f.write(f"/* %05X %08X %08X */  .word _{self.filename}SegmentRoDataSize # {self.rodataSize}\n" % (offset + self.commentOffset + 0x8, currentVram + 0x8, self.rodataSize))
            f.write(f"/* %05X %08X %08X */  .word _{self.filename}SegmentBssSize # {self.bssSize}\n" % (offset + self.commentOffset + 0xC, currentVram + 0xC, self.bssSize))
            f.write(f"\n")
            f.write(f"/* %05X %08X %08X */  .word  {self.relocCount} # reloc_count\n" % (offset + self.commentOffset + 0x10, currentVram + 0x10, self.relocCount))
            f.write(f"\n")

            offset += 0x14

            f.write(f"glabel {self.filename}OverlayRelocations\n")
            for r in self.entries:
                offsetHex = toHex(offset + self.commentOffset, 5)[2:]
                vramHex = ""
                if self.vRamStart != -1:
                    currentVram = self.getVramOffset(offset)
                    vramHex = toHex(currentVram, 8)[2:]
                relocHex = toHex(r.reloc, 8)[2:]
                line = str(r)

                f.write(f"/* {offsetHex} {vramHex} {relocHex} */  .word 0x{relocHex} # {line}\n")
                offset += 4

            f.write("\n")
            for pad in self.tail:
                offsetHex = toHex(offset + self.commentOffset, 5)[2:]
                vramHex = ""
                if self.vRamStart != -1:
                    currentVram = self.getVramOffset(offset)
                    vramHex = toHex(currentVram, 8)[2:]
                padcHex = toHex(pad, 8)

                f.write(f"/* {offsetHex} {vramHex} {padcHex[2:]} */  .word {padcHex}\n")
                offset += 4

            f.write(f"glabel {self.filename}OverlayInfoOffset\n")
            currentVram = self.getVramOffset(offset)
            f.write(f"/* %05X %08X %08X */  .word  {self.seekup}\n" % (offset + 0x0, currentVram + 0x0, self.seekup))
