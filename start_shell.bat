@echo off
echo.
IF "%PYTHON%" == "" (echo you must define PYTHON environment variable.) ELSE (
%PYTHON% utils\readline_client.py localhost 4242 )
pause