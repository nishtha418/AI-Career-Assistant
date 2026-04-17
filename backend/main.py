from fastapi import FastAPI
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = FastAPI()

# -------------------------------
# LOAD DATA
# -------------------------------
data = pd.read_csv("dataset/cleaned_data.csv")

grouped_data = data.groupby("job_role")["skills"].apply(
    lambda x: " ".join(x)
).reset_index()

# -------------------------------
# MODEL
# -------------------------------
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(grouped_data["skills"])

# -------------------------------
# PREDICT FUNCTION (YOUR LOGIC)
# -------------------------------
def predict_career(user_input):
    user_vec = vectorizer.transform([user_input])
    similarity = cosine_similarity(user_vec, X)[0]

    similarity = similarity / np.max(similarity)

    top_indices = similarity.argsort()[-5:][::-1]

    results = []
    seen = set()

    for i in top_indices:
        job = grouped_data.iloc[i]["job_role"]
        score = round(similarity[i] * 100, 2)

        if job not in seen:
            results.append({"role": job, "score": score})
            seen.add(job)

        if len(results) == 3:
            break

    return results

# -------------------------------
# SKILL GAP FUNCTION (SIMPLE)
# -------------------------------
def skill_gap(user_skills, target_role):
    user_list = user_skills.lower().split()
    user_set = set(user_list)

    role_data = grouped_data[grouped_data["job_role"] == target_role]

    if role_data.empty:
        return {"error": "Role not found"}

    role_list = str(role_data.iloc[0]["skills"]).split()
    role_set = set(role_list)

    matched = list(user_set & role_set)
    missing = list(role_set - user_set)

    return {
        "matched_skills": matched,
        "missing_skills": missing
    }

# -------------------------------
# ROUTES
# -------------------------------
@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/predict")
def predict(skills: str):
    results = predict_career(skills)
    return {"results": results}

@app.get("/skill-gap")
def skill_gap_api(skills: str, role: str):
    result = skill_gap(skills, role)
    return result