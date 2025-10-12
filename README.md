# PASSAUD - Comprehensive User Manual

## Overview

PassAud is a high-performance password security analysis tool designed for security professionals, penetration testers, and system administrators. It combines multiple password auditing techniques with GPU acceleration and comprehensive reporting.

### Key Features:
- **Multi-Vector Password Analysis**: Strength testing, entropy calculation, pattern detection
- **Advanced Hash Cracking**: Dictionary, brute-force, hybrid, and mask attacks
- **GPU Acceleration**: OpenCL support for faster hash operations
- **Online Intelligence**: HIBP (Have I Been Pwned) integration
- **Rule-Based Transformations**: Advanced password mutation rules
- **Session Management**: Encrypted session storage and reporting
- **Interactive Shell**: Command-line interface with tab completion

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Basic Installation
```bash
# Clone the repository
git clone https://github.com/CYB3RLEO/PASSAUD.git
cd PASSAUD

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Install in normal mode
pip install .

# add 'sudo' for global install
sudo pip install .
```

### Docker Installation
```bash
# Build from source
docker build -t passaud .

# Run container
docker run -it -v $(pwd)/data:/app/data passaud --help
```

### Verification
```bash
# Test installation
passaud --help
```

## Quick Start

### Basic Password Analysis
```bash
# Analyze password strength
passaud strength "MyP@ssw0rd123"

# Generate password hash
passaud hash "secret" --algorithm sha256

# Estimate brute-force time
passaud brute "C0mpl3x!P@ss" --speed 1000000
```

### Interactive Mode
```bash
# Start interactive shell
passaud --interactive

# In interactive mode:
passaud> strength "test123"
passaud> hash "admin" --algorithm md5
passaud> manual  # Show comprehensive manual
passaud> exit
```

## Command Reference

### 1. Password Strength Analysis (`strength`)

**Purpose**: Comprehensive password security assessment

**Usage**:
```bash
passaud strength <password> [--json] [--verbose]
```

**Examples**:
```bash
# Basic analysis
passaud strength "password123"

# JSON output for scripting
passaud strength "Admin@2024" --json

# Verbose logging
passaud strength "SecureP@ss!" --verbose
```

**Output Analysis**:
- **Security Score**: 1-5 rating (5 = most secure)
- **Entropy**: Bits of entropy (60+ recommended)
- **Vulnerabilities**: Common issues found
- **Recommendations**: Improvement suggestions
- **Brute-force Estimate**: Theoretical cracking time

**Sample Output**:
```
Password: MyP@ssw0rd123
Strength: Strong (4/5)
Length: 14 characters
Entropy: 78.4 bits

VULNERABILITIES:
  - Sequential characters detected
  - Contains common name: password

RECOMMENDATIONS:
  - Avoid dictionary words
  - Use more special characters
```

### 2. Dictionary Attack (`dict`)

**Purpose**: Password cracking using wordlists

**Usage**:
```bash
passaud dict <target> --wordlist <path> [--hash-type <type>] [--max-words <n>] [--rules] [--threads <n>]
```

**Parameters**:
- `target`: Password or hash to crack
- `--wordlist`: Path to wordlist file (required)
- `--hash-type`: Specify hash algorithm (auto-detected if not provided)
- `--max-words`: Limit words tested (default: 100,000)
- `--rules`: Enable rule-based transformations
- `--threads`: Number of parallel threads

**Examples**:
```bash
# Crack plain password
passaud dict "secret123" --wordlist /usr/share/wordlists/rockyou.txt

# Crack MD5 hash
passaud dict "5d41402abc4b2a76b9719d911017c592" --wordlist wordlist.txt --hash-type md5

# With rules and threading
passaud dict "P@ssw0rd" --wordlist common.txt --rules --threads 8 --max-words 50000
```

**Supported Wordlists**:
- RockYou (commonly used)
- SecLists collection
- Custom wordlists
- Rule files (John the Ripper compatible)

### 3. Deep Hash Cracking (`dehash`)

**Purpose**: Multi-stage hash cracking with intelligent strategy selection

**Usage**:
```bash
passaud dehash <hash> [--online] [--wordlist <path>] [--max-words <n>] [--strategy <type>]
```

**Parameters**:
- `hash`: Hash value to crack
- `--online**: Enable HIBP database lookup
- `--wordlist**: Custom wordlist path
- `--max-words**: Dictionary size limit
- `--strategy**: Attack strategy (auto/dictionary/hybrid/mask/brute)

