#!/bin/bash

# This script runs the llama-cpp-speculative-server Docker container using a pre-built image.
# It mounts the Hugging Face cache directory from the host to /hf_cache in the container.
#
# Usage: ./run.sh [DRAFT_MAX_VALUE]
# Example: ./run.sh 6
# If no argument is provided, DRAFT_MAX_VALUE defaults to 4.

# --- Path Configuration ---
# Absolute path to the Hugging Face cache directory on the HOST machine
HOST_HF_CACHE_DIR_ABS="$HOME/.cache/huggingface/hub"
# Path where the host's HF cache will be mounted INSIDE the CONTAINER
CONTAINER_HF_CACHE_MOUNT_POINT="/hf_cache"

# --- Model Paths (EDIT THESE if necessary) ---
# These paths should be the model's location INSIDE the container,
# relative to the CONTAINER_HF_CACHE_MOUNT_POINT.
TARGET_MODEL_PATH_IN_CONTAINER="/hf_cache/models--bartowski--Qwen_Qwen3-4B-GGUF/snapshots/cb76885dc66d50759b207c5a48c4e78dfa00c638/Qwen_Qwen3-4B-Q4_K_M.gguf"
DRAFT_MODEL_PATH_IN_CONTAINER="/hf_cache/models--bartowski--Qwen_Qwen3-0.6B-GGUF/snapshots/60b85c0e3d8fe0f6474f406922a26d12aca4550d/Qwen_Qwen3-0.6B-Q4_K_M.gguf"

# --- Server Configuration ---
# These values will be passed as command-line arguments to llama-server.
NGL_VALUE=0
NGLD_VALUE=999 # Maximize GPU layers for the draft model
CTX_SIZE_VALUE=2048
PARALLEL_VALUE=1
HOST_VALUE="0.0.0.0"
PORT_VALUE="8080"

# Set DRAFT_MAX_VALUE from the first script argument, or default to 4
DRAFT_MAX_VALUE=${1:-4}

# --- Sanity Check for Model Paths (Optional but Recommended) ---
if [[ "${TARGET_MODEL_PATH_IN_CONTAINER}" == */YOUR_TARGET_MODEL_RELATIVE_PATH_HERE.gguf* ]]; then
    echo "ERROR: Please edit TARGET_MODEL_PATH_IN_CONTAINER in this script with the actual model path."
    exit 1
fi
if [[ "${DRAFT_MODEL_PATH_IN_CONTAINER}" == */YOUR_DRAFT_MODEL_RELATIVE_PATH_HERE.gguf* ]]; then
    echo "ERROR: Please edit DRAFT_MODEL_PATH_IN_CONTAINER in this script with the actual model path."
    exit 1
fi

# Ensure the host cache directory exists
mkdir -p "${HOST_HF_CACHE_DIR_ABS}"

echo "Host Hugging Face cache directory: ${HOST_HF_CACHE_DIR_ABS}"
echo "Container mount point for cache: ${CONTAINER_HF_CACHE_MOUNT_POINT}"
echo "Target model path for server: ${TARGET_MODEL_PATH_IN_CONTAINER}"
echo "Draft model path for server: ${DRAFT_MODEL_PATH_IN_CONTAINER}"
echo "Using DRAFT_MAX_VALUE: ${DRAFT_MAX_VALUE}"
echo ""

# --- Run Docker Container ---
echo "Attempting to mount host cache: ${HOST_HF_CACHE_DIR_ABS} to container path: ${CONTAINER_HF_CACHE_MOUNT_POINT}"
echo "Starting Docker container with ghcr.io/ggml-org/llama.cpp:server-cuda..."

docker run --rm -it --gpus all \
    -v "${HOST_HF_CACHE_DIR_ABS}:${CONTAINER_HF_CACHE_MOUNT_POINT}" \
    -p "${PORT_VALUE}:${PORT_VALUE}" \
    ghcr.io/ggml-org/llama.cpp:server-cuda \
    -m "${TARGET_MODEL_PATH_IN_CONTAINER}" \
    -md "${DRAFT_MODEL_PATH_IN_CONTAINER}" \
    -ngl "${NGL_VALUE}" \
    -ngld "${NGLD_VALUE}" \
    -c "${CTX_SIZE_VALUE}" \
    --draft-max "${DRAFT_MAX_VALUE}" \
    --host "${HOST_VALUE}" \
    --port "${PORT_VALUE}" \
    -np "${PARALLEL_VALUE}"
    # Add any other llama-server specific flags here if needed

echo "Docker container exited."
