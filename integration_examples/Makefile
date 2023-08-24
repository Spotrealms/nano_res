# Variables
RESOURCE_DIR := resources
RESOURCE_DIR_INC := .
SRC_DIR := src
BUILD_DIR := build

# Tools
NRES := .scripts/nr_gen_aio.py

# Python commandline
ifeq ($(OS), Windows_NT) #Windows does not use the `python3` binary name for Python
	PYTHON := python
else 
	PYTHON := python3
endif

# Phony rules
.PHONY: res
res:
	@echo RESOURCES $(RESOURCE_DIR)
	$(PYTHON) $(NRES) -d $(RESOURCE_DIR)
	
.PHONY: build
build:
	@echo BUILD $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)
	$(MAKE) res
	g++ -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -I $(RESOURCE_DIR_INC) $(SRC_DIR)/main.cpp -o $(BUILD_DIR)/main

.PHONY: purge
purge:
	@echo PURGE $(BUILD_DIR)
	rm -rf $(BUILD_DIR)
	$(PYTHON) $(NRES) -p $(RESOURCE_DIR)

## Below lines are for the CMake and Meson examples
#CMake uses the Ninja backend for portability between *nix and Windows
.PHONY: cmake
cmake:
	@echo CMAKE $(BUILD_DIR)
	cmake -B $(BUILD_DIR) -G Ninja && \
	cmake --build $(BUILD_DIR)

.PHONY: meson
meson:
	@echo MESON $(BUILD_DIR)
	meson setup $(BUILD_DIR) --backend ninja && \
	meson compile -C $(BUILD_DIR)