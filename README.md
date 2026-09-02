# I2PConverter (Images to PDF & DOCX Converter)

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)

**I2PConverter** by GamesBondGIT is a modern, lightweight, desktop application that rapidly compiles folders of images (Posters & Video Thumbnails) into perfectly gridded, professional PDF and Microsoft Word (.docx) reports. 

## ✨ Features

- **Dual Output Formats**: Generate PDF and DOCX reports simultaneously.
- **Smart Directory Parsing**: Automatically categorizes images into "Posters" and "Videos" if they are inside a `VideoThumbs` directory.
- **Sleek Dark Mode UI**: Beautifully designed interface using `customtkinter`.
- **Advanced Grid Layouts**: Control the row/column count for Posters and Videos separately via the built-in Settings menu.
- **Optimized Engine**: Intelligently scales massive images behind the scenes to prevent memory crashes and keep document sizes lightweight.
- **Memory Safety**: Uses background threading and chunked streaming to prevent GUI freezes during generation.
- **Portable Settings**: Configurations are saved to the user's local `%APPDATA%` directory, ensuring compatibility with packaged Windows installers.

## 📂 Expected Directory Structure

The application expects your source directory to contain raw images (Posters) and a sub-folder containing Video Thumbnails.

```text
C:/Users/You/Downloads/Content/
│
├── Poster1.jpg
├── Poster2.png
│
└── VideoThumbs/
    ├── Video1_thumbnail.jpg
    └── Video2_thumbnail.png
```

## 🚀 Running from Source

### Prerequisites
Make sure you have Python 3.8+ installed.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/I2PConverter.git
   cd I2PConverter
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## 📦 Building the Standalone Installer

To compile the application into a standalone Windows installer (`setup.exe`) so users do not need Python:

1. **Compile the EXE using PyInstaller**:
   ```bash
   python -m PyInstaller -y --noconsole --name "I2PConverter" --icon "I2PConverterIcon.ico" --collect-all customtkinter app.py
   ```
   *This will generate a `dist/I2PConverter` directory containing the application and all dependencies.*

2. **Generate the Installer (`setup.exe`)**:
   - Install **Inno Setup**.
   - Open the included `installer.iss` file.
   - Click **Compile**.
   - Your final `I2PConverter_Setup.exe` will be located in the `InstallerOutput` folder!

## ⚙️ Configuration
By default, I2PConverter reads and writes preferences to:
`%APPDATA%\Images2PDF\settings.json`

This ensures that user settings persist across sessions without requiring Administrator privileges to modify files in the `Program Files` directory.

## 📝 License
This project is open-source and available under the MIT License.
