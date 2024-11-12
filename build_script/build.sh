#!/bin/bash

# Display help message if --help, -h, or no arguments are provided
if [[ "$1" == "--help" || "$1" == "-h" || $# -eq 0 ]]; then
    echo "Usage: ./script.sh <BUILD_FOLDER> [SPEC_FOLDER] [RUN_BUILDSCRIPT]"
    echo
    echo "Arguments:"
    echo "  BUILD_FOLDER     Required. The path to the build folder."
    echo "  SPEC_FOLDER      Optional. The path to the spec folder. Required if RUN_BUILDSCRIPT is 'true'."
    echo "  RUN_BUILDSCRIPT  Optional. Boolean value ('true' or 'false') to indicate whether to run the build script."
    echo
    echo "Description:"
    echo "  This script performs the following tasks:"
    echo "    1. Deletes the 'models' and 'endpoints' folders in the specified BUILD_FOLDER, if they exist."
    echo "    2. Creates the 'models' and 'endpoints' directories inside BUILD_FOLDER."
    echo "    3. Optionally runs the build_models.py script with SPEC_FOLDER and BUILD_FOLDER arguments if RUN_BUILDSCRIPT is 'true'."
    echo
    echo "Example:"
    echo "  ./script.sh build_output specs true"
    echo
    exit 0
fi

# Set variables
# Take the first argument as the build folder
BUILD_FOLDER=$1
# Check if the build folder is provided
if [ -z "$BUILD_FOLDER" ]; then
    echo "Error: Please provide the build folder as the first argument."
    exit 1
fi
# Variables for spec file and build script
SPEC_FOLDER=$2



BUILD_SCRIPT="build_models.py"

# Check if we should run the build script based on the third argument (boolean value)
RUN_BUILDSCRIPT=$3

# Validate RUN_BUILDSCRIPT is either "true" or "false"
if [ -z "$RUN_BUILDSCRIPT" ]; then
    RUN_BUILDSCRIPT=false
    echo "Info: No third argument provided, assuming NOT to run build script $BUILD_SCRIPT."
else
    # Convert RUN_BUILDSCRIPT to lowercase
    RUN_BUILDSCRIPT_LOWER=$(echo "$RUN_BUILDSCRIPT" | tr '[:upper:]' '[:lower:]')
    
    # Ensure RUN_BUILDSCRIPT is a valid boolean
    if [ "$RUN_BUILDSCRIPT_LOWER" != "true" ] && [ "$RUN_BUILDSCRIPT_LOWER" != "false" ]; then
        echo "Error: The third argument must be a boolean value ('true' or 'false')."
        exit 1
    fi

    # If true, check for the build script
    if [ "$RUN_BUILDSCRIPT_LOWER" == "true" ]; then
        if [ ! -f "$BUILD_SCRIPT" ]; then
            echo "Error: The $BUILD_SCRIPT file doesn't exist."
            exit 1
        fi
        # Check if the spec folder is provided and exists
        if [ -z "$SPEC_FOLDER" ]; then
            echo "Error: Please provide the spec folder as the second argument."
            exit 1
        fi

        if [ ! -d "$SPEC_FOLDER" ]; then
            echo "Error: The spec folder '$SPEC_FOLDER' does not exist."
            exit 1
        fi        
        echo "Info: Running build script $BUILD_SCRIPT."
    fi
fi

# 1. Delete the content of the pydantic_tfl_api folder (models and endpoints)
if [ -d "$BUILD_FOLDER" ]; then
    echo "The $BUILD_FOLDER directory exists. Deleting 'models' and 'endpoints' folders..."
    rm -rf "$BUILD_FOLDER/models"
    rm -rf "$BUILD_FOLDER/endpoints"
    
else
    echo "The $BUILD_FOLDER directory doesn't exist. Creating it..."
fi

# 2. Create the pydantic_tfl_api folder structure (models and endpoints)
mkdir -p "$BUILD_FOLDER/models"
mkdir -p "$BUILD_FOLDER/endpoints"

# 3. Optionally run the build_models.py script if RUN_BUILDSCRIPT is true
if [ "$RUN_BUILDSCRIPT_LOWER" == "true" ]; then
    python "$BUILD_SCRIPT" "$SPEC_FOLDER" "$BUILD_FOLDER"
fi

echo "Script execution completed."
