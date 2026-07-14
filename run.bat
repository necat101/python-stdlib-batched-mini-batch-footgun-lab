@echo off
setlocal EnableDelayedExpansion

REM interpreter discovery: %PYTHON_BIN%, python3.14, python3.13, python3.12, python3, python
set "PYTHON_BIN="
if defined PYTHON_BIN_ENV set "PYTHON_BIN=%PYTHON_BIN_ENV%"

if not defined PYTHON_BIN (
  where python3.14 >nul 2>&1 && set "PYTHON_BIN=python3.14"
)
if not defined PYTHON_BIN (
  where python3.13 >nul 2>&1 && set "PYTHON_BIN=python3.13"
)
if not defined PYTHON_BIN (
  where python3.12 >nul 2>&1 && set "PYTHON_BIN=python3.12"
)
if not defined PYTHON_BIN (
  where python3 >nul 2>&1 && set "PYTHON_BIN=python3"
)
if not defined PYTHON_BIN (
  where python >nul 2>&1 && set "PYTHON_BIN=python"
)

if not defined PYTHON_BIN (
  echo error: no python interpreter found ^(tried python3.14, python3.13, python3.12, python3, python^) >&2
  exit /b 1
)

echo Using: %PYTHON_BIN%
%PYTHON_BIN% --version
echo.

%PYTHON_BIN% -m py_compile run_lab.py test_lab.py
if errorlevel 1 exit /b 1

%PYTHON_BIN% run_lab.py
if errorlevel 1 exit /b 1

echo.
%PYTHON_BIN% -m unittest -v
