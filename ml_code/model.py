import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# load cleaned dataset
data = pd.read_csv("dataset/cleaned_data.csv")

# 🔥 GROUP same job roles together
grouped_data = data.groupby("job_role")["skills"].apply(
    lambda x: " ".join(x.astype(str))
).reset_index()

def clean_skills(text):
    skills = text.split()
    return list(set(skills))

grouped_data["skills_list"] = grouped_data["skills"].apply(clean_skills)

# classify roles
def classify_role(role):
    role = role.lower()

    # ❌ FIRST: remove manager-type roles
    if "manager" in role:
        return "non-tech"

    # ✅ THEN: detect tech roles
    tech_keywords = ["engineer", "developer", "scientist", "data", "analyst"]

    for word in tech_keywords:
        if word in role:
            return "tech"

    return "non-tech"

grouped_data["category"] = grouped_data["job_role"].apply(classify_role)


# vectorize skills
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(grouped_data["skills"])

# improved prediction function
import numpy as np

def predict_career(user_input, role_type="both"):
    user_vec = vectorizer.transform([user_input])
    similarity = cosine_similarity(user_vec, X)[0]

    import numpy as np
    similarity = similarity / np.max(similarity)

    # filter based on role type
    if role_type != "both":
        mask = grouped_data["category"] == role_type
    else:
        mask = [True] * len(grouped_data)

    filtered_indices = [i for i, m in enumerate(mask) if m]

    scores = [(i, similarity[i]) for i in filtered_indices]

    # sort scores
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    MIN_SCORE = 0.3  # 🔥 threshold

    results = []
    seen = set()

    for i, score in scores:
        if score < MIN_SCORE:
            continue  # skip weak matches

        job = grouped_data.iloc[i]["job_role"]
        score = round(score * 100, 2)

        if job not in seen:
            results.append({"role": job, "score": score})
            seen.add(job)

        if len(results) == 3:
            break

    return results


def skill_gap(user_skills, target_role):
    user_list = user_skills.lower().split()
    user_set = set(user_list)

    role_data = grouped_data[grouped_data["job_role"] == target_role]

    if role_data.empty:
        return {"error": "Role not found"}

    # use skills string safely
    role_list = str(role_data.iloc[0]["skills"]).split()
    role_set = set(role_list)

    matched = user_set & role_set
    missing = role_set - user_set

    return {
        "matched_skills": list(matched),
        "missing_skills": list(missing)
    }

    
if __name__ == "__main__":
    user_input = input("Enter your skills: ")
    role = input("Enter target role: ")

    result = skill_gap(user_input, role)

    print("\nSkill Gap Analysis:")
    print("Matched Skills:", result["matched_skills"])
    print("Missing Skills:", result["missing_skills"])    


# # test the model
# if __name__ == "__main__":
#     user_input = input("Enter your skills: ")
#     role_type = input("Choose role type (tech / non-tech / both): ")

#     results = predict_career(user_input, role_type)

#     print("\nTop Career Suggestions:")
#     for item in results:
#         print(f"{item['role']} ({item['score']}%)")