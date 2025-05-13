#!/usr/bin/env python3
import os
import yaml
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

def find_yaml_files(root_dir):
    """Find all YAML files in the repository."""
    yaml_files = []
    for path in Path(root_dir).rglob('*.y*ml'):
        if path.is_file():
            yaml_files.append(str(path))
    return yaml_files

def parse_yaml_file(file_path):
    """Parse a YAML file and return its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            return content
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def extract_relationships(yaml_files):
    """Extract relationships between YAML files."""
    relationships = []
    file_contents = {}
    
    # First, parse all files
    for file_path in yaml_files:
        content = parse_yaml_file(file_path)
        if content:
            file_contents[file_path] = content
    
    # Then, extract relationships
    for file_path, content in file_contents.items():
        # Check for includes
        if isinstance(content, dict) and 'include' in content:
            includes = content['include']
            if isinstance(includes, list):
                for include in includes:
                    if isinstance(include, dict) and 'local' in include:
                        target = include['local']
                        # Find the absolute path
                        for potential_target in yaml_files:
                            if potential_target.endswith(target):
                                relationships.append((file_path, potential_target, 'include'))
            elif isinstance(includes, dict) and 'local' in includes:
                target = includes['local']
                for potential_target in yaml_files:
                    if potential_target.endswith(target):
                        relationships.append((file_path, potential_target, 'include'))
        
        # Check for extends
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, dict) and 'extends' in value:
                    extends = value['extends']
                    if isinstance(extends, str):
                        # This is a reference to a job in the same file or another file
                        if '.' in extends and extends.startswith('.'):
                            # Local job reference
                            relationships.append((file_path, file_path, f'extends:{extends}'))
                        else:
                            # Could be a reference to another file
                            for potential_target in yaml_files:
                                if extends in potential_target:
                                    relationships.append((file_path, potential_target, 'extends'))
                    elif isinstance(extends, list):
                        for extend in extends:
                            if isinstance(extend, str):
                                if '.' in extend and extend.startswith('.'):
                                    # Local job reference
                                    relationships.append((file_path, file_path, f'extends:{extend}'))
                                else:
                                    # Could be a reference to another file
                                    for potential_target in yaml_files:
                                        if extend in potential_target:
                                            relationships.append((file_path, potential_target, 'extends'))
    
    return relationships

def create_graph(relationships):
    """Create a graph visualization of the relationships."""
    G = nx.DiGraph()
    
    # Add nodes and edges
    for source, target, rel_type in relationships:
        # Use shorter names for nodes
        source_short = os.path.basename(source)
        target_short = os.path.basename(target)
        
        G.add_node(source_short)
        G.add_node(target_short)
        G.add_edge(source_short, target_short, type=rel_type)
    
    # Create the visualization
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    
    # Draw edges
    edge_labels = {(u, v): d['type'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edges(G, pos, width=1.5, arrowsize=20)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10)
    
    plt.title("GitLab CI Templates Relationships")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("gitlab_templates_relationships.png")
    plt.show()

def main():
    # Get the repository root directory
    repo_root = os.getcwd()  # Assuming the script is run from the repo root
    
    # Find all YAML files
    yaml_files = find_yaml_files(repo_root)
    print(f"Found {len(yaml_files)} YAML files")
    
    # Extract relationships
    relationships = extract_relationships(yaml_files)
    print(f"Found {len(relationships)} relationships")
    
    # Create graph
    create_graph(relationships)
    print("Graph created and saved as 'gitlab_templates_relationships.png'")

if __name__ == "__main__":
    main()
