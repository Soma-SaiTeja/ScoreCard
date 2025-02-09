# ScoreCard
Developed a Dynamic Scorecard Tool for Performance Evaluation using Streamlit and Flask

project structure
📂 scorecard_project
│── 📂 venv/             # Virtual Environment (auto-created)
│── 📂 uploads/          # Folder for uploaded Excel/CSV files
│── 📜 app.py            # Flask Backend (API)
│── 📜 dashboard.py      # Streamlit Frontend
│── 📜 requirements.txt  # Dependencies (optional)

Run the commands to create in cmd prompt
This guide will show how to set up, build, and run a Flask + Streamlit project, including all necessary commands and the correct project structure.

step 1:
mkdir ScorecardProject
cd ScorecardProject

Step 2: Create a Virtual Environment
To ensure package management is clean, create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate

Step 3: Install Required Dependencies
Run the following command to install necessary Python packages:
pip install flask pandas openpyxl flask-cors flask-jwt-extended streamlit reportlab xlsxwriter requests

To Create These Folders, Run:
mkdir uploads exports

Step 5: Write Flask Backend (app.py)
📜 Create app.py inside ScorecardProject/ and paste the flask code aoo.py which is already attached

Step 6: Write Streamlit Frontend (dashboard.py)
📜 Create dashboard.py inside ScorecardProject/ and paste the attached dashboard.py

run the follwing .py files on different cmd panels
code to run ->python app.py
code to run ->streamlit run dashboard.py

