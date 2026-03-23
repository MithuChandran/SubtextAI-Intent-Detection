import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    print("Error: huggingface_hub is not installed. Run: pip install huggingface_hub")
    sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skill: Upload Model to Hugging Face Hub")
    parser.add_argument("--model", type=str, required=True, help="Local path to model directory (e.g., models/arch_weighted)")
    parser.add_argument("--repo", type=str, required=True, help="Hugging Face Repo ID (e.g., username/model-name)")
    parser.add_argument("--private", action="store_true", help="Make the repo private")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model):
        print(f"Error: Model directory {args.model} not found.")
        sys.exit(1)
        
    api = HfApi()
    
    print(f"Creating/Checking repo {args.repo}...")
    try:
        create_repo(args.repo, private=args.private, exist_ok=True)
    except Exception as e:
        print(f"Error creating repo: {e}")
        print("Tip: Make sure you are logged in with 'huggingface-cli login'")
        sys.exit(1)
        
    print(f"Uploading {args.model} to {args.repo}...")
    try:
        api.upload_folder(
            folder_path=args.model,
            repo_id=args.repo,
            repo_type="model"
        )
        print(f"\nSuccess! Model uploaded to: https://huggingface.co/{args.repo}")
    except Exception as e:
        print(f"Error uploading: {e}")
        sys.exit(1)
