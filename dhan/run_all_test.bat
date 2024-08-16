@echo off
echo Running all tests...

rem Change to the project root directory if necessary
rem cd /d "C:\path\to\your\project"

rem Activate your virtual environment if you're using one
rem call venv\Scripts\activate

rem Run the tests
python -m unittest discover -s test_cases -p "*test*.py" -v

rem Deactivate virtual environment if you activated one
rem deactivate

echo.
echo Test run complete.
pause