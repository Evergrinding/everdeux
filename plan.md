## Plan for Deploying Speculative Decoding Setup to GCP A3 VM

This plan outlines the steps to take your current local setup (scripts and workflow) and deploy it to a Google Cloud Platform (GCP) A3 Virtual Machine for testing with large language models.

**Phase 1: Prepare Your Local Repository for GitHub**

Your `~/everwise/everdeux` directory is already a Git repository. Let's ensure it's clean and contains everything needed.

1.  **Update `.gitignore`:**
    * Make sure your local Python virtual environment (`.venv/`) and any other local-only files/directories are ignored. The Hugging Face cache (`~/.cache/huggingface/hub` or specific model files if you copied them locally) should *not* be committed.
    * Your current `.gitignore` (3443 bytes) might already cover `.venv/`. Verify or add it:
        ```
        # .gitignore
        .venv/
        __pycache__/
        *.pyc
        *.pyo
        *.pyd
        # Add any other local files/directories to ignore
        ```

2.  **Review Files for Commit:**
    * **Essential Scripts:**
        * `download_models.py`: To download models on the A3 VM and get their cache paths.
        * `run.sh` (the one from the immersive artifact `simplified_run_sh` or your latest working version): To run the Docker container.
        * `test.sh` & `test2.sh`: Your curl scripts for testing the server.
    * **Configuration/Reference:**
        * `Dockerfile` (the one we were working on for custom builds, currently `dockerfile_ninja_multicore`): While you're currently using a pre-built image, keeping this Dockerfile in the repo is good for reference or if you decide to build a custom image later.
        * `LICENSE`
        * Your project plan/notes (if you have them in text files).
    * **Do NOT commit large model files.**

