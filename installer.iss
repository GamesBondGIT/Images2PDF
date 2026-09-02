[Setup]
; Basic Application Metadata
AppName=I2PConverter
AppVersion=1.0
AppPublisher=GamesBondGIT
AppId={{I2PCONVERTER-B1A2-4321-9C3E-A5B6C7D8E9F0}

; Description shown during install
AppCopyright=2026
AppComments=Converts images to PDF and DOCX formats automatically.

; Default Install Path (C:\Program Files\I2PConverter)
DefaultDirName={autopf}\I2PConverter
DefaultGroupName=I2PConverter

; Output Installer EXE setup
OutputDir=.\InstallerOutput
OutputBaseFilename=I2PConverter_Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=I2PConverterIcon.ico

[Files]
; Copy all the files from the PyInstaller dist output directory
Source: "dist\I2PConverter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "I2PConverterIcon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Icon
Name: "{group}\I2PConverter"; Filename: "{app}\I2PConverter.exe"; WorkingDir: "{app}"; IconFilename: "{app}\I2PConverterIcon.ico"
; Desktop Icon
Name: "{autodesktop}\I2PConverter"; Filename: "{app}\I2PConverter.exe"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\I2PConverterIcon.ico"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
; Option to launch the app immediately after install finishes
Filename: "{app}\I2PConverter.exe"; Description: "Launch I2PConverter"; Flags: nowait postinstall skipifsilent
