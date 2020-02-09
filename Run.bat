@echo off
@echo Checking for pipenv...


pip --disable-pip-version-check list | findstr pipenv > tmpFile 
set /p myvar= < tmpFile 
del tmpFile 

@echo. Loading bot
@echo. 

if "%myvar%" == "" GOTO InstallPipenv
GOTO Run

:InstallPipenv
@echo pipenv not found, installing...
@echo.
python -m pip --disable-pip-version-check install pipenv > tmpFile
del tmpFile
@echo.

:Run
@echo Pipenv is installed!


if exist "Pipfile.lock" GOTO Dependencies

@echo Creating Pipfile.lock, this might take a minute...

pipenv lock > tmpFile 2>&1
del tmpFile
color 07

:Dependencies
@echo Checking pipenv dependencies...
pipenv install > tmpFile 2>&1
del tmpFile 


@echo.
@echo Done, launching bot
@echo.

pipenv run python "main.py"
pause