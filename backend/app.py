
from flask import (
    Flask, session, request, render_template,
    make_response, redirect, url_for, flash
)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from functools import wraps
import pdfplumber
import os
import re
import secrets

# =====================================================
# FLASK CONFIGURATION
# =====================================================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set.")

CORS(app)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# SKILLS DATABASE
# =====================================================

skills_list = [
    "Python", "Java", "C++", "C", "SQL",
    "HTML", "CSS", "JavaScript", "React", "Angular",
    "Node.js", "Django", "Flask", "FastAPI",
    "REST API", "RESTful API", "Django REST Framework",
    "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "AWS", "Azure", "Docker", "Kubernetes",
    "Git", "GitHub", "Linux",
    "Machine Learning", "Deep Learning", "Data Science",
    "Data Structures", "Algorithms", "Cloud Computing",
    "Excel", "Power BI", "TensorFlow", "PyTorch",
    "Pandas", "NumPy", "Celery", "CI/CD",
    "Microservices", "OOP", "Agile", "JSON",
    "API Development", "Unit Testing", "Pytest"
]


# =====================================================
# SKILL DETECTION
# =====================================================

def detect_skills(text):
    found_skills = []
    normalized_text = text.lower()

    for skill in skills_list:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return found_skills


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# UPLOAD RESUME
# =====================================================

@app.route("/upload", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return "No resume file received.", 400

    file = request.files["resume"]

    if file.filename == "":
        return "Please select a resume.", 400

    if not file.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file only.", 400

    filename = secure_filename(file.filename)

    if not filename:
        return "Invalid file name.", 400

    # Use a unique filename to avoid overwriting another upload.
    filename = secrets.token_hex(8) + "_" + filename

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    session["current_file"] = filename

    return redirect(url_for("home"))


# =====================================================
# EXTRACT RESUME TEXT
# =====================================================

def extract_resume_text():

    current_file = session.get("current_file")

    if not current_file:
        return None, "Please upload a resume first."

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        current_file
    )

    if not os.path.exists(filepath):
        return None, "Resume file not found."

    try:
        extracted_text = ""

        with pdfplumber.open(filepath) as pdf:

            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

        if not extracted_text.strip():
            return None, "No readable text found in this PDF."

        return extracted_text, None

    except Exception as error:
        return None, f"Unable to read PDF: {error}"


# =====================================================
# READ RESUME
# =====================================================

@app.route("/read_resume")
def read_resume():

    text, error = extract_resume_text()

    if error:
        return f"""
            <h2>Resume Reading Error</h2>
            <p>{error}</p>
            <a href="/">Go Back</a>
        """, 400

    return render_template(
        "read_resume.html",
        resume_text=text
    )


# =====================================================
# SKILLS PAGE
# =====================================================

@app.route("/skills")
def get_skills():

    text, error = extract_resume_text()

    if error:
        return f"<h2>{error}</h2>", 400

    found_skills = detect_skills(text)

    skills_html = "".join(
        f"<li>{skill}</li>"
        for skill in found_skills
    )

    return f"""
        <h2>Skills Found in Resume</h2>
        <ul>{skills_html}</ul>
        <h3>Total Skills Found: {len(found_skills)}</h3>
        <a href="/">Go Back</a>
    """


# =====================================================
# RESUME QUALITY SCORE
# =====================================================

def calculate_resume_score(text, detected_skills):

    # Skills contribute up to 40 points.
    skills_score = (
        len(detected_skills) / len(skills_list)
    ) * 40 if skills_list else 0

    # Content contributes up to 30 points.
    content_length = len(text.strip())

    if content_length > 1000:
        content_score = 30
    elif content_length > 500:
        content_score = 25
    elif content_length > 300:
        content_score = 20
    elif content_length > 150:
        content_score = 10
    else:
        content_score = 0

    # Projects contribute up to 15 points.
    projects_score = 15 if re.search(
        r"\b(project|projects)\b",
        text,
        re.IGNORECASE
    ) else 0

    # Education contributes up to 15 points.
    education_score = 15 if re.search(
        r"\b(education|degree|bachelor|master|b\.?tech|b\.?e\.?|bsc|msc)\b",
        text,
        re.IGNORECASE
    ) else 0

    total = (
        skills_score
        + content_score
        + projects_score
        + education_score
    )

    return round(min(total, 100), 2)


