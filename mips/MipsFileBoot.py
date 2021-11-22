#!/usr/bin/python3

from __future__ import annotations

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.GlobalConfig import GlobalConfig

from py_mips_disasm.mips.MipsText import Text
from py_mips_disasm.mips.MipsData import Data
from py_mips_disasm.mips.MipsRodata import Rodata
from py_mips_disasm.mips.MipsBss import Bss
from py_mips_disasm.mips.MipsContext import Context

from .MipsFileGeneric import FileGeneric
from .MipsSplitEntry import SplitEntry, getFileStartsFromEntries

from .ZeldaOffsets import bootVramStart, bootDataStart, bootRodataStart


class FileBoot(FileGeneric):
    def __init__(self, array_of_bytes: bytearray, version: str, context: Context, textSplits: Dict[str, SplitEntry] = {}, dataSplits: Dict[str, SplitEntry] = {}, rodataSplits: Dict[str, SplitEntry] = {}, bssSplits: Dict[str, SplitEntry] = {}):
        super().__init__(array_of_bytes, "boot", version, context)

        self.vRamStart = bootVramStart.get(version, -1)

        text_start = 0
        data_start = bootDataStart.get(version, -1)
        rodata_start = bootRodataStart.get(version, -1)
        # bss_start = bootBssStart.get(version, -1)
        bss_start = self.size

        if rodata_start < 0:
            rodata_start = self.size
        if data_start < 0:
            data_start = rodata_start

        textStarts = getFileStartsFromEntries(textSplits, data_start)
        dataStarts = getFileStartsFromEntries(dataSplits, rodata_start)
        rodataStarts = getFileStartsFromEntries(rodataSplits, bss_start)
        bssStarts = getFileStartsFromEntries(bssSplits, self.size)

        if len(textSplits) == 0:
            textStarts.insert(0, (text_start, textStarts[0][0]-text_start, ""))
        if len(dataSplits) == 0:
            dataStarts.insert(0, (data_start, dataStarts[0][0]-data_start, ""))
        if len(rodataSplits) == 0:
            rodataStarts.insert(0, (rodata_start, rodataStarts[0][0]-rodata_start, ""))
        #if len(bssSplits) == 0:
        #    bssStarts.insert(0, (bss_start, bssStarts[0][0]-bss_start, ""))

        i = 0
        while i < len(textStarts) - 1:
            start, size, filename = textStarts[i]
            end = start + size

            text = Text(self.bytes[start:end], filename, version, context)
            text.parent = self
            text.offset = start
            text.vRamStart = self.vRamStart

            self.textList[filename] = text
            i += 1

        i = 0
        while i < len(dataStarts) - 1:
            start, size, filename = dataStarts[i]
            end = start + size

            data = Data(self.bytes[start:end], filename, version, context)
            data.parent = self
            data.offset = start
            data.vRamStart = self.vRamStart

            self.dataList[filename] = data
            i += 1

        i = 0
        while i < len(rodataStarts) - 1:
            start, size, filename = rodataStarts[i]
            end = start + size

            rodata = Rodata(self.bytes[start:end], filename, version, context)
            rodata.parent = self
            rodata.offset = start
            rodata.vRamStart = self.vRamStart

            self.rodataList[filename] = rodata
            i += 1

        i = 0
        while i < len(bssStarts) - 1:
            start, size, filename = bssStarts[i]
            end = start + size

            # bss = Bss(self.bytes[start:end], filename, version, context)
            # bss.parent = self
            # bss.offset = start
            # bss.vRamStart = self.vRamStart

            # self.bssList[filename] = bss
            i += 1
