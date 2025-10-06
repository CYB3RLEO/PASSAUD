"""
Argument parsing for PassAud CLI.
"""

import argparse

def create_parser():
    """Create the main argument parser for PassAud."""
    parser = argparse.ArgumentParser(
        description="PassAud - Password Security Analysis Tool",
        epilog="For more information, visit https://github.com/CYB3RLEO/PASSAUD"
    )
    
    # Global options
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
    
    parser.add_argument(
        "--manual", 
        action="store_true",
        help="Show comprehensive manual"
    )
    
    parser.add_argument(
        "--interactive", "-i", 
        action="store_true", 
        help="Start interactive mode"
    )
    
    parser.add_argument(
        "--config", 
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--session", 
        help="Path to session file for saving/loading"
    )
    
    # Subcommands
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
    
    # Dictionary attack command
    dict_parser = subparsers.add_parser(
        "dict", 
        help="Perform dictionary attack"
    )
    dict_parser.add_argument(
        "target", 
        help="Password or hash to attack"
    )
    dict_parser.add_argument(
        "--wordlist", 
        required=True,
        help="Path to wordlist file"
    )
    dict_parser.add_argument(
        "--hash-type", 
        help="Specify hash type"
    )
    dict_parser.add_argument(
        "--max-words", 
        type=int, 
        default=100000,
        help="Maximum words to test"
    )
    dict_parser.add_argument(
        "--rules", 
        action="store_true",
        help="Enable rule-based transformations"
    )
    
    # Dehash command
    dehash_parser = subparsers.add_parser(
        "dehash", 
        help="Deep hash cracking analysis"
    )
    dehash_parser.add_argument(
        "hash", 
        help="Hash to crack"
    )
    dehash_parser.add_argument(
        "--online", 
        action="store_true",
        help="Enable online hash lookup"
    )
    dehash_parser.add_argument(
        "--wordlist", 
        help="Path to wordlist for dictionary attack"
    )
    dehash_parser.add_argument(
        "--max-words", 
        type=int, 
        default=50000,
        help="Max words to test in dictionary"
    )
    dehash_parser.add_argument(
        "--strategy", 
        choices=["auto", "dictionary", "hybrid", "mask", "brute"], 
        default="auto",
        help="Attack strategy to use"
    )
    
    # Brute-force estimation command
    brute_parser = subparsers.add_parser(
        "brute", 
        help="Estimate brute-force time"
    )
    brute_parser.add_argument(
        "password", 
        help="Password to estimate for"
    )
    brute_parser.add_argument(
        "--speed", 
        type=int, 
        default=1000000,
        help="Cracking speed (attempts/sec)"
    )
    
    # Hash generation command
    hash_parser = subparsers.add_parser(
        "hash", 
        help="Generate password hashes"
    )
    hash_parser.add_argument(
        "password", 
        help="Password to hash"
    )
    hash_parser.add_argument(
        "--algorithm", 
        choices=["md5", "sha1", "sha256", "sha384", "sha512", "bcrypt", "scrypt", "argon2"], 
        default="md5",
        help="Hash algorithm to use"
    )
    
    return parser