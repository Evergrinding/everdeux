# download_models.py
from huggingface_hub import hf_hub_download
import os

def download_and_get_info(repo_id, filename, model_type_label="Model"):
    """
    Downloads a model from Hugging Face Hub and prints its local path
    and the snapshot directory name.
    """
    print(f"--- Preparing {model_type_label}: {repo_id}/{filename} ---")
    
    # Define the standard Hugging Face cache directory
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    
    try:
        downloaded_path_abs = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            cache_dir=cache_dir,
            local_dir_use_symlinks=False  # Recommended for compatibility
        )
        
        print(f"[{model_type_label}] File downloaded/cached successfully at (absolute host path):")
        print(f"  {downloaded_path_abs}")

        # Determine the path relative to the 'hub' directory
        # This helps in constructing paths for Docker if mounting the 'hub' directory
        if downloaded_path_abs.startswith(cache_dir):
            relative_path_in_hub = os.path.relpath(downloaded_path_abs, cache_dir)
            print(f"[{model_type_label}] Path relative to HF cache hub ('{cache_dir}'):")
            print(f"  {relative_path_in_hub}")

            # Extract the snapshot directory (the "hash code" you mentioned)
            # The structure is usually: models--<user>--<repo>/snapshots/<hash>/<filename>
            # So, we want the parent of the filename, which is the snapshot directory.
            snapshot_dir_abs = os.path.dirname(downloaded_path_abs)
            snapshot_dir_name = os.path.basename(snapshot_dir_abs)
            
            # The path part before the snapshot would be like models--<user>--<repo>/snapshots
            model_repo_cache_folder_name = os.path.basename(os.path.dirname(snapshot_dir_abs)) # e.g. models--bartowski--Qwen_Qwen3-4B-GGUF
            
            print(f"[{model_type_label}] Snapshot directory name (hash code):")
            print(f"  {snapshot_dir_name}")
            print(f"[{model_type_label}] Model's cache folder name:")
            print(f"  {model_repo_cache_folder_name}")
            print(f"To use in run.sh, the path inside container (if mounting hub to /hf_cache) would be like:")
            print(f"  /hf_cache/{model_repo_cache_folder_name}/snapshots/{snapshot_dir_name}/{filename}")
            print("-" * 30)
            return relative_path_in_hub # Return the path relative to the hub for easy use
            
    except Exception as e:
        print(f"Error downloading {model_type_label} {repo_id}/{filename}: {e}")
        import traceback
        traceback.print_exc()
        print("-" * 30)
        return None

if __name__ == "__main__":
    print("Starting model download process...\n")

    # --- Configure your models here ---
    target_model_repo_id = "bartowski/Qwen_Qwen3-4B-GGUF"
    target_model_filename = "Qwen_Qwen3-4B-Q4_K_M.gguf"

    draft_model_repo_id = "bartowski/Qwen_Qwen3-0.6B-GGUF"
    draft_model_filename = "Qwen_Qwen3-0.6B-Q4_K_M.gguf"
    
    # For your large models (example, replace with actual IDs and filenames)
    # target_large_model_repo_id = "Qwen/Qwen2-235B-A22B-GGUF" # Fictional, replace
    # target_large_model_filename = "qwen2-235b-a22b.q4_k_m.gguf" # Fictional, replace
    # draft_large_model_repo_id = "Qwen/Qwen2-30B-A3B-GGUF" # Fictional, replace
    # draft_large_model_filename = "qwen2-30b-a3b.q4_k_m.gguf" # Fictional, replace

    # Download Target Model
    target_rel_path = download_and_get_info(target_model_repo_id, target_model_filename, "Target Model")
    
    # Download Draft Model
    draft_rel_path = download_and_get_info(draft_model_repo_id, draft_model_filename, "Draft Model")

    # Example for large models (uncomment and configure when ready)
    # download_and_get_info(target_large_model_repo_id, target_large_model_filename, "Large Target Model")
    # download_and_get_info(draft_large_model_repo_id, draft_large_model_filename, "Large Draft Model")

    print("\nDownload process finished.")
    print("Please use the 'Path relative to HF cache hub' or construct the path using the snapshot hash for your run.sh script.")
    if target_rel_path:
        print(f"\nExample for TARGET_MODEL_PATH in run.sh (if mounting hub to /hf_cache): /hf_cache/{target_rel_path}")
    if draft_rel_path:
        print(f"Example for DRAFT_MODEL_PATH in run.sh (if mounting hub to /hf_cache): /hf_cache/{draft_rel_path}")

