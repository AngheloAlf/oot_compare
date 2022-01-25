MAKEFLAGS += --no-builtin-rules

# Build options can either be changed by modifying the makefile, or by building with 'make SETTING=value'

GAME     ?= oot
VERSION  ?= ne0

MAKE = make

DISASSEMBLER        ?= ./py_mips_disasm/simpleDisasm.py
OVL_DISASSEMBLER    ?= ./z64OvlDisasm.py

#### Files ####

BASE_DIR       := $(GAME)/$(VERSION)

# ROM image
BASE_ROM       := $(GAME)/$(GAME)_$(VERSION).z64

# ASM_DIRS       := $(shell find $(BASE_DIR)/asm/ -type d)

# S_FILES        := $(foreach dir,$(ASM_DIRS),$(wildcard $(dir)/*.s))

BASEROM_FILES  := $(wildcard $(BASE_DIR)/baserom/*)

DISASM_LIST    := $(shell cat $(GAME)/tables/disasm_list.txt) \
                  $(shell [ -f $(BASE_DIR)/tables/disasm_list.txt ] && cat $(BASE_DIR)/tables/disasm_list.txt)

CSV_FILES      := $(DISASM_LIST:%=$(BASE_DIR)/tables/files_%.csv) \
                  $(BASE_DIR)/tables/functions.csv $(BASE_DIR)/tables/variables.csv
DISASM_TARGETS := $(DISASM_LIST:%=$(BASE_DIR)/asm/text/%/.disasm)

.PHONY: all splitcsvs disasm clean
.DEFAULT_GOAL := all


#### Main commands ####

## Cleaning ##
clean:
	$(RM) -rf $(BASE_DIR)/asm $(BASE_DIR)/context

asmclean:
	$(RM) -rf $(BASE_DIR)/asm $(BASE_DIR)/context

## Extraction step
setup:
#	$(MAKE) -C tools
	./extract_baserom.py $(GAME) $(VERSION)

## Assembly generation
disasm: $(DISASM_TARGETS)
	@echo "Disassembly done!"



all: disasm

disasm: splitcsvs

splitcsvs: $(CSV_FILES)

#### Various Recipes ####
$(BASE_DIR)/tables/%.csv: $(GAME)/tables/%.csv
	./csvSplit.py $(GAME) $<
$(BASE_DIR)/tables/files_%.csv: $(GAME)/tables/%.*.csv
	./csvSplit.py $(GAME) $<



$(BASE_DIR)/asm/text/%/.disasm: $(BASE_DIR)/baserom/% $(BASE_DIR)/tables/variables.csv $(BASE_DIR)/tables/functions.csv $(BASE_DIR)/tables/files_%.csv
	$(RM) -rf $(BASE_DIR)/asm/text/$* $(BASE_DIR)/asm/data/$* $(BASE_DIR)/context/$*.txt
	$(DISASSEMBLER) $< $(BASE_DIR)/asm/text/$* -q --data-output $(BASE_DIR)/asm/data/$* \
		--file-splits $(BASE_DIR)/tables/files_$*.csv  \
		--variables $(BASE_DIR)/tables/variables.csv \
		--functions $(BASE_DIR)/tables/functions.csv \
		--constants $(GAME)/tables/constants.csv \
		--save-context $(BASE_DIR)/context/$*.txt \
		--constants $(BASE_DIR)/tables/constants_$*.csv
	@touch $@


$(BASE_DIR)/asm/text/ovl_%/.disasm: $(BASE_DIR)/baserom/ovl_% $(BASE_DIR)/tables/variables.csv $(BASE_DIR)/tables/functions.csv
	$(RM) -rf $(BASE_DIR)/asm/text/ovl_$* $(BASE_DIR)/asm/data/ovl_$* $(BASE_DIR)/context/ovl_$*.txt
	$(OVL_DISASSEMBLER) $< $(BASE_DIR)/asm/text/ovl_$* -v --data-output $(BASE_DIR)/asm/data/ovl_$* \
		--file-splits $(BASE_DIR)/tables/files_ovl_$*.csv \
		--variables $(BASE_DIR)/tables/variables.csv \
		--functions $(BASE_DIR)/tables/functions.csv \
		--constants $(GAME)/tables/constants.csv \
		--save-context $(BASE_DIR)/context/ovl_$*.txt \
		--constants $(BASE_DIR)/tables/constants_ovl_$*.csv \
		--file-addresses $(BASE_DIR)/tables/file_addresses.csv
	@touch $@
