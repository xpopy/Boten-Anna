@echo off
@echo Starting checks
@echo. 


:: Check for .git folder ::
:: Install it by cloning the repository, moving the .git folder and then deleting the clone ::
if not exist .git\NUL (
	@echo .git folder not found (happens if you download as zip^)
	@echo Installing .git (can take a minute depending on internet speeds^)
	bin\git\cmd\git.exe clone https://github.com/xpopy/Boten-Anna.git > tmpFile 2>&1
	attrib -h Boten-Anna\.git
	move Boten-Anna\.git .git >nul
	rmdir Boten-Anna\ /s /q
	@echo  .git is installed
	@echo.
)


:: Check for pipenv and install if not found ::
@echo Checking for pipenv...
pip --disable-pip-version-check list | findstr pipenv > tmpFile 
set /p myvar= < tmpFile 
del tmpFile 
if "%myvar%" == "" (
	@echo pipenv not found, installing...
	@echo.
	python -m pip --disable-pip-version-check install pipenv > tmpFile
	del tmpFile
	@echo  pipenv is installed
	@echo.
)


:: Create Pipfile.lock if it doesn't exist ::
if not exist Pipfile.lock (
	@echo Creating Pipfile.lock, this might take a minute...
	pipenv lock > tmpFile 2>&1
	del tmpFile
	color 07
)


:: Check dependencies ::
@echo Checking pipenv dependencies...
pipenv install > tmpFile 2>&1
del tmpFile


@echo.
@echo Done, launching bot
@echo.


:: Run main program either without or with 2 argumnets ::
set "TRUE="
IF %1.==. set TRUE=1
IF %2.==. set TRUE=1
IF defined TRUE (
	pipenv run python "main.py"
	pause
) else (
	pipenv run python "main.py" %1 %2
)
