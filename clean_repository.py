#!/usr/bin/env python3
"""
Clean Repository Script for MT4 Risk Management Calculator
This script will remove unnecessary files from the Git repository and keep only essential ones.
"""

import os
import sys
import subprocess
import shutil

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def remove_file_from_git(file_path):
    """Remove a file from Git tracking."""
    if os.path.exists(file_path):
        stdout, stderr, returncode = run_command(f'git rm "{file_path}"', check=False)
        if returncode == 0:
            print(f"✅ Removed from Git: {file_path}")
        else:
            print(f"⚠️  Could not remove from Git: {file_path} - {stderr}")
    else:
        print(f"⚠️  File not found: {file_path}")

def remove_directory_from_git(dir_path):
    """Remove a directory from Git tracking."""
    if os.path.exists(dir_path):
        stdout, stderr, returncode = run_command(f'git rm -r "{dir_path}"', check=False)
        if returncode == 0:
            print(f"✅ Removed from Git: {dir_path}")
        else:
            print(f"⚠️  Could not remove from Git: {dir_path} - {stderr}")
    else:
        print(f"⚠️  Directory not found: {dir_path}")

def clean_repository():
    """Clean the repository by removing unnecessary files."""
    print("🧹 Cleaning MT4 Risk Management Calculator Repository")
    print("=" * 55)
    
    # Files to remove from Git (but keep locally)
    files_to_remove = [
        "simple_upload.py",
        "github_config.json", 
        "run_auto_upload.bat",
        "auto_upload_to_github.py",
        "GITHUB_UPLOAD.md",
        "PROJECT_SUMMARY.md",
        "test_setup.bat",
        "upload_to_github.bat",
        "install.bat",
        "setup.py",
        "DEPLOYMENT_PACKAGE.md",
        "PROJECT_STRUCTURE.md",
        "start_mt4_app.bat",
        "test_port_5500.py",
        "FINAL_SUCCESS_REPORT.md",
        "COMPLETE_SETUP_GUIDE.md",
        "FRONTEND_SETUP.md",
        "start.bat",
        "test_server.py",
        "run_mt4_main.bat",
        "run_mt4_calculator.bat",
        "10.htm",
        "MT4_Risk_Management_Calculator.zip",
        "start_backend.bat",
        "start_frontend.bat",
        "run_frontend.bat"
    ]
    
    # Directories to remove from Git (but keep locally)
    dirs_to_remove = [
        "mt4_scraper",
        "mt4_refactored", 
        "mt4_optimized_final",
        "mt4_final",
        "uploads",
        "logs"
    ]
    
    print("\n📁 Removing unnecessary files from Git...")
    for file_path in files_to_remove:
        remove_file_from_git(file_path)
    
    print("\n📁 Removing unnecessary directories from Git...")
    for dir_path in dirs_to_remove:
        remove_directory_from_git(dir_path)
    
    # Remove __pycache__ directories from backend
    print("\n🗑️  Removing __pycache__ directories...")
    pycache_dirs = [
        "mt4_fastapi_backend/__pycache__",
        "mt4_fastapi_backend/app/__pycache__",
        "mt4_fastapi_backend/app/api/__pycache__",
        "mt4_fastapi_backend/app/core/__pycache__",
        "mt4_fastapi_backend/app/models/__pycache__",
        "mt4_fastapi_backend/app/services/__pycache__"
    ]
    
    for pycache_dir in pycache_dirs:
        if os.path.exists(pycache_dir):
            stdout, stderr, returncode = run_command(f'git rm -r "{pycache_dir}"', check=False)
            if returncode == 0:
                print(f"✅ Removed from Git: {pycache_dir}")
    
    # Remove backend test files and extra documentation
    print("\n📄 Removing extra backend files...")
    backend_files_to_remove = [
        "mt4_fastapi_backend/test_server.py",
        "mt4_fastapi_backend/run.py",
        "mt4_fastapi_backend/API_DOCUMENTATION.md",
        "mt4_fastapi_backend/FUNCTION_REFERENCE.md"
    ]
    
    for file_path in backend_files_to_remove:
        remove_file_from_git(file_path)
    
    # Remove backend directories that are not essential
    backend_dirs_to_remove = [
        "mt4_fastapi_backend/uploads",
        "mt4_fastapi_backend/logs"
    ]
    
    for dir_path in backend_dirs_to_remove:
        remove_directory_from_git(dir_path)
    
    print("\n✅ Repository cleaning completed!")
    return True

def commit_cleanup():
    """Commit the cleanup changes."""
    print("\n💾 Committing cleanup changes...")
    
    # Add all changes
    stdout, stderr, returncode = run_command("git add .")
    if returncode != 0:
        print(f"❌ Failed to add changes: {stderr}")
        return False
    
    # Commit changes
    stdout, stderr, returncode = run_command('git commit -m "Clean repository: Remove unnecessary files and keep only essential components"')
    if returncode != 0:
        print(f"❌ Failed to commit changes: {stderr}")
        return False
    
    print("✅ Cleanup changes committed successfully!")
    return True

def push_cleanup():
    """Push the cleanup changes to GitHub."""
    print("\n🚀 Pushing cleanup to GitHub...")
    
    stdout, stderr, returncode = run_command("git push origin master")
    if returncode != 0:
        # Try main branch if master fails
        print("⚠️  Master branch failed, trying main branch...")
        stdout, stderr, returncode = run_command("git push origin main")
        if returncode != 0:
            print(f"❌ Failed to push to GitHub: {stderr}")
            return False
    
    print("✅ Cleanup pushed to GitHub successfully!")
    return True

def show_final_structure():
    """Show the final repository structure."""
    print("\n📋 Final Repository Structure:")
    print("=" * 40)
    
    essential_files = [
        "README.md",
        "LICENSE", 
        ".gitignore",
        "mt4_fastapi_backend/main.py",
        "mt4_fastapi_backend/requirements.txt",
        "mt4_fastapi_backend/README.md",
        "mt4_frontend/index.html",
        "mt4_frontend/styles.css",
        "mt4_frontend/script.js",
        "mt4_frontend/README.md"
    ]
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
    
    print("\n📁 Essential Directories:")
    essential_dirs = [
        "mt4_fastapi_backend/app/",
        "mt4_frontend/"
    ]
    
    for dir_path in essential_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} (missing)")

def main():
    """Main function to clean the repository."""
    print("🚀 MT4 Risk Management Calculator - Repository Cleanup")
    print("=" * 60)
    
    # Clean the repository
    if not clean_repository():
        print("❌ Repository cleaning failed!")
        return False
    
    # Commit the cleanup
    if not commit_cleanup():
        print("❌ Failed to commit cleanup!")
        return False
    
    # Push to GitHub
    if not push_cleanup():
        print("❌ Failed to push cleanup!")
        return False
    
    # Show final structure
    show_final_structure()
    
    print("\n🎉 Repository cleanup completed successfully!")
    print("📱 Your GitHub repository now contains only essential files.")
    print("🔗 View your clean repository at: https://github.com/Satviksangamkar/Risk-Management-MT4")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Repository cleanup failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