**Attack Strategy Flow**:
1. **Hash Type Detection** (auto)
2. **Common Passwords** (top 1000)
3. **HIBP Lookup** (if enabled and SHA1)
4. **Dictionary Attack** (if wordlist provided)
5. **Hybrid Attack** (dictionary + variations)
6. **Limited Brute-force** (short hashes only)

**Examples**:
```bash
# Automatic cracking
passaud dehash "5d41402abc4b2a76b9719d911017c592"

# With online lookup
passaud dehash "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d" --online

# Custom strategy and wordlist
passaud dehash "e10adc3949ba59abbe56e057f20f883e" --wordlist rockyou.txt --strategy hybrid
```

### 4. Brute-force Estimation (`brute`)

**Purpose**: Calculate theoretical brute-force attack requirements

**Usage**:
```bash
passaud brute <password> [--speed <n>] [--json]
```

**Parameters**:
- `password`: Password to analyze
- `--speed**: Cracking speed in attempts/second (default: 1,000,000)
- `--json**: JSON output format

**Examples**:
```bash
# Basic estimation
passaud brute "password123"

# High-speed cracking scenario
passaud brute "C0mpl3x!P@ss" --speed 10000000

# JSON output for analysis
passaud brute "Test@2024" --json
```

**Output Includes**:
- Time estimate (seconds to centuries)
- Total possible combinations
- Character set analysis
- Cracking feasibility assessment

### 5. Hash Generation (`hash`)

**Purpose**: Generate cryptographic hashes for passwords

**Usage**:
```bash
passaud hash <password> [--algorithm <type>] [--json]
```

**Supported Algorithms**:
- `md5`, `sha1`, `sha256`, `sha384`, `sha512`
- `bcrypt`, `scrypt`, `argon2`
- `pbkdf2_sha256`

**Examples**:
```bash
# MD5 hash
passaud hash "password" --algorithm md5

# Secure hash with bcrypt
passaud hash "secret" --algorithm bcrypt

# Multiple algorithms comparison
for algo in md5 sha1 sha256 bcrypt; do
    echo "$algo: $(passaud hash "test" --algorithm $algo)"
done
```

### 6. Session Management

**Purpose**: Save and restore analysis sessions

**Usage**:
```bash
# Save current session
passaud --session my_session.enc strength "password123"
passaud dict "target" --wordlist wordlist.txt --session my_session.enc

# Generate report from session
passaud --session my_session.enc report --format text

# Interactive session management
passaud --interactive
passaud> save_session analysis.enc
passaud> load_session previous.enc
passaud> report --format json
```

## Attack Strategies

### 1. Dictionary Attack
- **Method**: Pre-compiled wordlists
- **Best For**: Common passwords, default credentials
- **Performance**: Fastest method
- **Tools**: RockYou, SecLists, custom wordlists

### 2. Brute-force Attack
- **Method**: Systematic character combinations
- **Best For**: Short passwords, known patterns
- **Performance**: Computationally intensive
- **Optimization**: GPU acceleration, character set reduction

### 3. Hybrid Attack
- **Method**: Dictionary words with appended/prepended characters
- **Best For**: Modified common passwords
- **Examples**: "password123", "123admin", "Welcome2024"

### 4. Mask Attack
- **Method**: Pattern-based generation
- **Best For**: Known password policies
- **Patterns**: 
  - `?l` = lowercase
  - `?u` = uppercase  
  - `?d` = digits
  - `?s` = special characters
- **Example**: `?l?l?l?l?d?d?d?d` = 4 letters + 4 digits

### 5. Rule-based Attack
- **Method**: Transform dictionary words using rules
- **Rules**: Case variations, leet speak, appending, prepending
- **Custom Rules**: John the Ripper compatible syntax

## Configuration

### Configuration File
Location: `~/.passaud.conf`

**Example Configuration**:
```ini
[DEFAULT]
api_timeout = 10
max_threads = 8
max_words = 100000
request_delay = 1.5
store_sensitive_data = false
max_requests_per_minute = 30
gpu_enabled = true
batch_size = 1000
max_bruteforce_length = 8
log_level = INFO
log_file = passaud.log

[API_KEYS]
hibp_api_key = your_hibp_api_key_here
custom_api_key = your_custom_key

[PATHS]
wordlists_dir = /usr/share/wordlists
sessions_dir = ./sessions
reports_dir = ./reports
```

### Environment Variables
```bash
export PASSAUD_HIBP_API_KEY="your_key"
export PASSAUD_MAX_THREADS="8"
export PASSAUD_LOG_LEVEL="DEBUG"
export PASSAUD_GPU_ENABLED="true"
```

## Advanced Usage

