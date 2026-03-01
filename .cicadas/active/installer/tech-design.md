# Tech Design — Installer

## Architecture

### Installer: `install.sh`

Single bash script in the project root (`/install.sh`). No build step, no dependencies beyond `bash`, `curl`, and `unzip`.

### Distribution

Raw GitHub archive URL (no releases needed):
```
https://github.com/ecodan/cicadas/archive/refs/heads/master.zip
```

Extracted archive dir: `cicadas-master/` → renamed to `--dir` target (default: `src/cicadas/`).

### Components

```
install.sh          # Entrypoint; parses flags, orchestrates steps
```

No additional Python scripts. The shell script calls existing `src/cicadas/scripts/init.py` after extraction.

## Python Check

```bash
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    # print guidance, exit 1
fi
VERSION=$("$PYTHON" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
MAJOR=$(echo "$VERSION" | cut -d. -f1)
MINOR=$(echo "$VERSION" | cut -d. -f2)
if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 13 ]); then
    # print guidance, exit 1
fi
```

OS detection for install guidance:
```bash
case "$(uname -s)" in
  Darwin)  INSTALL_CMD="brew install python@3.13" ;;
  Linux)   INSTALL_CMD="sudo apt install python3.13" ;;
  *)       INSTALL_CMD="See https://python.org/downloads" ;;
esac
```

## Download & Extract

```bash
ARCHIVE_URL="https://github.com/ecodan/cicadas/archive/refs/heads/master.zip"
TMP_DIR=$(mktemp -d)
curl -fsSL "$ARCHIVE_URL" -o "$TMP_DIR/cicadas.zip"
unzip -q "$TMP_DIR/cicadas.zip" -d "$TMP_DIR"
mkdir -p "$(dirname "$INSTALL_DIR")"
# Copy only the skill files (scripts/, emergence/, templates/, skill.md, etc.)
cp -r "$TMP_DIR/cicadas-master/src/cicadas/." "$INSTALL_DIR/"
rm -rf "$TMP_DIR"
```

## Init

```bash
"$PYTHON" "$INSTALL_DIR/scripts/init.py"
```

If `.cicadas/` already exists (update scenario), `init.py` is idempotent — it won't overwrite existing state.

## --update Flag

Re-runs download + extraction step only. Skips:
- Python check (already confirmed working)
- `init.py` (`.cicadas/` must not be touched)
- Agent setup (integrations already exist)

## Agent Integrations

### claude-code
```bash
mkdir -p .claude/skills
ln -sf "$(realpath "$INSTALL_DIR")" .claude/skills/cicadas
# or relative symlink for portability:
ln -sf "../../$INSTALL_DIR" .claude/skills/cicadas
```

### antigravity
```bash
mkdir -p .agents/skills
ln -sf "../../$INSTALL_DIR" .agents/skills/cicadas
```

### cursor
```bash
mkdir -p .cursor/rules
cp "$INSTALL_DIR/skill.md" .cursor/rules/cicadas.mdc
```

## Git Repo Check

```bash
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "[cicadas] ✗ No git repository found. Run 'git init' first."
    exit 1
fi
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Fatal error (Python missing/old, no git repo, download failed) |

## Constraints

- Bash only (no `zsh`-specific features)
- Must work with `bash install.sh` and `curl ... | bash`
- `curl | bash` means stdin is the script, so no `read` for interactive prompts when piped — detect with `[ -t 0 ]`
- Relative symlinks (portable across machines that mount the repo at different paths)
