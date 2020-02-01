@echo off
@echo Checking for pipenv...
@echo.


pip --disable-pip-version-check list | findstr pipenv > tmpFile 
set /p myvar= < tmpFile 
del tmpFile 

if "%myvar%" == "" GOTO InstallPipenv
GOTO Run

:InstallPipenv

@echo pipenv not found, installing...
@echo.

pip install pipenv
@echo.

:Run

@echo Checking dependencies...
@echo.

pipenv install > tmpFile 
del tmpFile 

@echo.
@echo Done, launching bot
@echo.

pipenv run python "main.py"
pause