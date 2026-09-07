; Inno Setup script for the Windows installer.
;
; The installer, rather than a bare executable, is what makes this maintainable:
; it creates the Start Menu and desktop shortcuts a non-technical user needs to
; find the program, registers an entry in "Add or remove programs", and -- the
; reason it matters most -- can be re-run silently by the built-in updater to
; replace an existing installation without anybody touching a file.
;
; Installs per user, into %LOCALAPPDATA%: a school laptop's account rarely has
; the administrator rights that Program Files demands, and a UAC prompt is one
; more place for a teacher to stop.

#define AppName "Horarios"
#define AppPublisher "Antonio Mancera Gamez"
#define AppUrl "https://github.com/manceras/horarios-escolares-manager"
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{8D3C1F42-6A1E-4C7B-9E52-5F0B7A2D9C31}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppUrl}
AppSupportURL={#AppUrl}/issues
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=Horarios-Setup-{#AppVersion}
SetupIconFile=horarios.ico
UninstallDisplayIcon={app}\Horarios.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; The school is Spanish; the wizard should be too.
ShowLanguageDialog=no
; Lets the silent updater close a running copy and start it again afterwards.
CloseApplications=yes
RestartApplications=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\Horarios\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\Horarios.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\Horarios.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Horarios.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

; Deliberately absent: an [UninstallDelete] entry for %LOCALAPPDATA%\Horarios.
; Uninstalling the program must never delete the school's timetables. They stay
; until somebody deletes that folder on purpose.
