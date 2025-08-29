#!/usr/bin/env python3
"""
Simple GitHub Upload Script for MT4 Risk Management Calculator
This script will automatically upload all project files to your GitHub repository.
"""

import os
import sys
import subprocess
import json

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def load_config():
    """Load configuration from JSON file."""
    try:
        with open('github_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Configuration file 'github_config.json' not found")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in configuration file")
        return None

def setup_git_config(config):
    """Set up Git configuration from config file."""
    print("🔧 Setting up Git configuration...")
    
    username = config.get('github_username')
    email = config.get('github_email')
    
    if not username or not email:
        print("❌ Username and email are required in config file")
        return False
    
    # Configure Git
    run_command(f'git config user.name "{username}"')
    run_command(f'git config user.email "{email}"')
    
    print("✅ Git configuration set up successfully")
    return True

def initialize_git_repo():
    """Initialize Git repository if not already done."""
    if not os.path.exists(".git"):
        print("📁 Initializing Git repository...")
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
    print("📦 Adding files to Git...")
    
    # Add all files
    stdout, stderr, returncode = run_command("git add .")
    if returncode != 0:
        print(f"❌ Failed to add files: {stderr}")
        return False
    
    print("✅ Files added to Git")
    return True

def commit_changes(config):
    """Commit changes to Git."""
    print("💾 Committing changes...")
    
    commit_message = config.get('commit_message', 'Initial commit: MT4 Risk Management Calculator')
    
    stdout, stderr, returncode = run_command(f'git commit -m "{commit_message}"')
    if returncode != 0:
        print(f"❌ Failed to commit changes: {stderr}")
        return False
    
    print("✅ Changes committed successfully")
    return True

def setup_remote_repository(config):
    """Set up remote repository."""
    print("🌐 Setting up remote repository...")
    
    repo_url = config.get('repository_url')
    
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
    print("🚀 Pushing to GitHub...")
    
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

def main():
    """Main function to handle the upload process."""
    print("🚀 MT4 Risk Management Calculator - Simple GitHub Upload")
    print("=" * 55)
    
    # Load configuration
    config = load_config()
    if not config:
        return False
    
    # Set up Git configuration
    if not setup_git_config(config):
        return False
    
    # Initialize Git repository
    if not initialize_git_repo():
        return False
    
    # Add files to Git
    if not add_files_to_git():
        return False
    
    # Commit changes
    if not commit_changes(config):
        return False
    
    # Set up remote repository
    if not setup_remote_repository(config):
        return False
    
    # Push to GitHub
    if not push_to_github():
        return False
    
    print("\n🎉 Upload completed successfully!")
    print(f"📱 View your repository at: https://github.com/Satviksangamkar/Risk-Management-MT4")
    
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
