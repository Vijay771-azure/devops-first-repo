#!/usr/bin/env python3
"""
IBM ACE Message Flow to Mermaid Diagram Generator
Parses IBM AppConnect Enterprise message flows and generates mermaid diagrams
"""

import xml.etree.ElementTree as ET
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class NodeType(Enum):
    """IBM ACE Node Types"""
    HTTP_INPUT = ("HTTPInputNode", "📥", "#e3f2fd", "#1976d2")
    HTTP_REPLY = ("HTTPReplyNode", "📤", "#fce4ec", "#c2185b")
    COMPUTE = ("ComputeNode", "⚙️", "#fff3e0", "#f57c00")
    DATABASE = ("DatabaseNode", "🗄️", "#e8f5e9", "#388e3c")
    FILTER = ("FilterNode", "🔄", "#f3e5f5", "#7b1fa2")
    MQ_INPUT = ("MQInputNode", "📨", "#e0f2f1", "#00796b")
    MQ_OUTPUT = ("MQOutputNode", "📤", "#b2ebf2", "#00897b")
    FILE_INPUT = ("FileInputNode", "📂", "#ffe0b2", "#e65100")
    FILE_OUTPUT = ("FileOutputNode", "📁", "#ffcc80", "#ef6c00")
    ERROR_HANDLER = ("ErrorHandler", "⚠️", "#ffebee", "#c62828")
    SWITCH = ("SwitchNode", "🔀", "#f3e5f5", "#6a1b9a")
    THROW = ("ThrowNode", "💥", "#ffebee", "#b71c1c")
    UNKNOWN = ("UnknownNode", "❓", "#f5f5f5", "#616161")

    def __init__(self, node_class: str, icon: str, bg_color: str, border_color: str):
        self.node_class = node_class
        self.icon = icon
        self.bg_color = bg_color
        self.border_color = border_color


@dataclass
class Node:
    """Represents an ACE message flow node"""
    name: str
    node_type: NodeType
    properties: Dict[str, str] = field(default_factory=dict)
    description: str = ""

    def get_label(self) -> str:
        """Generate node label for diagram"""
        lines = [f"{self.node_type.icon} {self.node_type.node_class}"]
        lines.append(f"{self.name}")
        if self.description:
            lines.append(f"{self.description}")
        return "<br/>".join(lines)


@dataclass
class Connection:
    """Represents a connection between nodes"""
    source: str
    target: str
    label: str = "flow"
    conn_type: str = "main"  # main, success, error, alternate

    def get_style(self) -> str:
        """Get connection line style"""
        if self.conn_type == "error":
            return "dashed,stroke:#d32f2f,color:#d32f2f"
        elif self.conn_type == "failure":
            return "dashed,stroke:#f57c00,color:#f57c00"
        elif self.conn_type == "alternate":
            return "dotted,stroke:#7b1fa2,color:#7b1fa2"
        return "solid,stroke:#333,color:#333"


@dataclass
class MessageFlow:
    """Represents an IBM ACE message flow"""
    name: str
    nodes: Dict[str, Node] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def add_node(self, name: str, node_type: NodeType, properties: Dict = None, description: str = ""):
        """Add a node to the flow"""
        self.nodes[name] = Node(name, node_type, properties or {}, description)

    def add_connection(self, source: str, target: str, label: str = "flow", conn_type: str = "main"):
        """Add a connection between nodes"""
        self.connections.append(Connection(source, target, label, conn_type))

    def get_metrics(self) -> Dict:
        """Calculate flow metrics"""
        node_types = {}
        for node in self.nodes.values():
            type_name = node.node_type.node_class
            node_types[type_name] = node_types.get(type_name, 0) + 1

        error_paths = len([c for c in self.connections if c.conn_type in ["error", "failure"]])
        
        return {
            "total_nodes": len(self.nodes),
            "node_types": node_types,
            "total_connections": len(self.connections),
            "error_paths": error_paths,
            "complexity_score": len(self.nodes) + len(self.connections)
        }


class ACEFlowParser:
    """Parses IBM ACE message flow XML files"""

    @staticmethod
    def detect_node_type(node_class: str) -> NodeType:
        """Detect node type from class name"""
        mapping = {
            "HTTPInputNode": NodeType.HTTP_INPUT,
            "HTTPReplyNode": NodeType.HTTP_REPLY,
            "HTTPRequestNode": NodeType.HTTP_INPUT,
            "ComputeNode": NodeType.COMPUTE,
            "DatabaseNode": NodeType.DATABASE,
            "FilterNode": NodeType.FILTER,
            "MQInputNode": NodeType.MQ_INPUT,
            "MQOutputNode": NodeType.MQ_OUTPUT,
            "FileInputNode": NodeType.FILE_INPUT,
            "FileOutputNode": NodeType.FILE_OUTPUT,
            "ErrorHandler": NodeType.ERROR_HANDLER,
            "SwitchNode": NodeType.SWITCH,
            "ThrowNode": NodeType.THROW,
        }
        return mapping.get(node_class, NodeType.UNKNOWN)

    @staticmethod
    def parse_xml(xml_content: str) -> MessageFlow:
        """Parse IBM ACE message flow XML"""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {e}")

        flow_name = root.get("name", "MessageFlow")
        flow = MessageFlow(name=flow_name)

        # Parse nodes
        for node_elem in root.findall(".//node"):
            node_name = node_elem.get("name", "UnnamedNode")
            node_class = node_elem.get("type", "UnknownNode")
            node_type = ACEFlowParser.detect_node_type(node_class)

            # Extract properties
            properties = {}
            for prop in node_elem.findall("property"):
                prop_name = prop.get("name", "")
                prop_value = prop.text or ""
                if prop_name:
                    properties[prop_name] = prop_value

            description = node_elem.get("description", "")
            flow.add_node(node_name, node_type, properties, description)

        # Parse connections
        for conn_elem in root.findall(".//connection"):
            source = conn_elem.get("source", "")
            target = conn_elem.get("target", "")
            label = conn_elem.get("label", "flow")
            conn_type = conn_elem.get("type", "main")

            if source and target:
                flow.add_connection(source, target, label, conn_type)

        return flow

    @staticmethod
    def parse_json(json_content: str) -> MessageFlow:
        """Parse IBM ACE message flow JSON format"""
        data = json.loads(json_content)
        flow = MessageFlow(name=data.get("name", "MessageFlow"))

        # Parse nodes
        for node_data in data.get("nodes", []):
            node_name = node_data.get("name", "")
            node_type = ACEFlowParser.detect_node_type(node_data.get("type", "UnknownNode"))
            properties = node_data.get("properties", {})
            description = node_data.get("description", "")
            flow.add_node(node_name, node_type, properties, description)

        # Parse connections
        for conn_data in data.get("connections", []):
            flow.add_connection(
                conn_data.get("source", ""),
                conn_data.get("target", ""),
                conn_data.get("label", "flow"),
                conn_data.get("type", "main")
            )

        return flow


