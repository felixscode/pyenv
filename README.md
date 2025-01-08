<div align="left">
<h1>Pyenv</h1>
    <img src="logo.webp" alt="Pyenv Logo" width="360" height="360">
</div>

A Python utility for managing virtual environments using the standard `venv` library for Linux users. This lightweight tool simplifies the creation, removal, and management of Python virtual environments. Its a wrapper around venv, witch manages venv access and locations.

## Features 🎯

- Create and manage isolated Python environments
- Simple command-line interface
- Built with standard library components
- Minimal dependencies (only requires `tomllib`)

## Installation 🛠️


Clone the repository:
   ```bash
   git clone <repository-url>
   cd pyenv
   chmod +x ./install.sh
   sudo ./install.sh
```
During installation you will be prompted for:

1. Binary location (e.g., /usr/local/bin/pyenv)
2. Virtual environments storage location (e.g., /home/user/.pyenvs)

The script will:
1. Check for Python 3 installation
2. Create necessary directories (optional)
3. Set up the executable script
4. Offer to add required paths to .bashrc

After installation:
```sh
source ~/.bashrc  # or restart your terminal
```
## Usage 🔧


The following commands are available:

```sh
# Create new environment
pyenv new myenv -

# Create a new environemt in a custom path and custom version
pyenv new myenv --version 3.9 --path /custom/path

# Remove environment
pyenv remove myenv

# List environments
pyenv list

# List environmets and filter after pattern
pyenv list --pattern "test.*"
```

## Requirements ⚙️
- Python 3.x
- Linux

## Contributions 😊

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

### Steps to contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License ⚖️

This project is licensed under the MIT License - see the LICENSE file for details.

## Author 👤

Felix Schelling<br>
GitHub: [felixscode](https://github.com/felixscode)<br>
Personal website: [felixschelling.de](https://felixschelling.de)<br>
Written with ❤️ in the 🏔️