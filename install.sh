#!/bin/sh
set -e

detect_pm() {
    if command -v apt >/dev/null 2>&1; then
        echo "apt"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    elif command -v yum >/dev/null 2>&1; then
        echo "yum"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper"
    else
        echo "apt"
    fi
}

PM=$(detect_pm)

install_pkg() {
    PKG="$1"
    case "$PM" in
        apt) apt update && apt install -y "$PKG" ;;
        dnf) dnf install -y "$PKG" ;;
        yum) yum install -y "$PKG" ;;
        pacman) pacman -Sy --noconfirm "$PKG" ;;
        zypper) zypper install -y "$PKG" ;;
        *) echo "Unsupported package manager. Please install $PKG manually."; exit 1 ;;
    esac
}

wget -O main.py https://raw.githubusercontent.com/funterminal/FireWiki/refs/heads/main/src/main.py

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    install_pkg python3 || install_pkg python
fi

SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    bash) CONF_FILE="$HOME/.bashrc" ;;
    zsh) CONF_FILE="$HOME/.zshrc" ;;
    sh) CONF_FILE="$HOME/.profile" ;;
    fish) CONF_FILE="$HOME/.config/fish/config.fish" ;;
    *) CONF_FILE="$HOME/.profile" ;;
esac

if [ "$SHELL_NAME" = "fish" ]; then
    if ! grep -q "alias firewiki" "$CONF_FILE" 2>/dev/null; then
        echo "alias firewiki 'python3 $(pwd)/main.py'" >> "$CONF_FILE"
    fi
else
    if ! grep -q "alias firewiki=" "$CONF_FILE" 2>/dev/null; then
        echo "alias firewiki='python3 $(pwd)/main.py'" >> "$CONF_FILE"
    fi
fi

. "$CONF_FILE"
