BUILD_DIR := build
TARGET := backtestingCpp

.DEFAULT_GOAL := build

.PHONY: build run debug gdb clean rebuild

build:
	cmake -S . -B $(BUILD_DIR)
	cmake --build $(BUILD_DIR)

run: build
	cd $(BUILD_DIR) && ./$(TARGET)

debug:
	cmake -S . -B $(BUILD_DIR) -DCMAKE_BUILD_TYPE=Debug
	cmake --build $(BUILD_DIR)

gdb: debug
	cd $(BUILD_DIR) && gdb ./$(TARGET)

clean:
	cmake --build $(BUILD_DIR) --target clean

rebuild:
	cmake -S . -B $(BUILD_DIR) --fresh
	cmake --build $(BUILD_DIR)