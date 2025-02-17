# Compiler and flags
CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17

# Directories
SRC_DIR = .
OBJ_DIR = tmp
BIN_DIR = tmp

# Source files
SRC_FILES = $(wildcard $(SRC_DIR)/*.cc) $(wildcard $(SRC_DIR)/Instance/*.cc)
OBJ_FILES = $(patsubst $(SRC_DIR)/%.cc, $(OBJ_DIR)/%.o, $(SRC_FILES))

# Executable name
EXEC = $(BIN_DIR)/main

# Default target
all: $(EXEC)

# Create directories if they don't exist
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)


# Create object directories dynamically
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cc | $(OBJ_DIR) $(BIN_DIR)
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# # Compile source files into object files
# $(OBJ_DIR)/%.o: $(SRC_DIR)/%.cc | $(OBJ_DIR)
# 	$(CXX) $(CXXFLAGS) -c $< -o $@

# Link object files into the executable
$(EXEC): $(OBJ_FILES) | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $(OBJ_FILES) -o $@

# Clean target to remove the tmp directory
clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)

# Phony targets
.PHONY: all clean