### Custom Wordlists
```bash
# Generate custom wordlist
crunch 6 8 0123456789abcdef -o custom_wordlist.txt

# Use multiple wordlists
cat wordlist1.txt wordlist2.txt > combined.txt
passaud dict "target" --wordlist combined.txt

# Rule-based transformations
passaud dict "hash_value" --wordlist base.txt --rules
```

### GPU Acceleration
```bash
# Check GPU support
passaud --verbose strength "test"

# Force CPU-only mode
export PASSAUD_GPU_ENABLED="false"

# Custom OpenCL device
export PYOPENCL_CTX="0:0"  # Use first device of first platform
```

### Batch Processing
```bash
# Process multiple hashes from file
echo -e "hash1\nhash2\nhash3" > hashes.txt
while read hash; do
    passaud dehash "$hash" --wordlist rockyou.txt >> results.txt
done < hashes.txt

# Parallel processing with GNU parallel
parallel -j 4 "passaud dehash {} --wordlist wordlist.txt" :::: hashes.txt
```

### Integration with Other Tools
```bash
# John the Ripper integration
john --wordlist=password.lst --rules --stdout | passaud dict "target" --wordlist -

# Hashcat rule conversion
python rules_convert.py john.rules passaud.rules
passaud dict "target" --wordlist wordlist.txt --rule-file passaud.rules
```

## Troubleshooting

### Common Issues

**1. "Command not found"**
```bash
# Reinstall in development mode
pip install -e .

# Check PATH
which passaud

# Run directly
python -m passaud.cli.main --help
```

**2. GPU Acceleration Not Working**
```bash
# Check OpenCL installation
python -c "import pyopencl; print(pyopencl.get_platforms())"

# Install GPU drivers
# NVIDIA: nvidia-opencl-icd
# AMD: rocm-opencl-runtime
# Intel: intel-opencl-icd

# Force CPU mode
export PASSAUD_GPU_ENABLED="false"
```

**3. HIBP API Errors**
```bash
# Check API key
cat ~/.passaud.conf | grep hibp_api_key

# Test API connectivity
curl -H "hibp-api-key: YOUR_KEY" "https://api.pwnedpasswords.com/range/5BAA6"

# Use without API key (rate limited)
passaud dehash "hash" --online
```

**4. Memory Issues with Large Wordlists**
```bash
# Use streaming mode
passaud dict "target" --wordlist large_list.txt --max-words 100000

# Increase swap space
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo mkswap /swapfile
sudo swapon /swapfile
```

**5. Performance Optimization**
```bash
# Use faster storage (SSD)
passaud --session /ssd/session.enc strength "test"

# Adjust thread count
passaud dict "target" --wordlist list.txt --threads $(nproc)

# Batch size tuning
export PASSAUD_BATCH_SIZE="5000"
```

### Debug Mode
```bash
# Enable verbose logging
passaud --verbose --log-file debug.log strength "password"

# Debug specific component
export PASSAUD_LOG_LEVEL="DEBUG"
passaud dehash "hash" --online

# Profile performance
python -m cProfile -o profile.stats -m passaud.cli.main strength "test"
```

## Security Considerations

### Legal and Ethical Use
- **Authorized Testing Only**: Use only on systems you own or have explicit permission to test
- **Corporate Policies**: Follow organizational security testing policies
- **Legal Compliance**: Adhere to local computer crime laws
- **Responsible Disclosure**: Report vulnerabilities to appropriate parties

### Data Protection
- **Session Encryption**: All sessions are AES-encrypted
- **Memory Security**: Sensitive data cleared from memory
- **No Data Collection**: Tool does not phone home or collect usage data
- **Local Processing**: All analysis happens locally

### Best Practices
```bash
# Secure session handling
passaud --session /encrypted/drive/session.enc strength "password"

# Clean up sensitive files
shred -u session.enc
rm -P sensitive_files.txt

# Use secure protocols
ssh -C user@target "passaud strength 'password'"
```


## Supported Platforms

- ✅ **Linux** (Ubuntu, Kali, Debian, CentOS)
- ✅ **Windows** (10/11 with Python 3.8+)
- ✅ **macOS** (10.14+ with Intel/Apple Silicon)
- ✅ **Docker** (Multi-architecture images)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This tool is for authorized security testing and educational purposes only. Users are responsible for complying with all applicable laws. Unauthorized use against systems you don't own is illegal.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- 🐛 [Issue Tracker](https://github.com/CYB3RLEO/PASSAUD/issues)
- 💬 [Discussions](https://github.com/CYB3RLEO/PASSAUD/discussions)
- 📧 Email: [abdulazeezhibullahikolade@gmail.com]

---

**Created by CYB3RLEO** | [GitHub Profile](https://github.com/CYB3RLEO)
```
