# IBM ACE Message Flow to Mermaid Diagram Generator - Requirements

## Core Requirements
- Python 3.7 or higher
- Standard library only (no external dependencies for core functionality)

## Optional Requirements

### For PNG/SVG Export
```
mermaid-cli
```

Install with:
```bash
npm install -g @mermaid-js/mermaid-cli
```

### For File Watching (Real-time Updates)
```
watchdog
```

Install with:
```bash
pip install watchdog
```

### For Enhanced CLI Features
```
click>=7.0
colorama>=0.4.0
```

## Installation

### 1. Core Installation (No Dependencies)
Simply ensure Python 3.7+ is installed. All core functionality works with standard library.

### 2. Full Installation (With Extras)
```bash
pip install -r requirements-full.txt
```

### 3. Development Installation
```bash
pip install -r requirements-dev.txt
```

## System Requirements

- **OS**: Windows, macOS, Linux
- **Memory**: 100+ MB
- **Disk**: 50+ MB for installation
- **Network**: Optional (only for external integrations)

## File Encoding

All .msgflow files should be UTF-8 encoded for proper parsing.

## Python Version Compatibility

- ✅ Python 3.7
- ✅ Python 3.8
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12

## No External Dependencies

The core generator requires **zero external packages** because it only uses:
- `xml.etree.ElementTree` - XML parsing (standard library)
- `json` - JSON handling (standard library)
- `dataclasses` - Data structures (standard library)
- `enum` - Enumerations (standard library)
- `re` - Regular expressions (standard library)
- `pathlib` - Path handling (standard library)
- `argparse` - CLI argument parsing (standard library)

This makes it lightweight and easy to deploy!

## Verification

To verify your installation:

```bash
python -c "from ace_mermaid_generator import ACEFlowParser; print('✓ Installation successful')"
```

## Troubleshooting

### ImportError on Windows
If you get module import errors on Windows:
1. Ensure Python is added to PATH
2. Rename files with hyphens to underscores (e.g., `ace_mermaid_generator.py`)
3. Use full paths when running scripts

### XML Parsing Errors
If you get XML parsing errors:
1. Ensure .msgflow files are valid XML
2. Check file encoding (must be UTF-8)
3. Verify opening/closing tags match

### Permission Denied
If you get permission errors:
1. Check file permissions (`chmod +x` on Unix/Linux)
2. Ensure write permissions in output directory
3. Run as administrator if needed (Windows)
