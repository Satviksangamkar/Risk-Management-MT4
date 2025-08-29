# 🚀 GitHub Upload Instructions

This document provides step-by-step instructions for uploading the MT4 Risk Management Calculator to your GitHub repository.

## 📋 Prerequisites

Before uploading to GitHub, ensure you have:

1. **Git installed** on your computer
   - Download from: https://git-scm.com/downloads
   - Verify with: `git --version`

2. **GitHub account** created
   - Sign up at: https://github.com/signup
   - Remember your username and password

3. **Repository created** on GitHub
   - The repository should be: https://github.com/Satviksangamkar/Risk-Management-MT4

## 🔄 Automatic Upload Method

The easiest way to upload is using the provided script:

1. **Run the test script** to verify your setup:
   ```
   test_setup.bat
   ```

2. **Run the upload script**:
   ```
   upload_to_github.bat
   ```

3. **Follow the prompts**:
   - Enter your GitHub username
   - Enter your GitHub email
   - Enter a commit message (or use the default)

4. **Enter your GitHub credentials** when prompted
   - You might need to use a personal access token instead of password
   - Create one at: https://github.com/settings/tokens

5. **Verify the upload** by visiting your repository:
   - https://github.com/Satviksangamkar/Risk-Management-MT4

## 🔧 Manual Upload Method

If you prefer to upload manually or the script doesn't work:

1. **Initialize Git repository**:
   ```
   git init
   ```

2. **Configure Git**:
   ```
   git config user.name "YourUsername"
   git config user.email "your.email@example.com"
   ```

3. **Add all files**:
   ```
   git add .
   ```

4. **Commit changes**:
   ```
   git commit -m "Initial commit of MT4 Risk Management Calculator"
   ```

5. **Add remote repository**:
   ```
   git remote add origin https://github.com/Satviksangamkar/Risk-Management-MT4.git
   ```

6. **Push to GitHub**:
   ```
   git push -u origin master
   ```

## 🔍 Troubleshooting

### Authentication Issues

If you see "Authentication failed":
- Use a personal access token instead of your password
- Create one at: https://github.com/settings/tokens
- Select at least the "repo" scope

### Permission Issues

If you see "Permission denied":
- Ensure you're the owner of the repository
- Check that the repository name is correct
- Verify your GitHub credentials

### Push Rejected

If your push is rejected:
- Try pulling first: `git pull origin master --allow-unrelated-histories`
- Resolve any conflicts
- Then push again: `git push -u origin master`

## 📱 After Uploading

Once your code is uploaded:

1. **Enable GitHub Pages** (optional):
   - Go to repository Settings > Pages
   - Select "master" branch and "/docs" folder
   - Click "Save"

2. **Add repository description**:
   - Go to repository main page
   - Click "Edit" button next to About section
   - Add a short description and topics

3. **Create a release** (optional):
   - Go to "Releases" section
   - Click "Create a new release"
   - Tag version as "v1.0.0"
   - Add release notes

## 🤝 Sharing Your Repository

Share your repository with others:
- Copy the URL: https://github.com/Satviksangamkar/Risk-Management-MT4
- Send it via email, messaging apps, or social media

## 🔄 Updating Your Repository

To update your repository later:

1. Make your changes to the code
2. Run the upload script again:
   ```
   upload_to_github.bat
   ```
3. Or manually update:
   ```
   git add .
   git commit -m "Update description"
   git push
   ```
