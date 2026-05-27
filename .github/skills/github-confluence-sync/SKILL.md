---
name: github-confluence-sync
description: "Use when: syncing GitHub file changes to Jira Confluence pages. Automatically creates or updates Confluence pages based on file modifications in your GitHub repository."
---

# GitHub to Confluence Sync

Automatically create and update Jira Confluence pages based on changes in your GitHub repository.

## Overview

This skill monitors a GitHub repository for file changes and synchronizes them to Jira Confluence pages. Each modified file in the repository creates or updates a corresponding page in your Confluence space.

## How It Works

1. **Provide GitHub Repository**: Enter the URL of your GitHub repository
2. **Fetch Changes**: The skill retrieves recent file changes from the repository
3. **Parse Content**: Extracts content from modified files
4. **Sync to Confluence**: Creates or updates pages in the target Confluence space with the file content and metadata

## Usage

Invoke this skill in chat with:
```
/github-confluence-sync <github-repo-url>
```

### Example

```
/github-confluence-sync https://github.com/Vijay771-azure/devops-first-repo
```

## Required Configuration

Before using this skill, ensure you have:

- **GitHub Token**: Set environment variable `GITHUB_TOKEN` for repository access
- **Confluence Token**: Set environment variable `CONFLUENCE_TOKEN` for API access
- **Confluence Base URL**: Set environment variable `CONFLUENCE_BASE_URL` (e.g., `https://your-domain.atlassian.net`)
- **Confluence Space Key**: Set environment variable `CONFLUENCE_SPACE_KEY` for the target space

## What Gets Synced

- **File Changes**: All modified files in the repository
- **Content**: File content becomes the page content in Confluence
- **Metadata**: File names, paths, and timestamps are preserved as page properties
- **Status**: Pages are tagged with sync status and last update time

## Limitations

- Only syncs files that have been modified
- Large files (>20MB) are skipped for performance
- Binary files are logged but not synced to Confluence
- Requires proper authentication to both GitHub and Confluence
