#!/usr/bin/env python3
"""
Script to find duplicated stubs in the stubs directory.
This script identifies duplicate function, class, and method definitions
across .py and .pyi files in the stubs directory.
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class StubDefinition:
    """Class to represent a definition found in stub files."""
    def __init__(self, name: str, kind: str, signature: str, file_path: str, line_number: int):
        self.name = name
        self.kind = kind  # 'function', 'class', 'method', etc.
        self.signature = signature  # Full function/method signature or class definition
        self.file_path = file_path
        self.line_number = line_number

    def __str__(self):
        return f"{self.kind} '{self.name}' in {self.file_path}:{self.line_number}"

    def __repr__(self):
        return self.__str__()


def parse_stub_file(file_path: str) -> List[StubDefinition]:
    """Parse a stub file and extract definitions."""
    definitions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
        # Keep track of current class and indentation level for methods
        current_class = None
        current_indent = 0
        
        for i, line in enumerate(lines):
            line_number = i + 1
            stripped_line = line.strip()
            
            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith('#'):
                continue
                
            # Calculate indentation level
            indent = len(line) - len(line.lstrip())
            
            # Check for class definition
            class_match = re.match(r'^class\s+(\w+)(?:\(.*\))?:', line)
            if class_match:
                current_class = class_match.group(1)
                current_indent = indent
                definitions.append(StubDefinition(
                    name=current_class,
                    kind='class',
                    signature=stripped_line,
                    file_path=file_path,
                    line_number=line_number
                ))
                continue
            
            # Check for function or method definition
            func_match = re.match(r'^def\s+(\w+)\s*\(', line)
            if func_match:
                func_name = func_match.group(1)
                
                # Collect the full signature which might span multiple lines
                signature = stripped_line
                j = i + 1
                while j < len(lines) and ')' not in signature:
                    signature += ' ' + lines[j].strip()
                    j += 1
                    
                if indent > current_indent and current_class:
                    # This is a method
                    qualified_name = f"{current_class}.{func_name}"
                    definitions.append(StubDefinition(
                        name=qualified_name,
                        kind='method',
                        signature=signature,
                        file_path=file_path,
                        line_number=line_number
                    ))
                else:
                    # This is a function
                    definitions.append(StubDefinition(
                        name=func_name,
                        kind='function',
                        signature=signature,
                        file_path=file_path,
                        line_number=line_number
                    ))
                    
            # Reset class tracking if we're back to lower indentation
            if current_class and indent <= current_indent:
                current_class = None
                
    return definitions


def find_duplicates_in_stubs(stubs_dir: str) -> Dict[str, List[StubDefinition]]:
    """Find duplicated definitions in stub files."""
    all_definitions = defaultdict(list)
    duplicates = {}
    
    # Walk through the stubs directory
    for root, _, files in os.walk(stubs_dir):
        for file in files:
            if file.endswith('.py') or file.endswith('.pyi'):
                file_path = os.path.join(root, file)
                
                try:
                    definitions = parse_stub_file(file_path)
                    for definition in definitions:
                        key = (definition.kind, definition.name)
                        all_definitions[key].append(definition)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}", file=sys.stderr)
    
    # Find duplicates
    for (kind, name), definitions in all_definitions.items():
        if len(definitions) > 1:
            duplicates[f"{kind}:{name}"] = definitions
            
    return duplicates


def print_duplicate_report(duplicates: Dict[str, List[StubDefinition]]):
    """Print a report of duplicate definitions."""
    if not duplicates:
        print("No duplicates found!")
        return
        
    print(f"\nFound {len(duplicates)} duplicated definitions:\n")
    
    for i, (key, definitions) in enumerate(sorted(duplicates.items()), 1):
        kind, name = key.split(':', 1)
        print(f"{i}. {kind.upper()} '{name}' is defined {len(definitions)} times:")
        
        for j, definition in enumerate(definitions, 1):
            relative_path = os.path.relpath(definition.file_path)
            print(f"   {j}. In {relative_path}:{definition.line_number}")
            
        print()  # Add a blank line between different duplicates
    
    # Print statistics
    total_duplicates = sum(len(definitions) - 1 for definitions in duplicates.values())
    print(f"Total duplicate declarations: {total_duplicates}")


def group_duplicates_by_folder(duplicates: Dict[str, List[StubDefinition]]) -> Dict[Tuple[str, str, str], List[StubDefinition]]:
    """Group duplicates by the stubs subfolder they belong to."""
    result = defaultdict(list)
    
    for key, definitions in duplicates.items():
        kind, name = key.split(':', 1)
        
        folder_groups = defaultdict(list)
        for definition in definitions:
            # Get the first folder under stubs
            path_parts = Path(definition.file_path).parts
            stubs_index = path_parts.index('stubs')
            if len(path_parts) > stubs_index + 1:
                subfolder = path_parts[stubs_index + 1]
                folder_groups[subfolder].append(definition)
        
        # Only report as duplicates if they appear in the same subfolder
        for subfolder, subfolder_definitions in folder_groups.items():
            if len(subfolder_definitions) > 1:
                result[(subfolder, kind, name)] = subfolder_definitions
                
    return result


def analyze_stubs_folder(stubs_dir: str):
    """Analyze stubs folder for duplicates."""
    print(f"Analyzing stubs in: {stubs_dir}")
    
    # Find all duplicates
    duplicates = find_duplicates_in_stubs(stubs_dir)
    
    if not duplicates:
        print("\nNo duplicates found across all stub files!")
        return
        
    # Report general duplicates
    print_duplicate_report(duplicates)
    
    print("\n" + "="*80)
    print("DUPLICATES WITHIN SAME STUB TYPE")
    print("="*80)
    
    # Report duplicates within the same subfolder
    by_folder = group_duplicates_by_folder(duplicates)
    
    if not by_folder:
        print("\nNo duplicates found within the same stub type folder!")
    else:
        print(f"\nFound {len(by_folder)} duplicated definitions within the same stub type:")
        
        for i, ((subfolder, kind, name), definitions) in enumerate(sorted(by_folder.items()), 1):
            print(f"{i}. {subfolder}: {kind.upper()} '{name}' is defined {len(definitions)} times:")
            
            for j, definition in enumerate(definitions, 1):
                relative_path = os.path.relpath(definition.file_path)
                print(f"   {j}. In {relative_path}:{definition.line_number}")
                
            print()  # Add a blank line between different duplicates


if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stubs_dir = os.path.join(script_dir, "stubs")
    
    # If command line argument is provided, use it as the stubs directory
    if len(sys.argv) > 1:
        stubs_dir = sys.argv[1]
    
    if not os.path.isdir(stubs_dir):
        print(f"Error: Stubs directory not found at {stubs_dir}", file=sys.stderr)
        sys.exit(1)
        
    analyze_stubs_folder(stubs_dir)
