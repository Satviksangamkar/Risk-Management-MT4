#!/usr/bin/env python3
"""
Automatic GitHub Upload Script for MT4 Risk Management Calculator
This script will automatically upload all project files to your GitHub repository.
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def check_git_installed():
    """Check if Git is installed."""
    stdout, stderr, returncode = run_command("git --version", check=False)
    if returncode != 0:
        print("❌ Git is not installed. Please install Git first:")
        print("   Download from: https://git-scm.com/downloads")
        return False
    print(f"✅ Git is installed: {stdout}")
    return True

def check_github_repo_exists(repo_url):
    """Check if the GitHub repository exists."""
    try:
        response = requests.get(f"https://api.github.com/repos/Satviksangamkar/Risk-Management-MT4")
        if response.status_code == 200:
            print("✅ GitHub repository exists")
            return True
        else:
            print("❌ GitHub repository does not exist or is not accessible")
            print(f"   Please create the repository at: {repo_url}")
            return False
    except Exception as e:
        print(f"❌ Error checking repository: {e}")
        return False

def setup_git_config():
    """Set up Git configuration."""
    print("\n🔧 Setting up Git configuration...")
    
    # Get user input for Git configuration
    username = input("Enter your GitHub username: ").strip()
    email = input("Enter your GitHub email: ").strip()
    
    if not username or not email:
        print("❌ Username and email are required")
        return False
    
    # Configure Git
    run_command(f'git config user.name "{username}"')
    run_command(f'git config user.email "{email}"')
    
    print("✅ Git configuration set up successfully")
    return True

def initialize_git_repo():
    """Initialize Git repository if not already done."""
    if not os.path.exists(".git"):
        print("\n📁 Initializing Git repository...")
        stdout, stderr, returncode = run_command("git init")
        if returncode != 0:
            print(f"❌ Failed to initialize Git repository: {stderr}")
            return False
        print("✅ Git repository initialized")
    else:
        print("✅ Git repository already exists")
    return True

def add_files_to_git():
    """Add all files to Git."""
    print("\n📦 Adding files to Git...")
    
    # Add all files
    stdout, stderr, returncode = run_command("git add .")
    if returncode != 0:
        print(f"❌ Failed to add files: {stderr}")
        return False
    
    # Check what files were added
    stdout, stderr, returncode = run_command("git status --porcelain")
    if returncode == 0 and stdout:
        print("📋 Files to be committed:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("⚠️  No new files to commit")
    
    print("✅ Files added to Git")
    return True

def commit_changes():
    """Commit changes to Git."""
    print("\n💾 Committing changes...")
    
    commit_message = input("Enter commit message (or press Enter for default): ").strip()
    if not commit_message:
        commit_message = "Initial commit: MT4 Risk Management Calculator with comprehensive documentation"
    
    stdout, stderr, returncode = run_command(f'git commit -m "{commit_message}"')
    if returncode != 0:
        print(f"❌ Failed to commit changes: {stderr}")
        return False
    
    print("✅ Changes committed successfully")
    return True

def setup_remote_repository():
    """Set up remote repository."""
    print("\n🌐 Setting up remote repository...")
    
    repo_url = "https://github.com/Satviksangamkar/Risk-Management-MT4.git"
    
    # Remove existing remote if any
    run_command("git remote remove origin", check=False)
    
    # Add remote repository
    stdout, stderr, returncode = run_command(f'git remote add origin {repo_url}')
    if returncode != 0:
        print(f"❌ Failed to add remote repository: {stderr}")
        return False
    
    print("✅ Remote repository configured")
    return True

def push_to_github():
    """Push changes to GitHub."""
    print("\n🚀 Pushing to GitHub...")
    
    # Try to push to master branch
    stdout, stderr, returncode = run_command("git push -u origin master")
    if returncode != 0:
        # If master fails, try main branch
        print("⚠️  Master branch failed, trying main branch...")
        stdout, stderr, returncode = run_command("git push -u origin main")
        if returncode != 0:
            print(f"❌ Failed to push to GitHub: {stderr}")
            print("\n🔧 Troubleshooting tips:")
            print("   1. Make sure you have access to the repository")
            print("   2. Use a personal access token instead of password")
            print("   3. Create token at: https://github.com/settings/tokens")
            return False
    
    print("✅ Successfully pushed to GitHub!")
    return True

def verify_upload():
    """Verify the upload was successful."""
    print("\n🔍 Verifying upload...")
    
    try:
        response = requests.get("https://api.github.com/repos/Satviksangamkar/Risk-Management-MT4/contents")
        if response.status_code == 200:
            files = response.json()
            print(f"✅ Repository contains {len(files)} files")
            
            # Check for key files
            key_files = ["README.md", "LICENSE", "mt4_fastapi_backend/main.py", "mt4_frontend/index.html"]
            found_files = [f["name"] for f in files]
            
            print("📋 Key files found:")
            for file in key_files:
                if file in found_files:
                    print(f"   ✅ {file}")
                else:
                    print(f"   ❌ {file}")
            
            return True
        else:
            print(f"❌ Failed to verify upload: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verifying upload: {e}")
        return False

def main():
    """Main function to handle the upload process."""
    print("🚀 MT4 Risk Management Calculator - Automatic GitHub Upload")
    print("=" * 60)
    
    # Check prerequisites
    if not check_git_installed():
        return False
    
    repo_url = "https://github.com/Satviksangamkar/Risk-Management-MT4"
    if not check_github_repo_exists(repo_url):
        return False
    
    # Set up Git configuration
    if not setup_git_config():
        return False
    
    # Initialize Git repository
    if not initialize_git_repo():
        return False
    
    # Add files to Git
    if not add_files_to_git():
        return False
    
    # Commit changes
    if not commit_changes():
        return False
    
    # Set up remote repository
    if not setup_remote_repository():
        return False
    
    # Push to GitHub
    if not push_to_github():
        return False
    
    # Verify upload
    if not verify_upload():
        print("⚠️  Upload verification failed, but files may still be uploaded")
    
    print("\n🎉 Upload completed successfully!")
    print(f"📱 View your repository at: {repo_url}")
    print("\n📋 Next steps:")
    print("   1. Visit your repository to verify all files are uploaded")
    print("   2. Add a description and topics to your repository")
    print("   3. Share the repository link with others")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Upload failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
