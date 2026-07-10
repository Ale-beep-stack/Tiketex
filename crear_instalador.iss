; Script de Inno Setup para crear el instalador
; Generador de Tickets - Instalador Automático

#define MyAppName "Generador de Tickets"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "TiketEx"
#define MyAppExeName "GeneradorTickets.exe"

[Setup]
; Información de la aplicación
AppId={{F4A2E8B6-9C3D-4F1E-8A7B-5D2C9E1F4A3B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Icono del instalador
SetupIconFile=disenos\raffle-ticket-blue.ico
; Directorio de salida
OutputDir=dist
OutputBaseFilename=GeneradorTickets_Instalador_v{#MyAppVersion}
; Compresión
Compression=lzma2/max
SolidCompression=yes
; Permisos
PrivilegesRequired=admin
; Interfaz
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un icono en el &escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
; Ejecutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Carpeta de diseños
Source: "disenos\*"; DestDir: "{app}\disenos"; Flags: ignoreversion recursesubdirs createallsubdirs

; Archivos de configuración (solo si no existen)
Source: "config.json"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "emisores.json"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "version.json"; DestDir: "{app}"; Flags: ignoreversion

; Crear carpeta de tickets vacía
Source: "tickets\.gitkeep"; DestDir: "{app}\tickets"; Flags: ignoreversion

[Icons]
; Icono en el menú inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"

; Icono en el escritorio
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Ejecutar la aplicación después de instalar
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Eliminar archivos generados por el usuario al desinstalar
Type: filesandordirs; Name: "{app}\tickets"
Type: filesandordirs; Name: "{app}\*.db"
Type: filesandordirs; Name: "{app}\*.log"

[Messages]
WelcomeLabel1=Bienvenido al Asistente de Instalación de [name]
WelcomeLabel2=Este programa instalará [name/ver] en su computadora.%n%nSe recomienda cerrar todas las demás aplicaciones antes de continuar.
FinishedLabel=La instalación de [name] se ha completado exitosamente.%n%nLa aplicación verificará automáticamente actualizaciones cada vez que se inicie.

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Crear archivo .gitkeep en carpeta tickets si no existe
    if not FileExists(ExpandConstant('{app}\tickets\.gitkeep')) then
      SaveStringToFile(ExpandConstant('{app}\tickets\.gitkeep'), '', False);
  end;
end;
