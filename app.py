from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app)

# Configure JWT authentication
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)

UPLOAD_FOLDER = "uploads"
EXPORT_FOLDER = "exports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Sample users with roles
users = {
    "admin": {"password": "password123", "role": "admin"},
    "viewer": {"password": "viewerpass", "role": "viewer"}
}

# Login route to generate JWT token
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        access_token = create_access_token(identity=username, additional_claims={"role": users[username]["role"]})
        return jsonify({"access_token": access_token, "role": users[username]["role"]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# Score calculation function with dynamic weights
def calculate_score(df, prod_weight=0.4, qual_weight=0.35, time_weight=0.25):
    required_columns = ["Name", "Productivity", "Quality", "Timeliness"]
    
    # Check if required columns exist
    if not all(col in df.columns for col in required_columns):
        return None, {"error": "Missing required columns in dataset."}
    
    df["Total Score"] = (
        df["Productivity"] * prod_weight +
        df["Quality"] * qual_weight +
        df["Timeliness"] * time_weight
    )
    return df, None

# File upload and processing route (Admin only)
@app.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    # Get user role from token
    current_user = get_jwt_identity()
    role = get_jwt()["role"]

    if role != "admin":
        return jsonify({"error": "Unauthorized access! Only admins can upload files."}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, "latest_file.csv")
    file.save(file_path)

    # Determine file type
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            return jsonify({"error": "Unsupported file format. Upload a CSV or XLSX file."}), 400
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500

    # Get weights from request params
    prod_weight = float(request.args.get("prod_weight", 0.4))
    qual_weight = float(request.args.get("qual_weight", 0.35))
    time_weight = float(request.args.get("time_weight", 0.25))

    # Calculate scores with dynamic weights
    df, error = calculate_score(df, prod_weight, qual_weight, time_weight)
    if error:
        return jsonify(error), 400

    df.to_csv(file_path, index=False)  # Save updated file

    return jsonify({"message": "File processed successfully", "data": df.to_dict()}), 200

# Generate PDF report
@app.route("/export/pdf", methods=["GET"])
@jwt_required()
def export_pdf():
    try:
        file_path = os.path.join(UPLOAD_FOLDER, "latest_file.csv")
        if not os.path.exists(file_path):
            return jsonify({"error": "No file uploaded yet!"}), 400
        
        df = pd.read_csv(file_path)
        pdf_path = os.path.join(EXPORT_FOLDER, "scorecard_report.pdf")
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        y = 750  # Start position for text
        c.drawString(200, y, "Scorecard Performance Report")
        y -= 30

        for index, row in df.iterrows():
            c.drawString(50, y, f"{row['Name']}: {row['Total Score']} Points")
            y -= 20
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 750

        c.save()
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