3.  **Commit and Push to GitHub:**
    * Stage your changes: `git add .`
    * Commit: `git commit -m "Prepare scripts and configuration for GCP A3 VM deployment"`
    * Push to your remote GitHub repository (create one on GitHub.com if you haven't already for this project).

**Phase 2: Set Up the GCP A3 VM**

1.  **Create the A3 VM Instance:**
    * In the GCP Console, navigate to "Compute Engine" > "VM instances".
    * Click "Create Instance".
    * **Machine Type:** Select an A3 series machine type (e.g., `a3-highgpu-1g` for 1 H100 GPU, or larger if your 30B draft model needs more VRAM). Start with the smallest suitable A3 to manage costs. Consider Spot VMs for cost savings during testing, but be aware they can be preempted.
    * **Boot Disk:**
        * Choose an OS. A "Deep Learning VM Image" (Debian or Ubuntu based) is highly recommended as it comes with NVIDIA drivers, CUDA Toolkit, Docker, and the NVIDIA Container Toolkit pre-installed. This will save significant setup time.
        * If using a standard Linux distro, you'll need to install these manually.
        * Ensure sufficient disk space for your OS, tools, cloned repo, and the large models in the Hugging Face cache (235B + 30B models will require hundreds of GBs).
    * **Firewall:** Allow HTTP traffic if you want to test the server from outside the VM (e.g., port 8080).
    * **Service Account/Permissions:** Ensure the VM has permissions to access any necessary GCP services (e.g., Cloud Storage if you plan to store models there, though caching directly on the VM's persistent disk is also fine).

2.  **Initial VM Setup (if *not* using a Deep Learning VM image):**
    * SSH into your new A3 VM.
    * **Install NVIDIA Drivers:** Follow GCP documentation for A3 instances.
    * **Install CUDA Toolkit:** Match the version compatible with the `llama.cpp` pre-built image or your intended build.
    * **Install Docker and NVIDIA Container Toolkit:** Essential for running GPU-accelerated containers. Follow official Docker and NVIDIA documentation.
    * **Install Git:** `sudo apt update && sudo apt install git -y`

3.  **Install Python and `huggingface_hub` (if needed):**
    * Python 3 and `pip` should be available on most modern Linux images, especially Deep Learning VM images.
    * If `huggingface_hub` (for `download_models.py`) or `huggingface-cli` is not pre-installed on the Deep Learning VM:
        * Try a user install first: `pip3 install --user huggingface_hub`
        * If that fails due to "externally-managed-environment" (less common on fresh cloud VMs but possible), you might need to install `python3-venv` (`sudo apt install python3-venv -y`) and set up a virtual environment on the VM as you did locally, or install `pipx`.
        * The goal is to be able to run `download_models.py` or `huggingface-cli download`.

**Phase 3: Deploy and Configure on the A3 VM**

1.  **Clone Your Repository:**
    * SSH into your A3 VM.
    * Clone your GitHub repository: `git clone <your-github-repo-url>`
    * `cd` into the cloned directory (e.g., `cd everdeux`).

2.  **Download the Large Models:**
    * Navigate to your cloned repository directory on the VM.
    * **Modify `download_models.py`:**
        * Update the `target_model_repo_id`, `target_model_filename`, `draft_model_repo_id`, and `draft_model_filename` variables to point to your large Qwen models (e.g., Qwen3-235B and Qwen3-30B). **Ensure you have the correct Hugging Face repository IDs and exact GGUF filenames for these large models.**
    * **Run the downloader script:**
        * If you set up a venv on the VM: `source .venv/bin/activate` (if you created one named `.venv`)
        * `python3 download_models.py`
    * This will download the large models into the A3 VM's `~/.cache/huggingface/hub` and print their paths. Note these paths carefully.
    * Alternatively, if `huggingface-cli` is available and preferred, use `huggingface-cli download <repo_id> <filename>` for each large model.

3.  **Configure `run.sh` for Large Models:**
    * Open `run.sh` (the one based on `simplified_run_sh`) on the A3 VM using a text editor (e.g., `nano run.sh` or `vim run.sh`).
    * **Update Model Paths:**
        * Modify `TARGET_MODEL_PATH_IN_CONTAINER`: Use the path information from `download_models.py` (or your manual check if using `huggingface-cli`). It will look like `/hf_cache/<path-within-hub-to-235B-model.gguf>`.
        * Modify `DRAFT_MODEL_PATH_IN_CONTAINER`: Similarly, update this for your 30B draft model.
    * **Update GPU Layer Allocation (Crucial for Large Models):**
        * `NGL_VALUE=0`: Keep this for the 235B target model to run on CPU.
        * `NGLD_VALUE=999`: Keep this to try and offload all layers of the 30B draft model to the H100 GPU. Monitor VRAM usage carefully.
    * **Context Size (`CTX_SIZE_VALUE`):** You might need to adjust this based on the capabilities of the large models and available system RAM/VRAM. Start with your current `2048` and adjust if needed.
    * **Draft Max (`DRAFT_MAX_VALUE`):** Start with the value you found optimal locally (e.g., 6 or whatever you determined). You'll likely need to re-tune this for the large models.

**Phase 4: Run and Test on the A3 VM**

1.  **Execute `run.sh`:**
    * Make sure it's executable: `chmod +x run.sh`
    * Run it: `./run.sh` (you can pass a `DRAFT_MAX_VALUE` as an argument, e.g., `./run.sh 6`)

2.  **Monitor Resources:**
    * While the server is starting and running, use `htop` (for CPU/RAM) and `nvidia-smi` (for GPU VRAM/utilization) in another SSH session to monitor resource usage.
    * Ensure the 235B model fits in system RAM and the 30B draft model (plus its KV cache) fits in GPU VRAM.

3.  **Test with `curl`:**
    * Use your `test.sh` and `test2.sh` scripts (you might need to `chmod +x` them too) from another SSH session on the A3 VM, or from your local machine if you've configured firewall rules and know the A3 VM's external IP.
    * `./test.sh`
    * `./test2.sh`
    * Observe the server logs and the `curl` responses.

4.  **Benchmark and Tune:**
    * Systematically test different `DRAFT_MAX_VALUE` settings with the large models to find the optimal balance of acceptance rate and tokens/second.
    * Compare performance against a baseline without speculative decoding (if feasible to run the 235B model alone).

**Phase 5: Cost Management**

* **A3 VMs are expensive.**
* **STOP or DELETE your A3 VM instance when you are not actively using it.**
* Monitor your GCP billing closely.
* Consider using GCP's tools for budget alerts.