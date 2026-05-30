#!/usr/bin/env python3
"""
Create Confluence page with embedded Mermaid diagram
"""

import sys
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv(encoding='utf-8')

class MermaidConfluenceCreator:
    """Create Confluence page with Mermaid diagram"""
    
    def __init__(self):
        self.confluence_token = os.getenv('CONFLUENCE_TOKEN')
        self.confluence_base_url = os.getenv('CONFLUENCE_BASE_URL')
        self.confluence_space_key = os.getenv('CONFLUENCE_SPACE_KEY')
        self.confluence_email = os.getenv('CONFLUENCE_EMAIL')
        self.confluence_space_id = os.getenv('CONFLUENCE_SPACE_ID')
        
        if not all([self.confluence_token, self.confluence_base_url, self.confluence_space_key]):
            raise ValueError("Missing required environment variables")
    
    def get_auth_headers(self):
        """Create authentication headers for Confluence API"""
        if self.confluence_email:
            auth_str = base64.b64encode(
                f"{self.confluence_email}:{self.confluence_token}".encode()
            ).decode()
            return {
                'Authorization': f'Basic {auth_str}',
                'Content-Type': 'application/json'
            }
        else:
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
    
    def create_mermaid_page(self, title, mermaid_content):
        """Create a Confluence page with Mermaid diagram"""
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
            
            # Create the page body with Mermaid diagram
            # Use the mermaid macro directly in storage format
            page_body = f'''<p><strong>Last synced:</strong> {datetime.now().isoformat()}</p>
<ac:structured-macro ac:name="mermaid" ac:schema-version="1">
<ac:plain-text-body><![CDATA[{mermaid_content}]]></ac:plain-text-body>
</ac:structured-macro>'''
            
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
                        'value': page_body
                    },
                    'version': {
                        'number': current_version + 1
                    }
                }
                response = requests.put(update_url, headers=headers, json=update_data)
                response.raise_for_status()
                print(f"✓ Updated page: {title}")
                return True
            else:
                # Create new page
                create_url = f"{self.confluence_base_url}/wiki/api/v2/pages"
                create_data = {
                    'spaceId': space_id,
                    'status': 'current',
                    'title': title,
                    'body': {
                        'representation': 'storage',
                        'value': page_body
                    }
                }
                response = requests.post(create_url, headers=headers, json=create_data)
                response.raise_for_status()
                print(f"✓ Created page: {title}")
                return True
        except requests.RequestException as e:
            print(f"✗ Error syncing page '{title}': {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_mermaid_page.py <mermaid_file> <page_title>")
        print("Example: python create_mermaid_page.py diagram.mmd 'Payment Processing Flow'")
        sys.exit(1)
    
    mermaid_file = sys.argv[1]
    page_title = sys.argv[2] if len(sys.argv) > 2 else "Mermaid Diagram"
    
    try:
        # Read mermaid file with UTF-8 encoding
        with open(mermaid_file, 'r', encoding='utf-8') as f:
            mermaid_content = f.read()
        
        print(f"Reading mermaid diagram from: {mermaid_file}")
        print(f"Page title: {page_title}")
        
        creator = MermaidConfluenceCreator()
        success = creator.create_mermaid_page(page_title, mermaid_content)
        
        if success:
            print("✓ Mermaid diagram successfully synced to Confluence!")
            sys.exit(0)
        else:
            sys.exit(1)
    except FileNotFoundError:
        print(f"✗ Error: File not found: {mermaid_file}")
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
