#!/bin/bash

# Set variables
BUILD_FOLDER="pydantic_tfl_api"
SRC_FOLDER="src"
SPEC_FILE="TfL_OpenAPI_specs"
BUILD_SCRIPT="build_models.py"

# 1. Delete the content of the pydantic_tfl_api folder
if [ -d "$BUILD_FOLDER" ]; then
    rm -rf "$BUILD_FOLDER"/*
else
    echo "The $BUILD_FOLDER directory doesn't exist. Creating it..."
fi

# 2. Create the pydantic_tfl_api folder (if it doesn't exist)
mkdir -p "$BUILD_FOLDER"

# 3. Copy the content of app folder to pydantic_tfl_api
if [ -d "$SRC_FOLDER" ]; then
    cp -R "$SRC_FOLDER"/* "$BUILD_FOLDER"
else
    echo "Error: The $SRC_FOLDER directory doesn't exist."
    exit 1
fi

# 4. Run the build_models.py script with arguments
if [ -f "$BUILD_SCRIPT" ]; then
    python "$BUILD_SCRIPT" "$SPEC_FILE" "$BUILD_FOLDER"
else
    echo "Error: The $BUILD_SCRIPT file doesn't exist."
    exit 1
fi

echo "Script execution completed."