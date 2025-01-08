#!/bin/bash

# Set PYENV_ROOT to current directory
PYENV_ROOT=$(pwd)

# Check if src folder exists
if [ ! -d "$PYENV_ROOT/src" ]; then
    echo "Error: src folder not found in current directory. Please run this script from the correct location."
    exit 1
fi

# Ask for remaining destinations
echo "Please provide the following information:"
read -p "1. Bin location and name (e.g., /usr/local/bin/pyenv): " PYENV_BIN
read -p "2. Location to store virtual environments (e.g., /home/user/.venvs): " VENV_PATH

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 to continue."
    exit 1
fi

# Confirm creation of directories
read -p "Do you want to create the necessary directories if they don't exist? (y/n): " CREATE_DIRS
if [[ $CREATE_DIRS =~ ^[Yy]$ ]]; then
    mkdir -p "$(dirname "$PYENV_BIN")"
    mkdir -p "$VENV_PATH/bin"
fi

# Create execution script in bin location
cat > "$PYENV_BIN" << 'EOL'
#!/bin/bash
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
REPO_ROOT="PYENV_ROOT_PLACEHOLDER"

python3 "$REPO_ROOT/src/pyenv.py" "$@"
EOL

# Replace placeholder with actual PYENV_ROOT
sed -i "s|PYENV_ROOT_PLACEHOLDER|$PYENV_ROOT|g" "$PYENV_BIN"

# Make executable
chmod +x "$PYENV_BIN"

# Ask to add to .bashrc
read -p "Do you want to add VENV_PATHS to your .bashrc? (y/n): This is necessary to activate the venv via an alias " ADD_TO_BASHRC
if [[ $ADD_TO_BASHRC =~ ^[Yy]$ ]]; then
    echo "" >> ~/.bashrc
    echo "# Pyenv configuration" >> ~/.bashrc
    echo "export PATH=\"$VENV_PATH/bin:\$PATH\"" >> ~/.bashrc
    echo "Added paths to .bashrc. Please restart your terminal or run 'source ~/.bashrc'"
fi