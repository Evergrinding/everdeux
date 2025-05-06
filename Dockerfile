# --- Base Image ---
# Using Ubuntu 22.04 LTS base image with CUDA 12.5.1 for stability.
FROM nvidia/cuda:12.5.1-devel-ubuntu22.04

# --- Environment Variables ---
# Set non-interactive frontend for package installations
ENV DEBIAN_FRONTEND=noninteractive
# Default paths for models *inside* the container.
ENV TARGET_MODEL_PATH="/models/target_model.gguf"
ENV DRAFT_MODEL_PATH="/models/draft_model.gguf"
# Default GPU layer offloading
ENV NGL=0
ENV NGLD=999
# Default context size
ENV CTX_SIZE=2048
# Default tuned draft length
ENV DRAFT_MAX=4
# Default server host and port
ENV HOST="0.0.0.0"
ENV PORT=8080
# Default server concurrency
ENV PARALLEL=1

# --- Install Dependencies ---
# Update package lists and install build tools, git, libcurl, ninja, and coreutils.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    build-essential \
    libcurl4-openssl-dev \
    ninja-build \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Add CUDA library paths (including stubs) to the system's dynamic linker configuration
# for the build process. The NVIDIA Container Toolkit should manage this at runtime.
# This ensures that the linker can find libcuda.so (stub for libcuda.so.1) during build.
RUN echo "/usr/local/cuda/lib64/stubs" > /etc/ld.so.conf.d/00-cuda-stubs.conf && \
    echo "/usr/local/cuda/lib64" >> /etc/ld.so.conf.d/00-cuda-stubs.conf && \
    ldconfig

# --- Clone and Build llama.cpp ---
# Set working directory
WORKDIR /app

# Clone the llama.cpp repository and checkout the specified commit.
RUN git clone https://github.com/ggerganov/llama.cpp.git && \
    cd llama.cpp && \
    git checkout b5289 # Retaining user's specified commit

# Build llama.cpp with CUDA support
WORKDIR /app/llama.cpp
# Create a build directory and build the project.
# The LD_LIBRARY_PATH for the build step will implicitly use paths configured by ldconfig
# and those inherent to the nvidia/cuda base image.
RUN mkdir build && cd build && \
    # Configure CMake:
    cmake .. \
        -G Ninja \
        -DLLAMA_CUDA=ON \
        -DLLAMA_CUDA_FORCE_MMQ=ON \
        -DCMAKE_CUDA_ARCHITECTURES="89;90" && \
    # Build the project using all available CPU cores (nproc).
    cmake --build . --config Release -j $(nproc)

# --- Runtime Configuration ---
# Expose the default server port
EXPOSE ${PORT}

# Set the working directory for the entrypoint (where the server executable is)
WORKDIR /app/llama.cpp/build/bin

# --- Entrypoint ---
# Define the command to run when the container starts.
# Modified to echo the command, arguments, and LD_LIBRARY_PATH before execution for debugging.
ENTRYPOINT ["sh", "-c", "echo '--- Debug: Effective command to be run: ---' && \
            echo \"./llama-server -m '${TARGET_MODEL_PATH}' -md '${DRAFT_MODEL_PATH}' -ngl '${NGL}' -ngld '${NGLD}' -c '${CTX_SIZE}' --draft-max '${DRAFT_MAX}' --host '${HOST}' --port '${PORT}' -np '${PARALLEL}'\" && \
            echo '--- Debug: LD_LIBRARY_PATH at runtime: ---' && \
            echo \"${LD_LIBRARY_PATH}\" && \
            echo '--- End Debug ---' && \
            exec ./llama-server \
            -m \"${TARGET_MODEL_PATH}\" \
            -md \"${DRAFT_MODEL_PATH}\" \
            -ngl \"${NGL}\" \
            -ngld \"${NGLD}\" \
            -c \"${CTX_SIZE}\" \
            --draft-max \"${DRAFT_MAX}\" \
            --host \"${HOST}\" \
            --port \"${PORT}\" \
            -np \"${PARALLEL}\" \
            "]
# Add any other default flags for the server here.
