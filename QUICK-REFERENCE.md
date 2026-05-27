# IBM ACE to Mermaid Diagram - Quick Reference Card

## ⚡ Quick Commands

### Generate Single Diagram
```bash
python ace-flow-cli.py single flow.msgflow -o diagram.mmd
```

### Batch Generate All Flows
```bash
python ace-flow-cli.py batch -i ./flows -o ./diagrams -r
```

### Python Module Usage
```python
from ace_mermaid_generator import ACEFlowParser, MermaidDiagramGenerator
flow = ACEFlowParser.parse_xml(open("flow.msgflow").read())
print(MermaidDiagramGenerator.generate_with_legend(flow))
```

---

## 📊 Node Types Quick Reference

| Icon | Type | Description |
|------|------|-------------|
| 📥 | HTTPInputNode | Receive HTTP requests |
| 📤 | HTTPReplyNode | Send HTTP responses |
| ⚙️ | ComputeNode | Transform/process messages |
| 🗄️ | DatabaseNode | Database operations |
| 🔄 | FilterNode | Conditional routing |
| 📨 | MQInputNode | Message queue input |
| 📤 | MQOutputNode | Message queue output |
| 📂 | FileInputNode | Read files |
| 📁 | FileOutputNode | Write files |
| ⚠️ | ErrorHandler | Handle exceptions |
| 🔀 | SwitchNode | Multi-way branching |
| 💥 | ThrowNode | Throw exceptions |

---

## 🎨 Connection Types

| Type | Line Style | Meaning |
|------|-----------|---------|
| main | ——→ | Primary flow |
| success | ——→ | Successful outcome |
| error | ⋯→ (red) | Error/Exception |
| failure | ⋯→ (orange) | Failure condition |
| alternate | ⋯→ (purple) | Alternative path |

---

## 📈 Metrics Explained

```
total_nodes          = Total node count
node_types           = Breakdown by type
total_connections    = Total paths
error_paths          = Error handling paths
complexity_score     = nodes + connections
```

**Example:**
```json
{
  "total_nodes": 9,
  "total_connections": 12,
  "error_paths": 5,
  "complexity_score": 21
}
```

---

## 🔧 Common Patterns

### Parse & Get Metrics
```python
flow = ACEFlowParser.parse_xml(open("flow.msgflow").read())
metrics = flow.get_metrics()
print(f"Complexity: {metrics['complexity_score']}")
```

### Generate Without Legend
```python
diagram = MermaidDiagramGenerator.generate(flow, "My Flow")
```

### Generate With Legend
```python
diagram = MermaidDiagramGenerator.generate_with_legend(flow, "My Flow")
```

### Filter Error Paths Only
```python
error_conns = [c for c in flow.connections if c.conn_type == "error"]
```

### Get Node by Name
```python
node = flow.nodes["ReceiveOrder"]
print(node.node_type.icon)  # 📥
```

---

## 📁 File Structure

```
project/
├── flow.msgflow              ← Your ACE message flow
├── ace_mermaid_generator.py  ← Parser engine
├── ace-flow-cli.py          ← CLI tool
└── diagrams/                ← Output directory
    └── diagram.mmd          ← Generated diagram
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Rename file with hyphens to underscores |
| XML parsing error | Verify .msgflow is valid XML, UTF-8 encoded |
| Nodes missing | Check that all `<node>` elements have `name` and `type` |
| Import fails | Ensure `ace_mermaid_generator.py` is in same directory |
| Permission denied | Check write permissions on output directory |

---

## 📚 Documentation

- **SKILL.md** - What the skill does
- **skill-instructions.md** - How to use it
- **ace-mermaid-analyzer.md** - Deep dive implementation
- **REQUIREMENTS.md** - Installation & dependencies
- **SKILL-SUMMARY.md** - Complete overview

---

## ✅ Zero Dependencies

Core functionality uses **ONLY standard library**:
- `xml.etree.ElementTree` - XML parsing
- `json` - JSON support
- `dataclasses` - Data structures
- `enum` - Enumerations
- `re` - Regular expressions
- `pathlib` - Path operations
- `argparse` - CLI parsing

**No pip install needed for core features!**

---

## 🚀 Next Steps

1. ✅ Place .msgflow files in a directory
2. ✅ Run `python ace-flow-cli.py single yourflow.msgflow`
3. ✅ Review generated .mmd diagram
4. ✅ Copy to documentation
5. ✅ Set up CI/CD automation

---

## 📞 Support

For issues:
1. Check REQUIREMENTS.md for setup
2. Verify .msgflow is valid XML
3. See troubleshooting section above
4. Check example files for reference format

---

**Created with Copilot Skill Agent | Python 3.7+ | Zero Dependencies**
