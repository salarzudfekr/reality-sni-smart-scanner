#!/usr/bin/env sh
set -eu

REPO="salarzudfekr/reality-sni-smart-scanner"
BRANCH="main"
INSTALL_DIR="${INSTALL_DIR:-$HOME/reality-sni-smart-scanner}"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
RAW_BASE="https://raw.githubusercontent.com/$REPO/$BRANCH"

echo "Installing Reality SNI Smart Scanner..."
echo "Install dir: $INSTALL_DIR"

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
fetch "$RAW_BASE/CHANGELOG.md" "$INSTALL_DIR/CHANGELOG.md"
fetch "$RAW_BASE/LICENSE" "$INSTALL_DIR/LICENSE"
fetch "$RAW_BASE/VERSION" "$INSTALL_DIR/VERSION"

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

echo ""
echo "Installed successfully."
echo "Run from anywhere:"
echo "  reality-sni-smart"
echo ""
echo "If the command is not found, add this to your shell profile:"
echo "  export PATH=\"$BIN_DIR:\$PATH\""
echo "Or run directly:"
echo "  python $INSTALL_DIR/reality_sni_smart.py"
