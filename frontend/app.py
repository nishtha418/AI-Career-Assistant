import streamlit as st
import requests
import PyPDF2

st.set_page_config(page_title="AI Career Assistant", layout="centered")

# -------------------------------
# STYLE
# -------------------------------
st.markdown("""
    <style>
    .card {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.title("🚀 AI Career Assistant")
st.write("Get career suggestions & analyze your skill gap")

# -------------------------------
# RESUME UPLOAD
# -------------------------------
st.header("📄 Upload Resume")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

skills_keywords = [
    "python", "machine learning", "deep learning", "tensorflow",
    "pandas", "numpy", "sql", "java", "c++", "javascript",
    "react", "node.js", "aws", "docker", "kubernetes",
    "nlp", "data analysis", "ai"
]

if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file).lower()

    detected_skills = []
    for skill in skills_keywords:
        if skill in resume_text:
            detected_skills.append(skill)

    st.success("Detected Skills:")
    st.write(detected_skills)

    if detected_skills:
        skills_string = " ".join(detected_skills)

        if st.button("Analyze Resume"):

            # ----------- PREDICTION -----------
            response = requests.get(
                f"https://ai-career-assistant-e0ze.onrender.com/predict?skills={skills_string}"
            )
            data = response.json()

            st.subheader("🎯 Career Suggestions")

            for item in data["results"]:
                st.markdown(f"""
                <div class="card">
                    <h4>{item['role'].title()}</h4>
                    <p>🔥 Match Score: {item['score']}%</p>
                </div>
                """, unsafe_allow_html=True)

            # ----------- SKILL GAP -----------
            top_role = data["results"][0]["role"]

            gap_response = requests.get(
                f"https://ai-career-assistant-e0ze.onrender.com/skill-gap?skills={skills_string}&role={top_role}"
            )
            gap_data = gap_response.json()

            st.subheader(f"📊 Skill Gap for {top_role.title()}")

            col1, col2 = st.columns(2)

            with col1:
                st.success("✅ You Have")
                st.write(gap_data["matched_skills"])

            with col2:
                st.error("❌ You Need")
                st.write(gap_data["missing_skills"])

# -------------------------------
# TABS
# -------------------------------
tab1, tab2 = st.tabs(["🎯 Career Prediction", "📊 Skill Gap"])

# -------------------------------
# TAB 1: PREDICTION
# -------------------------------
with tab1:
    st.subheader("Enter your skills")
    skills_input = st.text_input("e.g. python machine learning")

    if st.button("Predict"):
        if skills_input:
            response = requests.get(
                f"http://127.0.0.1:8000/predict?skills={skills_input}"
            )
            data = response.json()

            st.subheader("Top Matches")

            for item in data["results"]:
                st.markdown(f"""
                <div class="card">
                    <h4>{item['role'].title()}</h4>
                    <p>🔥 Match Score: {item['score']}%</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Enter skills first")

# -------------------------------
# TAB 2: SKILL GAP
# -------------------------------
with tab2:
    st.subheader("Analyze your skill gap")

    gap_skills = st.text_input("Your skills (e.g. python machine learning)")
    target_role = st.text_input("Target role (e.g. data scientist)")

    if st.button("Analyze"):
        if gap_skills and target_role:
            response = requests.get(
                f"http://127.0.0.1:8000/skill-gap?skills={gap_skills}&role={target_role}"
            )
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                col1, col2 = st.columns(2)

                with col1:
                    st.success("✅ Matched Skills")
                    st.write(data["matched_skills"])

                with col2:
                    st.error("❌ Missing Skills")
                    st.write(data["missing_skills"])
        else:
            st.warning("Fill all fields")