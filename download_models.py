# download_models.py
from huggingface_hub import hf_hub_download, snapshot_download
import os

def download_model_files(repo_id, filenames, model_type_label="Model"):
    """
    Downloads specified model files from a Hugging Face Hub repository.
    If filenames is a list, it downloads each file.
    If filenames is a single string, it downloads that one file.
    It prints local paths and snapshot information.
    """
    print(f"--- Preparing {model_type_label}: {repo_id} ---")
    
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    os.makedirs(cache_dir, exist_ok=True) # Ensure cache_dir exists

    if not isinstance(filenames, list):
        filenames = [filenames] # Make it a list if it's a single string

    first_file_relative_path = None

    for i, filename in enumerate(filenames):
        print(f"Processing file: {filename} ({i+1}/{len(filenames)})")
        try:
            downloaded_path_abs = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=cache_dir,
                local_dir_use_symlinks=False
            )
            
            print(f"  [{model_type_label} - {filename}] File downloaded/cached successfully at (absolute host path):")
            print(f"    {downloaded_path_abs}")

            if downloaded_path_abs.startswith(cache_dir):
                relative_path_in_hub = os.path.relpath(downloaded_path_abs, cache_dir)
                if i == 0: # Store the relative path of the first file
                    first_file_relative_path = relative_path_in_hub
                
                if i == 0: # Print detailed info only for the first file to avoid redundancy
                    print(f"  [{model_type_label}] Path relative to HF cache hub ('{cache_dir}'):")
                    print(f"    {relative_path_in_hub}")
                    
                    snapshot_dir_abs = os.path.dirname(downloaded_path_abs)
                    snapshot_dir_name = os.path.basename(snapshot_dir_abs)
                    model_repo_cache_folder_name = os.path.basename(os.path.dirname(snapshot_dir_abs))
                    
                    print(f"  [{model_type_label}] Snapshot directory name (hash code):")
                    print(f"    {snapshot_dir_name}")
                    print(f"  [{model_type_label}] Model's cache folder name:")
                    print(f"    {model_repo_cache_folder_name}")
                    print(f"  To use in run.sh, the path to the *first file* inside container (if mounting hub to /hf_cache) would be like:")
                    print(f"    /hf_cache/{relative_path_in_hub}") # This is the path to the current file
            
        except Exception as e:
            print(f"Error downloading {model_type_label} {repo_id}/{filename}: {e}")
            import traceback
            traceback.print_exc()
            if i == 0: return None # If first file fails, abort for this model
    
    print(f"--- Finished processing {model_type_label}: {repo_id} ---")
    return first_file_relative_path


if __name__ == "__main__":
    print("Starting model download process...\n")

    # --- Configure your models here ---

    # Small Target Model (example)
    target_model_repo_id = "bartowski/Qwen_Qwen3-4B-GGUF"
    target_model_filename = "Qwen_Qwen3-4B-Q4_K_M.gguf" 
    # download_model_files(target_model_repo_id, target_model_filename, "Small Target Model")

    # Small Draft Model (example)
    draft_model_repo_id = "bartowski/Qwen_Qwen3-0.6B-GGUF"
    draft_model_filename = "Qwen_Qwen3-0.6B-Q4_K_M.gguf"
    # download_model_files(draft_model_repo_id, draft_model_filename, "Small Draft Model")

    # --- Large Target Model (Split) ---
    large_target_model_repo_id = "lmstudio-community/Qwen3-235B-A22B-GGUF"
    large_target_model_filenames = [
        "Qwen3-235B-A22B-Q4_K_M-00001-of-00004.gguf",
        "Qwen3-235B-A22B-Q4_K_M-00002-of-00004.gguf",
        "Qwen3-235B-A22B-Q4_K_M-00003-of-00004.gguf",
        "Qwen3-235B-A22B-Q4_K_M-00004-of-00004.gguf"
    ]
    # This will download all parts and return the relative path of the FIRST file.
    first_large_target_file_rel_path = download_model_files(
        large_target_model_repo_id, 
        large_target_model_filenames, 
        "Large Target Model (Split)"
    )

    # --- Large Draft Model (Assuming it's a single file, adjust if split) ---
    # Example:
    # large_draft_model_repo_id = "NousResearch/Hermes-2-Pro-Llama-3-70B-GGUF" 
    # large_draft_model_filename = "Hermes-2-Pro-Llama-3-70B.Q4_K_M.gguf"
    # first_large_draft_file_rel_path = download_model_files(
    #     large_draft_model_repo_id,
    #     large_draft_model_filename,
    #     "Large Draft Model"
    # )
    # For now, let's assume your 30B draft model is a single file for the example:
    large_draft_model_repo_id = "bartowski/Qwen_Qwen3-30B-A3B-GGUF" # Replace with actual
    large_draft_model_filename = "Qwen_Qwen3-30B-A3B-Q6_K.gguf" # Replace with actual
    first_large_draft_file_rel_path = download_model_files(
        large_draft_model_repo_id,
        large_draft_model_filename,
        "Large Draft Model"
    )


    print("\nDownload process finished.")
    print("Please use the 'Path relative to HF cache hub' for the *first file* of each model for your run.sh script.")
    
    if first_large_target_file_rel_path:
        print(f"\nExample for TARGET_MODEL_PATH in run.sh (if mounting hub to /hf_cache):")
        print(f"  /hf_cache/{first_large_target_file_rel_path}")
    
    if first_large_draft_file_rel_path:
        print(f"Example for DRAFT_MODEL_PATH in run.sh (if mounting hub to /hf_cache):")
        print(f"  /hf_cache/{first_large_draft_file_rel_path}")

