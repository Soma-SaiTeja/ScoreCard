import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import yagmail
import base64

# Streamlit App Title
st.title("📊 Dynamic Scorecard Tool")

# Sidebar Login Section
st.sidebar.title("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if login_button:
    response = requests.post("http://127.0.0.1:5000/login", json={"username": username, "password": password})
    if response.status_code == 200:
        st.session_state["token"] = response.json()["access_token"]
        st.session_state["role"] = response.json()["role"]
        st.sidebar.success(f"✅ Login successful! Role: {st.session_state['role']}")
    else:
        st.sidebar.error("❌ Invalid credentials!")

# Check if user is logged in
if "token" in st.session_state:
    role = st.session_state["role"]

    # Admin Features
    if role == "admin":
        st.sidebar.subheader("⚖️ Customize Weights")
        prod_weight = st.sidebar.slider("Productivity Weight", 0.0, 1.0, 0.4)
        qual_weight = st.sidebar.slider("Quality Weight", 0.0, 1.0, 0.35)
        time_weight = st.sidebar.slider("Timeliness Weight", 0.0, 1.0, 0.25)

    st.subheader("Upload Score Data")
    uploaded_file = st.file_uploader("Upload your Excel/CSV file", type=["csv", "xlsx"])

    if uploaded_file and role == "admin":
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        params = {"prod_weight": prod_weight, "qual_weight": qual_weight, "time_weight": time_weight}

        response = requests.post("http://127.0.0.1:5000/upload", files=files, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()["data"]
            df = pd.DataFrame.from_dict(data)
            st.write("### Processed Performance Scores")
            st.dataframe(df)

            if not df.empty:
                # Bar Chart
                st.write("### 📊 Score Distribution")
                st.bar_chart(df.set_index("Name")["Total Score"])

                # Pie Chart
                st.write("### 🍰 Score Breakdown")
                fig_pie = px.pie(df, names="Name", values="Total Score", title="Total Score Distribution")
                st.plotly_chart(fig_pie)

                # Radar Chart
                st.write("### 🕸 Radar Chart for Performance Metrics")
                categories = ["Productivity", "Quality", "Timeliness"]
                fig_radar = go.Figure()

                for index, row in df.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[row["Productivity"], row["Quality"], row["Timeliness"]],
                        theta=categories,
                        fill='toself',
                        name=row["Name"]
                    ))

                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)))
                st.plotly_chart(fig_radar)

                # PDF Export Option
                st.subheader("📄 Download Report")
                if st.button("Download PDF Report"):
                    pdf_headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    pdf_response = requests.get("http://127.0.0.1:5000/export/pdf", headers=pdf_headers)

                    if pdf_response.status_code == 200:
                        st.success("✅ PDF Report Ready! Click below to download.")
                        st.download_button(label="Download PDF", data=pdf_response.content, file_name="scorecard_report.pdf", mime="application/pdf")
                    else:
                        st.error("⚠️ Error generating PDF report.")

                # Share Report via Email
                st.write("### 📩 Share Report via Email")
                recipient_email = st.text_input("Enter recipient email")
                if st.button("Send Report via Email"):
                    sender_email = "your_email@gmail.com"  # Replace with your email
                    sender_password = "your_app_password"  # Use an App Password (not your real password)
                    try:
                        yag = yagmail.SMTP(sender_email, sender_password)
                        yag.send(to=recipient_email, subject="Scorecard Report", contents="Please find the attached report.", attachments="scorecard_report.pdf")
                        st.success(f"✅ Report sent to {recipient_email}!")
                    except Exception as e:
                        st.error(f"⚠️ Error sending email: {e}")

        else:
            st.error("⚠️ Error processing file upload.")

    elif uploaded_file and role == "viewer":
        st.warning("👀 Viewers cannot upload files. Please contact an admin.")

    elif role == "viewer":
        st.info("👀 Viewer Mode: You can only view reports.")
