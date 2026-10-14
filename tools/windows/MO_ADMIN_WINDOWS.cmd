@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 --version >nul 2>nul
if not errorlevel 1 (
  py -3 MO_ADMIN.py
  goto :done
)
python --version >nul 2>nul
if not errorlevel 1 (
  python MO_ADMIN.py
  goto :done
)
echo Máy chưa có Python. Cài Python 3 từ https://www.python.org/downloads/windows/
echo Chọn Add python.exe to PATH, rồi mở lại MO_ADMIN_WINDOWS.cmd.
:done
pause
