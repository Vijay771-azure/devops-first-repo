# IBM ACE Message Flow to Mermaid Diagram Skill Agent

A powerful AI-assisted skill that analyzes IBM AppConnect Enterprise (ACE) message flows and automatically generates interactive mermaid diagrams for visualization and documentation.

## What's Included

This skill package contains:

1. **SKILL.md** - Skill definition and capabilities
2. **ace-mermaid-analyzer.md** - Comprehensive usage guide
3. **ace_mermaid_generator.py** - Core Python implementation
4. **ace-flow-cli.py** - CLI tool for batch processing
5. **skill-instructions.md** - Detailed integration and usage instructions
6. **sample-payment-flow.msgflow** - Example ACE message flow
7. **payment-flow-diagram.mmd** - Generated mermaid diagram example

## Quick Start

### Generate Diagram from a Single Flow
```bash
python ace-flow-cli.py single your-flow.msgflow -o output-diagram.mmd
```

### Batch Process Multiple Flows
```bash
python ace-flow-cli.py batch -i ./flows -o ./diagrams -r
```

## Key Features

 Automatic Parsing - Extracts all nodes and connections
 Visual Hierarchy - Left-to-right flow with clear data paths
 Color Coding - Different colors for node types
 Error Handling - Visualizes exception paths
 Metrics - Calculates flow complexity
 CLI Tool - Single and batch processing

## Use Cases

1. Documentation - Auto-generate flow diagrams
2. Training - Visual learning of integration patterns
3. Code Review - Understand flow changes
4. Validation - Verify flow structure
5. Monitoring - Track flow complexity

## Support & Documentation

- See **SKILL.md** for capability details
- See **ace-mermaid-analyzer.md** for usage patterns
- See **skill-instructions.md** for advanced usage

**Created with Copilot Skill Agent**
