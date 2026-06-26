#!/usr/bin/env sh
set -eu

REPO="salarzudfekr/reality-sni-smart-scanner"
BRANCH="main"
INSTALL_DIR="${INSTALL_DIR:-$HOME/reality-sni-smart-scanner}"
RAW_BASE="https://raw.githubusercontent.com/$REPO/$BRANCH"

choose_bin_dir() {
  if [ -n "${BIN_DIR:-}" ]; then
    printf '%s\n' "$BIN_DIR"
    return
  fi

  # Termux keeps this directory in PATH by default, so prefer it when writable.
  if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX/bin" ] && [ -w "$PREFIX/bin" ]; then
    printf '%s\n' "$PREFIX/bin"
    return
  fi

  case ":$PATH:" in
    *":$HOME/.local/bin:"*) printf '%s\n' "$HOME/.local/bin" ;;
    *) printf '%s\n' "$HOME/.local/bin" ;;
  esac
}

BIN_DIR="$(choose_bin_dir)"
RAW_BASE="https://raw.githubusercontent.com/$REPO/$BRANCH"

echo "Installing Reality SNI Smart Scanner..."
echo "Install dir: $INSTALL_DIR"
echo "Command dir: $BIN_DIR"

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

fetch() {
  src="$1"
  dst="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$src" -o "$dst"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$dst" "$src"
  else
    echo "Error: curl or wget is required." >&2
    exit 1
  fi
}

fetch "$RAW_BASE/reality_sni_smart.py" "$INSTALL_DIR/reality_sni_smart.py"
fetch "$RAW_BASE/README.md" "$INSTALL_DIR/README.md"
fetch "$RAW_BASE/README.fa.md" "$INSTALL_DIR/README.fa.md"
fetch "$RAW_BASE/CHANGELOG.md" "$INSTALL_DIR/CHANGELOG.md"
fetch "$RAW_BASE/LICENSE" "$INSTALL_DIR/LICENSE"
fetch "$RAW_BASE/VERSION" "$INSTALL_DIR/VERSION"
fetch "$RAW_BASE/domains.example.txt" "$INSTALL_DIR/domains.example.txt"

chmod +x "$INSTALL_DIR/reality_sni_smart.py" 2>/dev/null || true
cat > "$BIN_DIR/reality-sni-smart" <<EOF
#!/usr/bin/env sh
python "$INSTALL_DIR/reality_sni_smart.py" "\$@"
EOF
chmod +x "$BIN_DIR/reality-sni-smart"

if command -v python >/dev/null 2>&1; then
  python -m py_compile "$INSTALL_DIR/reality_sni_smart.py"
elif command -v python3 >/dev/null 2>&1; then
  python3 -m py_compile "$INSTALL_DIR/reality_sni_smart.py"
else
  echo "Warning: Python was not found. Install Python before running the scanner." >&2
fi

path_note=""
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    profile="$HOME/.profile"
    if [ -n "${PREFIX:-}" ]; then
      profile="$HOME/.bashrc"
    fi
    marker='export PATH="$HOME/.local/bin:$PATH"'
    if [ "$BIN_DIR" = "$HOME/.local/bin" ] && ! grep -qsF "$marker" "$profile"; then
      printf '\n# Reality SNI Smart Scanner\n%s\n' "$marker" >> "$profile"
      path_note="Added $HOME/.local/bin to PATH in $profile. Restart the shell or run: . $profile"
    else
      path_note="Note: $BIN_DIR is not currently in PATH. Run directly with: $BIN_DIR/reality-sni-smart"
    fi
    ;;
esac

echo ""
echo "Installed successfully."
if command -v reality-sni-smart >/dev/null 2>&1; then
  echo "Run from anywhere:"
  echo "  reality-sni-smart"
else
  echo "Run now:"
  echo "  $BIN_DIR/reality-sni-smart"
  if [ -n "$path_note" ]; then
    echo "$path_note"
  fi
fi
echo "Or run directly:"
echo "  python $INSTALL_DIR/reality_sni_smart.py"
