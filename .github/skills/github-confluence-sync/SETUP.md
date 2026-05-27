# GitHub to Confluence Sync - Setup Guide

## Prerequisites

- Python 3.8+
- GitHub Personal Access Token
- Jira Confluence API Token
- Access to a Confluence space

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### 1. GitHub Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Create a new token with `repo` scope (read access)
3. Copy the token (you'll need this in the next step)

### 2. Confluence Token

1. Go to Jira Cloud → Your Profile → Account settings → Security
2. Create an API token
3. Copy the token (you'll need this in the next step)

### 3. Create `.env` File

Create a `.env` file in the project root with your tokens:

```bash
GITHUB_TOKEN="<your_github_token_here>"
CONFLUENCE_TOKEN="<your_confluence_token_here>"
CONFLUENCE_BASE_URL="https://your-domain.atlassian.net"
CONFLUENCE_SPACE_KEY="<your_space_key>"
```

Replace:
- `<your_github_token_here>` — Your GitHub Personal Access Token
- `<your_confluence_token_here>` — Your Jira Confluence API Token
- `https://your-domain.atlassian.net` — Your Confluence base URL
- `<your_space_key>` — Your Confluence space key (e.g., `MYSPACE`)

### 4. Secure the `.env` File

**IMPORTANT**: Make sure `.env` is in your `.gitignore`:

```bash
# Check if .gitignore exists
cat .gitignore

# Add .env if not already there
echo ".env" >> .gitignore
```

**Never commit `.env` to version control!** This file contains sensitive credentials.

## Usage

### Command Line

```bash
python sync.py https://github.com/owner/repository
```

### From Copilot Chat

Invoke the skill using:
```
/github-confluence-sync https://github.com/owner/repository
```

## What Gets Synced

- **Text files** only (markdown, code, config files, etc.)
- **Recent commits** (last 3 commits by default)
- **Modified and added files** (deleted files are skipped)
- **File metadata** (timestamps, paths)

## Binary Files

Binary files (images, PDFs, executables) are logged but not synced to Confluence.

## Troubleshooting

### Authentication Errors

- Verify `GITHUB_TOKEN` has `repo` scope
- Verify `CONFLUENCE_TOKEN` is valid and not expired
- Check that tokens are correctly set in environment

### Page Creation Fails

- Ensure `CONFLUENCE_SPACE_KEY` is correct
- Verify you have write permissions in the Confluence space
- Check that `CONFLUENCE_BASE_URL` is correct (no trailing slash)

### Rate Limiting

GitHub API has rate limits (60 requests/hour for unauthenticated, 5000/hour for authenticated).
If you hit limits, wait before retrying.

## Limitations

- Large files (>20MB) are skipped
- Binary files are not synced
- Requires proper authentication
- Confluence page titles are based on filenames
