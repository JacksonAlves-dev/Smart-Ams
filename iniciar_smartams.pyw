# iniciar_smartams.pyw
import os, subprocess, sys, time, webbrowser

base = os.path.dirname(os.path.abspath(__file__))

# Prioriza o Python embutido da pasta runtime se existir
runtime_python = os.path.join(base, "runtime", "python.exe")
python_exe = runtime_python if os.path.exists(runtime_python) else sys.executable

log = open(os.path.join(base, "smartams.log"), "a", encoding="utf-8")

# O argumento creationflags=0x08000000 (CREATE_NO_WINDOW) oculta a janela do prompt mesmo usando python.exe
CREATE_NO_WINDOW = 0x08000000

subprocess.Popen(
    [python_exe, "-m", "streamlit", "run", "SmartAms.py",
     "--server.headless", "true",
     "--server.port", "8501",
     "--browser.gatherUsageStats", "false"],
    cwd=base,
    stdout=log,
    stderr=log,
    creationflags=CREATE_NO_WINDOW,
)

time.sleep(4)
webbrowser.open("http://localhost:8501")