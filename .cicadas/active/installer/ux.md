# UX Spec — Installer

## Command Surface

### Bootstrap (nothing pre-installed)
```bash
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash
```

### Local invocation (after download)
```bash
bash install.sh [options]
```

### Flags
```
--dir <path>        Install location (default: src/cicadas/)
--agent <list>      Agent integrations, comma-separated (default: prompt user)
                    Supported: claude-code, antigravity, cursor, none
--update            Re-download and overwrite skill files only; never touch .cicadas/
```

### Examples
```bash
# Default install with interactive agent prompt
bash install.sh

# Install to custom directory
bash install.sh --dir tools/cicadas

# Install with Claude Code integration
bash install.sh --agent claude-code

# Install with multiple agents
bash install.sh --agent claude-code,cursor

# Update Cicadas files only (preserve .cicadas/)
bash install.sh --update

# Skip agent setup
bash install.sh --agent none
```

## Interactive Prompt (when no --agent flag)

```
Which AI coding agents are you using? (comma-separated, or 'none')
  Supported: claude-code, antigravity, cursor
>
```

## Output Format

Progress lines prefixed with status indicators:
```
[cicadas] Checking Python version...
[cicadas] ✓ Python 3.13.2 found
[cicadas] Downloading Cicadas...
[cicadas] ✓ Downloaded and extracted to src/cicadas/
[cicadas] Initializing .cicadas/ workspace...
[cicadas] ✓ Workspace initialized
[cicadas] Setting up claude-code integration...
[cicadas] ✓ .claude/skills/cicadas → src/cicadas/
[cicadas]
[cicadas] Installation complete!
[cicadas] Next steps:
[cicadas]   python src/cicadas/scripts/status.py
```

## Error Output

Python not found or too old:
```
[cicadas] ✗ Python 3.13+ required (found: 3.11.2)
[cicadas]
[cicadas] Install Python 3.13:
[cicadas]   macOS:   brew install python@3.13
[cicadas]   Ubuntu:  sudo apt install python3.13
[cicadas]   Windows: winget install Python.Python.3.13
[cicadas]            (or use WSL)
[cicadas]
[cicadas] Then re-run this installer.
```

Not in a git repo:
```
[cicadas] ✗ No git repository found. Run 'git init' first.
```
