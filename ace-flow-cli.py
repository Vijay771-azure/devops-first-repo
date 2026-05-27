#!/usr/bin/env python3
"""
CLI tool to generate mermaid diagrams from IBM ACE message flows
"""

import sys
import argparse
from pathlib import Path
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ace_mermaid_generator import ACEFlowParser, MermaidDiagramGenerator
import json


def process_single_file(input_file: str, output_file: str = None):
    """Process a single ACE flow file"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Parse flow
        flow = ACEFlowParser.parse_xml(xml_content)
        print(f"✓ Parsed flow: {flow.name}")
        print(f"  - Nodes: {len(flow.nodes)}")
        print(f"  - Connections: {len(flow.connections)}")
        
        # Generate diagram
        diagram = MermaidDiagramGenerator.generate_with_legend(flow, flow.name)
        
        # Output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(diagram)
            print(f"✓ Diagram saved to: {output_file}")
        else:
            print("\n" + "="*60)
            print("GENERATED MERMAID DIAGRAM:")
            print("="*60)
            print(diagram)
        
        # Show metrics
        metrics = flow.get_metrics()
        print("\n" + "="*60)
        print("FLOW METRICS:")
        print("="*60)
        print(f"Total Nodes: {metrics['total_nodes']}")
        print(f"Total Connections: {metrics['total_connections']}")
        print(f"Error Paths: {metrics['error_paths']}")
        print(f"Complexity Score: {metrics['complexity_score']}")
        print("\nNode Types:")
        for node_type, count in metrics['node_types'].items():
            print(f"  - {node_type}: {count}")
        
        return True
    
    except FileNotFoundError:
        print(f"✗ Error: File not found: {input_file}")
        return False
    except Exception as e:
        print(f"✗ Error processing file: {e}")
        return False


def batch_process(input_dir: str, output_dir: str, recursive: bool = True):
    """Batch process multiple flow files"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .msgflow files
    pattern = "**/*.msgflow" if recursive else "*.msgflow"
    flow_files = list(input_path.glob(pattern))
    
    if not flow_files:
        print(f"✗ No .msgflow files found in {input_dir}")
        return False
    
    print(f"Found {len(flow_files)} flow files to process\n")
    
    results = {"success": 0, "failed": 0}
    
    for flow_file in flow_files:
        relative_path = flow_file.relative_to(input_path)
        output_file = output_path / relative_path.with_suffix('.mmd')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing: {relative_path}")
        if process_single_file(str(flow_file), str(output_file)):
            results["success"] += 1
        else:
            results["failed"] += 1
    
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY:")
    print("="*60)
    print(f"Successful: {results['success']}")
    print(f"Failed: {results['failed']}")
    print(f"Output directory: {output_dir}")
    
    return results["failed"] == 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate mermaid diagrams from IBM ACE message flows"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Single file command
    single_parser = subparsers.add_parser("single", help="Process a single flow file")
    single_parser.add_argument("input", help="Input .msgflow file")
    single_parser.add_argument("-o", "--output", help="Output .mmd file (optional)")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Process multiple flow files")
    batch_parser.add_argument("-i", "--input-dir", required=True, help="Input directory")
    batch_parser.add_argument("-o", "--output-dir", required=True, help="Output directory")
    batch_parser.add_argument("-r", "--recursive", action="store_true", help="Recursive search")
    
    args = parser.parse_args()
    
    if args.command == "single":
        success = process_single_file(args.input, args.output)
        sys.exit(0 if success else 1)
    
    elif args.command == "batch":
        success = batch_process(args.input_dir, args.output_dir, args.recursive)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
