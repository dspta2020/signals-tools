@echo off

REM Echoing a message
echo Generating new Python virtual environment...

REM Run the Python command to create a virtual environment
python3 -m venv venv

REM Check if the venv was created successfully
if exist "venv\Scripts\Activate" (
  echo Virtual environment activated.
  echo Installing libraries in the new virtual environment...

  REM Activate the virtual environment
  venv\Scripts\Activate

  REM Install some libraries
  pip install numpy matplotlib scipy pandas

  REM Deactivate the virtual environment
  deactivate
  echo Libraries installed successfully.
) else (
  echo Failed to create virtual environment.
)

REM Provide a final message
echo Your new Python virtual environment is ready at: venv
echo To activate it, run: venv\Scripts\Activate