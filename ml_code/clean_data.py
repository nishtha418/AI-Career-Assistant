import pandas as pd

df = pd.read_csv("dataset/job_market.csv")

# select correct columns
df = df[["job_title", "skills"]]

# remove missing
df = df.dropna()

# lowercase
df["skills"] = df["skills"].str.lower()
df["job_title"] = df["job_title"].str.lower()

# clean skills
df["skills"] = df["skills"].str.replace(",", " ")

# rename properly (IMPORTANT FIX)
df = df.rename(columns={
    "skills": "skills",
    "job_title": "job_role"
})

# reorder columns (VERY IMPORTANT)
df = df[["skills", "job_role"]]

# save
df.to_csv("dataset/cleaned_data.csv", index=False)

print("✅ Fixed dataset saved")