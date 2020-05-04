@echo off
set "exitCode="
set "returnChannel="

:init
@echo Starting checks
@echo. 


REM Check for .git folder ::
REM Install it by cloning the repository, moving the .git folder and then deleting the clone ::
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


REM Check for pipenv and install if not found ::
@echo Checking for pipenv
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


REM Create Pipfile.lock if it doesn't exist ::
if not exist Pipfile.lock (
	@echo Creating Pipfile.lock, this might take a minute...
	pipenv lock > tmpFile 2>&1
	del tmpFile
	color 07
)


REM Check dependencies ::
@echo Checking pipenv dependencies
pipenv install > tmpFile 2>&1
del tmpFile


@echo.
@echo Done, launching bot
@echo.


REM Start main.py
pipenv run python "main.py" "%exitCode%" "%returnChannel%"

REM Check if exitCode file exists, else quit
if not exist exitCode.tmp (
	pause
	Exit
)

REM Read from exitCode file
for /f "tokens=*" %%a in (exitCode.tmp) do (
	if "%%a" == "exit" (
		REM Quit batch
		pause
		Exit
	)
	if "%%a" == "restart" (
		set exitCode=restart
	) else (
		set returnChannel=%%a
	)
)

REM Delete the file afterwards
del exitCode.tmp

REM Jump to start
goto init

