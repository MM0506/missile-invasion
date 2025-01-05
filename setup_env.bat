@echo off
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate
echo Installing requirements...
pip install -r requirements.txt
echo Virtual environment setup complete!
pause 