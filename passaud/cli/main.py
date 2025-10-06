"""
Main CLI entry point for PassAud.
"""

import logging
import sys
import json
import getpass

from passaud.utils.logger import setup_logging
from passaud.core.auditor import PasswordAuditor
from passaud.cli.help import print_banner, print_comprehensive_help, print_quick_guide
from passaud.config.config_manager import ConfigManager
from passaud.cli.parser import create_parser


def main():
    """Main CLI function."""
    parser = create_parser()  # Use our custom parser
    args = parser.parse_args()

    # Handle help and manual requests first
    if args.manual:
        print_comprehensive_help()
        return 0

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file=args.log_file)
    logger = logging.getLogger("passaud")

    # Load configuration
    config_manager = ConfigManager(args.config)

    # Handle interactive mode
    if args.interactive:
        from passaud.cli.shell import PassAudShell
        shell = PassAudShell(config_manager)
        shell.cmdloop()
        return 0

    # Print banner for command execution
    print_banner()

    auditor = PasswordAuditor(config_manager)

    # Handle commands
    if args.command == "strength":
        logger.info(f"Analyzing password strength: {args.password}")
        result = auditor.analyze_strength(args.password)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Password: {args.password}")
            print(f"Strength: {result['rating']} ({result['score']}/5)")
            print(f"Length: {result['length']} characters")
            print(f"Entropy: {result['entropy']} bits")
            if result.get('vulnerabilities'):
                print("\nVulnerabilities:")
                for vuln in result['vulnerabilities']:
                    print(f"  - {vuln}")
            if result.get('feedback'):
                print("\nRecommendations:")
                for item in result['feedback']:
                    print(f"  - {item}")

    elif args.command == "dict":
        logger.info(f"Dictionary attack on: {args.target}")
        result = auditor.dictionary_attack(
            target=args.target,
            wordlist_path=args.wordlist,
            hash_type=args.hash_type,
            apply_rules=args.rules,
            max_words=args.max_words
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result['found']:
                print(f"✓ Password found: {result['password']}")
            else:
                print("✗ Password not found")
            print(f"Attempts: {result['attempts']}")
            print(f"Time: {result['time_elapsed']:.2f} seconds")

    elif args.command == "dehash":
        logger.info(f"Dehashing: {args.hash}")
        result = auditor.deep_dehash(
            hash_value=args.hash,
            use_online=args.online,
            wordlist_path=args.wordlist,
            max_words=args.max_words,
            strategy=args.strategy
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result['cracked']:
                print(f"✓ Hash cracked: {result['password']}")
                print(f"Method: {result['method']}")
            else:
                print("✗ Hash not cracked")
                print(f"Method attempted: {result['method']}")
            print(f"Time: {result['time_elapsed']:.2f} seconds")
            print(f"Attempts: {result['attempts']}")

    elif args.command == "brute":
        logger.info(f"Brute-force estimation for: {args.password}")
        result = auditor.estimate_bruteforce(args.password, args.speed)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Password: {args.password}")
            print(f"Time Estimate: {result['time_estimate']}")
            print(f"Combinations: {result['combinations']}")
            print(f"Character Sets: {', '.join(result['character_sets'])}")
            print(f"Charset Size: {result['charset_size']}")

    elif args.command == "hash":
        logger.info(f"Generating {args.algorithm} hash for: {args.password}")
        hash_result = auditor.hasher.hash_string(args.password, args.algorithm)
        result = {
            "password": args.password,
            "algorithm": args.algorithm,
            "hash": hash_result
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Algorithm: {args.algorithm.upper()}")
            print(f"Input: {args.password}")
            print(f"Hash: {hash_result}")

    else:
        # No command provided, show quick guide
        print_quick_guide()

    return 0


if __name__ == "__main__":
    sys.exit(main())
