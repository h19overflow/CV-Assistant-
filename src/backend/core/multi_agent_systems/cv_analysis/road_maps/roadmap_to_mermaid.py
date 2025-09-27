"""
Convert roadmap data to Mermaid diagram format.
"""

def roadmap_to_mermaid(steps, edges, include_details=True):
    """
    Convert roadmap steps and edges to Mermaid diagram format.

    Args:
        steps: List of RoadmapStep objects
        edges: List of RoadmapEdge objects
        include_details: Whether to include step details in click events

    Returns:
        str: Mermaid diagram as string
    """
    node_lines = []
    click_lines = []

    for step in steps:
        # Clean ID to be valid Mermaid identifier (no spaces, special chars)
        clean_id = step.id.replace(' ', '_').replace('-', '_')

        # Clean label for node display
        label = step.label.replace('"', "'")

        # Create node
        if step.milestone:
            node_lines.append(f'{clean_id}(["{label}"])')
        else:
            node_lines.append(f'{clean_id}["{label}"]')

        # Add click event with details if available
        if include_details and step.detail:
            # Clean detail text for tooltip
            detail_text = step.detail.replace('"', "'").replace('\n', ' ')
            timeframe_text = f" ({step.timeframe})" if step.timeframe else ""
            full_detail = f"{step.label}{timeframe_text}: {detail_text}"
            click_lines.append(f'click {clean_id} "{full_detail}"')

    edge_lines = []
    for edge in edges:
        # Clean source and target IDs
        clean_source = edge.source.replace(' ', '_').replace('-', '_')
        clean_target = edge.target.replace(' ', '_').replace('-', '_')

        label = f'|{edge.label}|' if edge.label else ""
        edge_lines.append(f'{clean_source} --{label}--> {clean_target}')

    # Combine all parts
    all_lines = node_lines + edge_lines + click_lines
    return "graph TD\n    " + "\n    ".join(all_lines)

def roadmap_to_mermaid_with_details(steps, edges):
    """
    Convert roadmap steps and edges to Mermaid diagram format with details in nodes.

    Args:
        steps: List of RoadmapStep objects
        edges: List of RoadmapEdge objects

    Returns:
        str: Mermaid diagram as string with details in nodes
    """
    node_lines = []

    for step in steps:
        # Clean ID to be valid Mermaid identifier (no spaces, special chars)
        clean_id = step.id.replace(' ', '_').replace('-', '_')

        # Create comprehensive label with details
        label = step.label.replace('"', "'")

        # Add timeframe if available
        if step.timeframe:
            label += f"<br/><small>({step.timeframe})</small>"

        # Add truncated detail if available
        if step.detail:
            detail_preview = step.detail[:80] + "..." if len(step.detail) > 80 else step.detail
            detail_preview = detail_preview.replace('"', "'").replace('\n', ' ')
            label += f"<br/><small>{detail_preview}</small>"

        # Create node
        if step.milestone:
            node_lines.append(f'{clean_id}(["{label}"])')
        else:
            node_lines.append(f'{clean_id}["{label}"])')

    edge_lines = []
    for edge in edges:
        # Clean source and target IDs
        clean_source = edge.source.replace(' ', '_').replace('-', '_')
        clean_target = edge.target.replace(' ', '_').replace('-', '_')

        edge_label = f'|{edge.label}|' if edge.label else ""
        edge_lines.append(f'{clean_source} --{edge_label}--> {clean_target}')

    return "graph TD\n    " + "\n    ".join(node_lines + edge_lines)

def save_mermaid_to_file(mermaid_content, filepath):
    """
    Save Mermaid content to a file.

    Args:
        mermaid_content: Mermaid diagram string
        filepath: Path to save the file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(mermaid_content)