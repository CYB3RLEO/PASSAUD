"""
Comprehensive help system and banner for PassAud.
"""

def print_banner():
    """Print the PassAud banner."""
    banner = r"""
    ██████╗  █████╗ ███████╗███████╗ █████╗ ██╗   ██╗██████╗ 
    ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗██║   ██║██╔══██╗
    ██████╔╝███████║███████╗███████╗███████║██║   ██║██║  ██║
    ██╔═══╝ ██╔══██║╚════██║╚════██║██╔══██║██║   ██║██║  ██║
    ██║     ██║  ██║███████║███████║██║  ██║╚██████╔╝██████╔╝
    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ 
    """
    
    # Print colorful version
    print("\033[1;36m" + banner + "\033[0m")
    print("\033[1;32mCreated by CYB3RLEO\033[0m")
    print("\033[1;32mGitHub Profile: https://github.com/CYB3RLEO\033[0m")
    print("\033[1;34m" + "=" * 70 + "\033[0m")
    print("\033[1;31mWARNING: For authorized security testing and educational purposes only.")
    print("Unauthorized access to computer systems is illegal and unethical.")
    print("Use this tool only on systems where you have explicit permission.\033[0m")
    print("\033[1;34m" + "=" * 70 + "\033[0m\n")

def print_comprehensive_help():
    """Display comprehensive help guide and manual."""
    print_banner()
    
    help_content = """
\033[1;36m╔══════════════════════════════════════════════════════════════════════════════╗
║                        PASSAUD COMPREHENSIVE MANUAL                  ║
╚══════════════════════════════════════════════════════════════════════════════╝\033[0m

\033[1;35mOVERVIEW:\033[0m
PassAud is a comprehensive password security analysis tool designed for 
penetration testers, security researchers, and system administrators. It 
provides multi-vector password analysis, hash cracking, and security assessment 
capabilities with both offline and online attack methods.

\033[1;33m══════════════════════════════════════════════════════════════════════════════\033[0m
\033[1;35mCOMMAND REFERENCE:\033[0m

\033[1;32m1. STRENGTH - Password Strength Analysis\033[0m
   Purpose: Analyze password security and provide improvement recommendations
   
   Usage: strength <password> [--json]
   
   Features:
   • Length validation (minimum 8, recommended 12+)
   • Character complexity analysis
   • Common password detection
   • Brute-force time estimation
   • Security scoring (1-5 scale)
   • Detailed vulnerability reporting
   • Entropy calculation
   • Sequential character detection
   • Personal information detection

\033[1;32m2. DICT - Dictionary Attack\033[0m
   Purpose: Perform dictionary-based password/hash cracking
   
   Usage: dict <target> --wordlist <path> [--hash-type <type>] [--max-words <n>] [--rules]
   
   Required:
   --wordlist <path>     Path to wordlist file
   
   Options:
   --hash-type <type>    Specify hash type (auto-detected if not provided)
   --max-words <number>  Maximum words to test (default: 100000)
   --rules               Enable rule-based transformations

\033[1;32m3. DEHASH - Deep Hash Cracking\033[0m
   Purpose: Multi-stage hash cracking using various attack methods
   
   Usage: dehash <hash> [--online] [--wordlist <path>] [--strategy <auto|dictionary|hybrid|mask|brute>]
   
   Options:
   --online              Enable online hash database lookup
   --wordlist <path>     Use dictionary attack with specified wordlist
   --strategy            Specify attack strategy (default: auto)

\033[1;32m4. BRUTE - Brute Force Time Estimation\033[0m
   Purpose: Calculate theoretical brute-force attack time requirements
   
   Usage: brute <password> [--speed <n>]
   
   Options:
   --speed <number>      Cracking speed in attempts/second (default: 1000000)

\033[1;32m5. HASH - Password Hash Generation\033[0m
   Purpose: Generate cryptographic hashes for passwords
   
   Usage: hash <password> [--algorithm <md5|sha1|sha256|sha512>]

\033[1;33m══════════════════════════════════════════════════════════════════════════════\033[0m

\033[1;35mATTACK STRATEGIES:\033[0m

• Dictionary Attack: Uses pre-compiled wordlists of common passwords
• Brute Force: Systematically tries all possible character combinations  
• Hybrid Attack: Combines dictionary words with brute-force variations
• Mask Attack: Attacks based on known password patterns and masks

\033[1;35mEXAMPLES:\033[0m

  passaud strength "MyP@ssw0rd123"
  passaud dict 5d41402abc4b2a76b9719d911017c592 --wordlist rockyou.txt
  passaud dehash 5d41402abc4b2a76b9719d911017c592 --online
  passaud brute "password123" --speed 1000000
  passaud hash "secret" --algorithm sha256

For more information, visit: https://github.com/CYB3RLEO/PASSAUD
"""
    print(help_content)

def print_quick_guide():
    """Display quick usage guide."""
    print_banner()
    
    guide = """
\033[1;36mQUICK START GUIDE:\033[0m

\033[1;33mBasic Commands:\033[0m
  strength <password>          - Analyze password strength
  dict <target> --wordlist <file> - Dictionary attack
  dehash <hash>                - Deep de-hash analysis
  brute <password>             - Estimate brute-force time
  hash <password>              - Generate password hashes
  help                         - Show this quick guide
  manual                       - Show comprehensive manual

For detailed help: passaud --help
For comprehensive manual: passaud --manual
"""
    print(guide)