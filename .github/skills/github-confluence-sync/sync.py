#!/usr/bin/env python3
"""
GitHub to Confluence Sync Script
Syncs file changes from GitHub repository to Jira Confluence pages
"""


import sys
import json
import requests
import base64
from datetime import datetime
from urllib.parse import urlparse
import argparse
from dotenv import load_dotenv
import os
load_dotenv()  # this loads .env variables


class GitHubConfluenceSync:
    """Sync GitHub file changes to Confluence pages"""
    
    def __init__(self):
        self.github_token = os.getenv('MY_GITHUB_TOKEN')
        self.confluence_token = os.getenv('CONFLUENCE_TOKEN')
        self.confluence_base_url = os.getenv('CONFLUENCE_BASE_URL')
        self.confluence_space_key = os.getenv('CONFLUENCE_SPACE_KEY')
        self.confluence_email = os.getenv('CONFLUENCE_EMAIL')
        self.confluence_space_id = os.getenv('CONFLUENCE_SPACE_ID')
        
        if not all([self.github_token, self.confluence_token, self.confluence_base_url, self.confluence_space_key]):
            raise ValueError(
                "Missing required environment variables:\n"
                "  - GITHUB_TOKEN\n"
                "  - CONFLUENCE_TOKEN\n"
                "  - CONFLUENCE_BASE_URL\n"
                "  - CONFLUENCE_SPACE_KEY\n"
                "Optional (for authentication):\n"
                "  - CONFLUENCE_EMAIL (for Basic Auth)\n"
                "  - CONFLUENCE_SPACE_ID (use this instead of space key)"
            )
    
    def get_auth_headers(self):
        """Create authentication headers for Confluence API"""
        if self.confluence_email:
            # Use Basic Auth (email:token) for Confluence Cloud
            auth_str = base64.b64encode(
                f"{self.confluence_email}:{self.confluence_token}".encode()
            ).decode()
            return {
                'Authorization': f'Basic {auth_str}',
                'Content-Type': 'application/json'
            }
        else:
            # Fallback to Bearer token
            return {
                'Authorization': f'Bearer {self.confluence_token}',
                'Content-Type': 'application/json'
            }
    
    def get_space_id(self):
        """Get space ID from space key if not provided"""
        if self.confluence_space_id:
            return self.confluence_space_id
        
        headers = self.get_auth_headers()
        try:
            response = requests.get(
                f"{self.confluence_base_url}/wiki/api/v2/spaces",
                headers=headers,
                params={'keys': self.confluence_space_key, 'limit': 1}
            )
            response.raise_for_status()
            spaces = response.json().get('results', [])
            if spaces:
                return spaces[0]['id']
        except requests.RequestException as e:
            print(f"Warning: Could not fetch space ID: {e}")
        
        return None
    
    def parse_github_url(self, repo_url):
        """Parse GitHub repository URL to extract owner and repo"""
        # Remove .git if present
        repo_url = repo_url.rstrip('/')
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        # Extract owner and repo from URL
        parts = repo_url.rstrip('/').split('/')
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
    
    def get_recent_commits(self, owner, repo, limit=5):
        """Get recent commits from GitHub"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        headers = {'Authorization': f'token {self.github_token}'}
        
        try:
            response = requests.get(url, headers=headers, params={'per_page': limit})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching commits: {e}")
            return []
    
    def get_changed_files(self, owner, repo, commit_sha):
        """Get files changed in a specific commit"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
        headers = {'Authorization': f'token {self.github_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            commit_data = response.json()
            return commit_data.get('files', [])
        except requests.RequestException as e:
            print(f"Error fetching changed files: {e}")
            return []
    
    def get_file_content(self, owner, repo, file_path, ref='main'):
        """Get file content from GitHub"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        headers = {'Authorization': f'token {self.github_token}'}
        
        try:
            response = requests.get(url, headers=headers, params={'ref': ref})
            response.raise_for_status()
            file_data = response.json()
            
            if 'content' in file_data:
                content = base64.b64decode(file_data['content']).decode('utf-8')
                return content
            return None
        except requests.RequestException as e:
            print(f"Error fetching file content: {e}")
            return None
    
    def create_or_update_confluence_page(self, title, content, labels=None):
        """Create or update a Confluence page"""
        if labels is None:
            labels = []
        
        headers = self.get_auth_headers()
        space_id = self.get_space_id()
        
        if not space_id:
            print(f"✗ Error: Could not determine space ID for '{self.confluence_space_key}'")
            return False
        
        try:
            # Search for existing page by title
            search_url = f"{self.confluence_base_url}/wiki/api/v2/spaces/{space_id}/pages"
            search_response = requests.get(
                search_url,
                headers=headers,
                params={'title': title, 'limit': 1}
            )
            search_response.raise_for_status()
            existing_pages = search_response.json().get('results', [])
            
            page_body = {
                'type': 'doc',
                'version': 1,
                'content': [
                    {
                        'type': 'paragraph',
                        'content': [
                            {
                                'type': 'text',
                                'text': f'Last synced: {datetime.now().isoformat()}\n\n{content}'
                            }
                        ]
                    }
                ]
            }
            
            # Confluence API v2 requires body to be wrapped in 'representation'
            update_create_body = {
                'representation': 'storage',
                'value': f'<p><strong>Last synced:</strong> {datetime.now().isoformat()}</p><p>{content.replace(chr(10), "<br/>")}</p>'
            }
            
            if existing_pages:
                # Update existing page
                page_id = existing_pages[0]['id']
                current_version = existing_pages[0].get('version', {}).get('number', 1)
                update_url = f"{self.confluence_base_url}/wiki/api/v2/pages/{page_id}"
                update_data = {
                    'id': page_id,
                    'status': 'current',
                    'title': title,
                    'body': {
                        'representation': 'storage',
                        'value': f'<p><strong>Last synced:</strong> {datetime.now().isoformat()}</p><p>{content.replace(chr(10), "<br/>")}</p>'
                    },
                    'version': {
                        'number': current_version + 1
                    }
                }
                response = requests.put(update_url, headers=headers, json=update_data)
                response.raise_for_status()
                print(f"Updated page: {title}")
            else:
                # Create new page using correct endpoint
                create_url = f"{self.confluence_base_url}/wiki/api/v2/pages"
                create_data = {
                    'spaceId': space_id,
                    'status': 'current',
                    'title': title,
                    'body': {
                        'representation': 'storage',
                        'value': f'<p><strong>Last synced:</strong> {datetime.now().isoformat()}</p><p>{content.replace(chr(10), "<br/>")}</p>'
                    }
                }
                response = requests.post(create_url, headers=headers, json=create_data)
                response.raise_for_status()
                print(f"Created page: {title}")
            
            return True
        except requests.RequestException as e:
            print(f"Error syncing page '{title}': {e}")
            return False
    
    def is_text_file(self, file_path):
        """Check if file is a text file"""
        text_extensions = {
            '.md', '.txt', '.py', '.js', '.ts', '.json', '.yaml', '.yml',
            '.xml', '.html', '.css', '.sh', '.java', '.go', '.rs', '.cpp',
            '.c', '.h', '.rb', '.php', '.sql', '.dockerfile', '.tf',
            '.properties', '.env', '.gradle', '.maven', '.pom'
        }
        _, ext = os.path.splitext(file_path.lower())
        return ext in text_extensions
    
    def sync(self, repo_url):
        """Main sync function"""
        print(f"Starting GitHub to Confluence sync...")
        print(f"Repository: {repo_url}")
        
        owner, repo = self.parse_github_url(repo_url)
        print(f"Owner: {owner}, Repo: {repo}")
        
        # Get recent commits
        commits = self.get_recent_commits(owner, repo, limit=3)
        if not commits:
            print("No commits found")
            return
        
        synced_files = set()
        
        for commit in commits:
            commit_sha = commit['sha']
            print(f"\nProcessing commit: {commit_sha[:7]}")
            
            # Get changed files
            changed_files = self.get_changed_files(owner, repo, commit_sha)
            
            for file_info in changed_files:
                file_path = file_info['filename']
                status = file_info['status']
                
                # Skip if already synced in this run
                if file_path in synced_files:
                    continue
                
                # Skip deleted files
                if status == 'deleted':
                    print(f"  - Skipping deleted: {file_path}")
                    continue
                
                # Skip binary files
                if not self.is_text_file(file_path):
                    print(f"  - Skipping binary: {file_path}")
                    continue
                
                print(f"  - Processing: {file_path}")
                
                # Get file content
                content = self.get_file_content(owner, repo, file_path)
                if content:
                    # Create/update Confluence page
                    page_title = os.path.basename(file_path)
                    labels = ['github-sync', status, repo]
                    self.create_or_update_confluence_page(page_title, content, labels)
                    synced_files.add(file_path)
        
        print(f"\nSync complete! Processed {len(synced_files)} files")

def main():
    parser = argparse.ArgumentParser(description='Sync GitHub files to Confluence')
    parser.add_argument('repo_url', help='GitHub repository URL')
    args = parser.parse_args()
    
    try:
        sync = GitHubConfluenceSync()
        sync.sync(args.repo_url)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
