"""
Interactive shell for PassAud.
"""

import cmd
import logging
import shlex

from passaud.core.auditor import PasswordAuditor  # UPDATED
from passaud.cli.help import print_banner, print_comprehensive_help, print_quick_guide


class PassAudShell(cmd.Cmd):
    """Interactive shell for PassAud."""

    intro = "\nWelcome to PassAud Interactive Mode. Type 'help' or '?' for commands.\n"
    prompt = "passaud> "

    def __init__(self, config_manager=None):
        super().__init__()
        self.auditor = PasswordAuditor(config_manager)  # UPDATED
        self.logger = logging.getLogger("passaud")
        # Print banner when shell starts
        print_banner()

    def do_strength(self, arg):
        """Analyze password strength: strength <password>"""
        if not arg:
            print("Error: Password is required")
            return

        result = self.auditor.analyze_strength(arg)  # UPDATED

        print(f"Password: {arg}")
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

    def do_dehash(self, arg):
        """Deep hash cracking: dehash <hash> [--online] [--wordlist <path>] [--max-words <n>] [--strategy <auto|dictionary|hybrid|mask|brute>]"""
        args = shlex.split(arg)

        if not args:
            print("Error: Hash is required")
            return

        # Simple parsing for interactive mode
        hash_value = args[0]
        use_online = '--online' in args
        wordlist = None
        strategy = "auto"

        for i, arg in enumerate(args):
            if arg == '--wordlist' and i + 1 < len(args):
                wordlist = args[i + 1]
            elif arg == '--strategy' and i + 1 < len(args):
                strategy = args[i + 1]

        result = self.auditor.deep_dehash(  # UPDATED
            hash_value=hash_value,
            use_online=use_online,
            wordlist_path=wordlist,
            strategy=strategy
        )

        if result.get('error'):
            print(f"Error: {result['error']}")
            return

        print(f"Hash: {result['hash']}")
        if result.get('hash_type'):
            print(f"Type: {result['hash_type'].upper()}")

        if result['cracked']:
            print(f"✓ Hash cracked: {result['password']}")
            print(f"Method: {result['method']}")
        else:
            print("✗ Hash not cracked")
            print(f"Method attempted: {result['method']}")
        print(f"Time: {result['time_elapsed']:.2f} seconds")
        print(f"Attempts: {result['attempts']}")

    def do_dict(self, arg):
        """Dictionary attack: dict <target> --wordlist <path> [--hash-type <type>] [--max-words <n>] [--rules]"""
        args = shlex.split(arg)

        if len(args) < 2 or '--wordlist' not in args:
            print("Error: Target and --wordlist are required")
            return

        # Simple parsing
        target = args[0]
        wordlist = None
        hash_type = None
        max_words = 100000
        rules = '--rules' in args

        for i, arg in enumerate(args):
            if arg == '--wordlist' and i + 1 < len(args):
                wordlist = args[i + 1]
            elif arg == '--hash-type' and i + 1 < len(args):
                hash_type = args[i + 1]
            elif arg == '--max-words' and i + 1 < len(args):
                max_words = int(args[i + 1])

        if not wordlist:
            print("Error: Wordlist path is required")
            return

        result = self.auditor.dictionary_attack(  # UPDATED
            target=target,
            wordlist_path=wordlist,
            hash_type=hash_type,
            max_words=max_words,
            apply_rules=rules
        )

        if result.get('found'):
            print(f"✓ Password found: {result['password']}")
        else:
            print("✗ Password not found")
        print(f"Attempts: {result['attempts']}")
        print(f"Time: {result['time_elapsed']:.2f} seconds")

    def do_brute(self, arg):
        """Brute-force time estimation: brute <password> [--speed <n>]"""
        args = shlex.split(arg)

        if not args:
            print("Error: Password is required")
            return

        password = args[0]
        speed = 1000000

        for i, arg in enumerate(args):
            if arg == '--speed' and i + 1 < len(args):
                speed = int(args[i + 1])

        result = self.auditor.estimate_bruteforce(password, speed)  # UPDATED

        print(f"Password: {password}")
        print(f"Time Estimate: {result['time_estimate']}")
        print(f"Combinations: {result['combinations']}")
        print(f"Character Sets: {', '.join(result['character_sets'])}")
        print(f"Charset Size: {result['charset_size']}")

    def do_hash(self, arg):
        """Generate password hash: hash <password> [--algorithm <type>]"""
        args = shlex.split(arg)

        if not args:
            print("Error: Password is required")
            return

        password = args[0]
        algorithm = 'md5'

        for i, arg in enumerate(args):
            if arg == '--algorithm' and i + 1 < len(args):
                algorithm = args[i + 1]

        try:
            hash_result = self.auditor.hasher.hash_string(
                password, algorithm)  # UPDATED
            print(f"Algorithm: {algorithm.upper()}")
            print(f"Input: {password}")
            print(f"Hash: {hash_result}")
        except ValueError as e:
            print(f"Error: {e}")

    def do_help(self, arg):
        """Show quick help guide: help"""
        print_quick_guide()

    def do_manual(self, arg):
        """Show comprehensive manual: manual"""
        print_comprehensive_help()

    def do_exit(self, arg):
        """Exit the interactive shell: exit"""
        print("Goodbye!")
        return True

    def do_quit(self, arg):
        """Exit the interactive shell: quit"""
        return self.do_exit(arg)

    def do_clear(self, arg):
        """Clear the screen: clear"""
        print("\033c", end="")  # ANSI escape code to clear screen
        print_banner()  # Reprint banner after
