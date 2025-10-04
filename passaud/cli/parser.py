"""
Argument parsing for PassAud CLI.
"""

import argparse

def create_parser():
    """Create the argument parser for PassAud."""
    parser = argparse.ArgumentParser(
        description="PassAud - Password Security Analysis Tool",
        epilog="For more information, visit https://github.com/CYB3RLEO/PASSAUD"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--log-file", 
        help="Path to log file"
    )
    
    parser.add_argument(
        "--json", 
        action="store_true",
        help="Output in JSON format"
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Strength analysis command
    strength_parser = subparsers.add_parser(
        "strength", 
        help="Analyze password strength"
    )
    strength_parser.add_argument(
        "password", 
        help="Password to analyze"
    )
    
    return parser