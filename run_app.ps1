$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$venvPath = Join-Path $scriptDir ".venv"
$pythonExe = Join-Path $venvPath "Scripts/python.exe"

if (-not (Test-Path $pythonExe)) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv $venvPath
    }
    elseif (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.11 -m venv $venvPath
    }
    else {
        throw "Python was not found. Install Python 3.11 and try again."
    }
}

if (-not (Test-Path $pythonExe)) {
    throw "Virtual environment could not be created."
}

& $pythonExe -m pip install --upgrade pip setuptools wheel | Out-Null
& $pythonExe -m pip install -r requirements.txt | Out-Null
& $pythonExe -m streamlit run excel_gen.py
