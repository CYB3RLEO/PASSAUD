"""
Interactive shell for PassAud.
"""

import cmd
import logging

from passaud.core.analyzer import PasswordAnalyzer
from passaud.cli.help import print_comprehensive_help, print_quick_guide


class PassAudShell(cmd.Cmd):
    """Interactive shell for PassAud."""

    intro = "\nWelcome to PassAud Interactive Mode. Type 'help' or '?' for commands.\n"
    prompt = "passaud> "

    def __init__(self):
        super().__init__()
        self.analyzer = PasswordAnalyzer()
        self.logger = logging.getLogger("passaud")

    def do_strength(self, arg):
        """Analyze password strength: strength <password>"""
        if not arg:
            print("Error: Password is required")
            return

        result = self.analyzer.analyze(arg)
        print(f"Password: {arg}")
        print(f"Strength: {result['rating']} ({result['score']}/5)")
        print(f"Length: {result['length']} characters")

        if result['vulnerabilities']:
            print("Vulnerabilities:")
            for vuln in result['vulnerabilities']:
                print(f"  - {vuln}")

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
