"""
Main CLI entry point for PassAud.
"""

import argparse
import logging
import sys
import json

from passaud.utils.logger import setup_logging
from passaud.core.analyzer import PasswordAnalyzer

def main():
    """Main CLI function."""
    # Set up argument parser
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
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file=args.log_file)
    logger = logging.getLogger("passaud")
    
    # Handle commands
    if args.command == "strength":
        logger.info(f"Analyzing password strength: {args.password}")
        
        # Initialize analyzer and analyze password
        analyzer = PasswordAnalyzer()
        result = analyzer.analyze(args.password)
        
        # Output results
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Password: {args.password}")
            print(f"Strength: {result['rating']} ({result['score']}/5)")
            print(f"Length: {result['length']} characters")
            if result['vulnerabilities']:
                print("Vulnerabilities:")
                for vuln in result['vulnerabilities']:
                    print(f"  - {vuln}")
    
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())