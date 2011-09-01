@echo off
echo.

IF "%PYTHON%" == "" (
    echo you must define PYTHON environment variable.
    GOTO :END
)
echo PYTHON is %PYTHON%

IF "%PYTHONPATH%" == "" (
    echo you must define PYTHONPATH environment variable.
    GOTO :END
)
set PYTHONPATH=%PYTHONPATH%;%cd%\RAS\face;%cd%\extern\pyvision_0.9.0\src;
echo PYTHONPATH is %PYTHONPATH%

IF NOT "%HOME%" == "" (IF EXIST "%HOME%\.lightHead.conf" set LIGHTHEAD=%HOME%\.lightHead.conf)
IF "%LIGHTHEAD%" == "" set LIGHTHEAD=common\lightHead.conf
echo LIGHTHEAD is %LIGHTHEAD%

rem lightHead.exe
 lightHead-window.exe
rem HALA-window.exe
rem GIZMO.exe
:END
pause
