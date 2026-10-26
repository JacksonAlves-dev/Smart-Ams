; Script do Inno Setup para compilar o Smart AMS em um instalador .exe unico
; Baixe o Inno Setup gratuitamente em: https://jrsoftware.org/isdl.php

#define MyAppName "Smart AMS - Agente L1"
#define MyAppVersion "1.0"
#define MyAppPublisher "Softtek"
#define MyAppExeName "Iniciar_SmartAMS.bat"

[Setup]
AppId={{E65A4930-B11B-4E38-9B21-0D4A06A3E39F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SmartAMS
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=Instalador_SmartAMS_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Inclui todos os arquivos e subpastas do projeto
Source: "*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "dist,*.log"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Encerrar Smart AMS"; Filename: "{app}\Parar_SmartAMS.bat"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: shellexec postinstall nowait skipifsilent