class MermaidDiagramGenerator:
    """Generates mermaid diagrams from ACE message flows"""

    @staticmethod
    def generate(flow: MessageFlow, title: str = "") -> str:
        """Generate mermaid diagram syntax"""
        lines = ["graph LR"]
        
        # Add title if provided
        if title or flow.name:
            lines.append(f"    subgraph sg [\" {title or flow.name} \"]")

        # Add nodes
        node_definitions = []
        for node_name, node in flow.nodes.items():
            node_id = MermaidDiagramGenerator._sanitize_id(node_name)
            label = node.get_label()
            node_def = f'    {node_id}["{label}"]'
            node_definitions.append(node_def)

        lines.extend(node_definitions)

        # Add connections
        for conn in flow.connections:
            source_id = MermaidDiagramGenerator._sanitize_id(conn.source)
            target_id = MermaidDiagramGenerator._sanitize_id(conn.target)
            label = conn.label if conn.label != "flow" else ""
            
            arrow = "-->|" + label + "|" if label else "-->"
            lines.append(f"    {source_id} {arrow} {target_id}")

        # Add styling
        lines.append("")
        lines.append("    %% Node Styling")
        for node_name, node in flow.nodes.items():
            node_id = ACEFlowParser._sanitize_id(node_name)
            style = f"fill:{node.node_type.bg_color},stroke:{node.node_type.border_color},color:#000"
            lines.append(f"    style {node_id} {style}")

        if title or flow.name:
            lines.append("    end")

        return "\n".join(lines)

    @staticmethod
    def _sanitize_id(name: str) -> str:
        """Sanitize node name for use as ID in mermaid"""
        # Remove special characters and replace spaces
        sanitized = re.sub(r"[^\w]", "_", name)
        return sanitized if sanitized else "node"

    @staticmethod
    def generate_with_legend(flow: MessageFlow, title: str = "") -> str:
        """Generate mermaid diagram with legend"""
        mermaid = MermaidDiagramGenerator.generate(flow, title)
        
        # Add legend section
        legend_lines = [
            "",
            "    subgraph legend [\" Legend \"]",
            "        direction LR",
            "        i1[\"📥 HTTP Input\"]",
            "        i2[\"📤 HTTP Reply\"]",
            "        i3[\"⚙️ Compute\"]",
            "        i4[\"🗄️ Database\"]",
            "        i5[\"🔄 Filter\"]",
            "    end",
            "",
            "    style legend fill:#f9f9f9,stroke:#999,stroke-width:2px",
        ]
        
        return mermaid + "\n".join(legend_lines)


def main():
    """Example usage"""
    # Sample XML flow
    sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <messageFlow name="OrderProcessing">
        <node name="ReceiveOrder" type="HTTPInputNode" description="Receive HTTP Order"/>
        <node name="ValidateOrder" type="ComputeNode" description="Validate Order Data"/>
        <node name="CheckStatus" type="FilterNode" description="Check Order Status"/>
        <node name="SaveToDB" type="DatabaseNode" description="Save to Database"/>
        <node name="SendResponse" type="HTTPReplyNode" description="Send HTTP Response"/>
        <node name="ErrorHandler" type="ErrorHandler" description="Handle Errors"/>
        
        <connection source="ReceiveOrder" target="ValidateOrder" label="Input" type="main"/>
        <connection source="ValidateOrder" target="CheckStatus" label="Process" type="main"/>
        <connection source="CheckStatus" target="SaveToDB" label="Valid" type="main"/>
        <connection source="CheckStatus" target="ErrorHandler" label="Invalid" type="error"/>
        <connection source="SaveToDB" target="SendResponse" label="Success" type="main"/>
        <connection source="ErrorHandler" target="SendResponse" label="Error" type="error"/>
    </messageFlow>
    '''

    # Parse flow
    flow = ACEFlowParser.parse_xml(sample_xml)
    
    # Generate diagram
    diagram = MermaidDiagramGenerator.generate_with_legend(flow, "Order Processing Flow")
    
    print("Generated Mermaid Diagram:")
    print(diagram)
    print("\n\nFlow Metrics:")
    print(json.dumps(flow.get_metrics(), indent=2))


if __name__ == "__main__":
    main()
