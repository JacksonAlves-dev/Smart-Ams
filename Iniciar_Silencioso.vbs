Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")

baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = baseDir

pythonExe = baseDir & "\runtime\pythonw.exe"
If Not fso.FileExists(pythonExe) Then
    pythonExe = "pythonw.exe"
End If

scriptPath = baseDir & "\iniciar_smartams.pyw"

WshShell.Run """" & pythonExe & """ """ & scriptPath & """", 0, False