# =====================================================
# RESUME SCORE PAGE
# =====================================================

@app.route("/score")
def score_resume():

    text, error = extract_resume_text()

    if error:
        return f"<h2>{error}</h2>", 400

    found_skills = detect_skills(text)

    resume_score = calculate_resume_score(
        text,
        found_skills
    )

    return f"""
        <h1>Resume Score</h1>
        <h2>{resume_score}%</h2>
        <p>Skills detected: {len(found_skills)}</p>
        <h3>Detected Skills</h3>
        <p>{", ".join(found_skills)}</p>
        <a href="/">Go Back</a>
    """


# =====================================================
# ANALYZE JOB DESCRIPTION
# =====================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    text, error = extract_resume_text()

    if error:
        return f"<h2>{error}</h2>", 400

    job_description = request.form.get(
        "job_description", ""
    ).strip()

    if not job_description:
        return """
            <h2>Please enter a Job Description.</h2>
            <a href="/">Go Back</a>
        """, 400

    # All skills detected in the uploaded resume.
    detected_skills = detect_skills(text)

    # All skills detected in the job description.
    required_skills = detect_skills(job_description)

    # Compare normalized skill names.
    resume_skill_set = {
        skill.lower() for skill in detected_skills
    }

    matched_skills = [
        skill for skill in required_skills
        if skill.lower() in resume_skill_set
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill.lower() not in resume_skill_set
    ]

    # ATS score is based on detected JD skills.
    if required_skills:
        ats_score = (
            len(matched_skills) / len(required_skills)
        ) * 100
    else:
        ats_score = 0

    ats_score = round(ats_score, 2)

    # Independent resume quality score.
    resume_score = calculate_resume_score(
        text,
        detected_skills
    )

    # Recommendation.
    if not required_skills:
        recommendation_title = "Unable to Assess"
        recommendation_text = (
            "No supported technical skills were detected "
            "in the job description. Add clear skill "
            "requirements to get a meaningful comparison."
        )

    elif ats_score >= 75:
        recommendation_title = "Strong Match"
        recommendation_text = (
            "The resume matches most of the detected "
            "job-description skills. Consider the candidate "
            "for further evaluation."
        )

    elif ats_score >= 50:
        recommendation_title = "Moderate Match"
        recommendation_text = (
            "The resume matches some of the job requirements. "
            "Review the missing skills before proceeding."
        )

    else:
        recommendation_title = "Low Match"
        recommendation_text = (
            "The resume has limited alignment with the "
            "detected job requirements. Consider improving "
            "the missing skills."
        )

    # Save results for report download.
    session["ats_score"] = ats_score
    session["resume_score"] = resume_score
    session["detected_skills"] = detected_skills
    session["required_skills"] = required_skills
    session["matched_skills"] = matched_skills
    session["missing_skills"] = missing_skills
    session["recommendation_title"] = recommendation_title
    session["recommendation_text"] = recommendation_text

    return render_template(
        "result.html",
        ats_score=ats_score,
        resume_score=resume_score,
        detected_skills=detected_skills,
        required_skills=required_skills,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        recommendation_title=recommendation_title,
        recommendation_text=recommendation_text
    )


# =====================================================
# DOWNLOAD REPORT
# =====================================================

@app.route("/download_report")
def download_report():

    if "ats_score" not in session:
        return redirect(url_for("home"))

    report = f"""
AI RESUME SCREENING SYSTEM
================================

ATS MATCH: {session.get('ats_score')}%
RESUME SCORE: {session.get('resume_score')}%

TOTAL SKILLS DETECTED:
{len(session.get('detected_skills', []))}

DETECTED SKILLS:
{', '.join(session.get('detected_skills', []))}

REQUIRED JOB SKILLS:
{', '.join(session.get('required_skills', []))}

MATCHED SKILLS:
{', '.join(session.get('matched_skills', []))}

MISSING SKILLS:
{', '.join(session.get('missing_skills', []))}

RECOMMENDATION:
{session.get('recommendation_title')}

{session.get('recommendation_text')}

================================
Generated by AI Resume Screening System
"""

    response = make_response(report)

    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = (
        "attachment; filename=resume_analysis_report.txt"
    )

    return response


# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(413)
def file_too_large(error):
    return "File is too large. Maximum upload size is 10 MB.", 413


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=False)
