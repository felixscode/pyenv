#!/bin/bash

# Set PYENV_ROOT to current directory
PYENV_ROOT=$(pwd)

# Check if src folder exists
if [ ! -d "$PYENV_ROOT/src" ]; then
    echo "Error: src folder not found in current directory. Please run this script from the correct location."
    exit 1
fi
# Check if the script is run with sudo privileges
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run with sudo privileges."
    exit 1
fi



# Ask for remaining destinations
echo "Please provide the following information:"
read -p "1. Bin location and name (default: /usr/local/bin/pyenv): " PYENV_BIN
PYENV_BIN=${PYENV_BIN:-/usr/local/bin/pyenv}
read -p "2. Location to store virtual environments (default: /home/$USER/.pyenvs): " VENV_PATH
VENV_PATH=${VENV_PATH:-/home/$USER/.pyenvs}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 to continue."
    exit 1
fi

# Confirm creation of directories
read -p "Do you want to create the necessary directories if they don't exist? (Y/n): " CREATE_DIRS
CREATE_DIRS=${CREATE_DIRS:-Y}
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
read -p "Do you want to add VENV_PATHS to your .bashrc? (Y/n): This is necessary to activate the venv via an alias " ADD_TO_BASHRC
ADD_TO_BASHRC=${ADD_TO_BASHRC:-Y}
if [[ $ADD_TO_BASHRC =~ ^[Yy]$ ]]; then
    echo "" >> /home/$USER/.bashrc
    echo "# Pyenv configuration" >> /home/$USER/.bashrc
    echo "export PATH=\"$VENV_PATH/bin:\$PATH\"" >> /home/$USER/.bashrc
    echo "Added paths to .bashrc. Please restart your terminal or run 'source ~/.bashrc'"

fi