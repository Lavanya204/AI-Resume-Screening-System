# AI Resume Screening System

An AI-powered resume screening application developed using Python and Flask. The system analyzes uploaded resumes, extracts relevant information, identifies skills, and evaluates how well a candidate's resume matches a job description.

## Project Overview

The AI Resume Screening System is designed to simplify the initial resume evaluation process by automating resume analysis and helping recruiters identify relevant candidate skills.

## Key Features

- **Resume Upload:** Upload resumes in PDF format.
- **Resume Text Extraction:** Extract text from uploaded resumes using Python.
- **Skill Detection:** Identify technical skills mentioned in resumes.
- **ATS Matching:** Compare resume content with job requirements.
- **Resume Scoring:** Generate a resume score based on the screening logic.
- **Resume Analysis:** Display extracted skills and analysis results.
- **Resume Reading:** View extracted resume content.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| PDF Processing | pdfplumber |
| Frontend | HTML, CSS, JavaScript |
| Development Tools | VS Code, Git, GitHub |

## Project Structure

```text
AI-Resume-Screening-System/
│
├── backend/
│   ├── app.py
│   ├── templates/
│   │   ├── index.html
│   │   └── result.html
│   └── uploads/
│
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Lavanya204/AI-Resume-Screening-System.git
```

### 2. Navigate to the backend folder

```bash
cd AI-Resume-Screening-System/backend
```

### 3. Install dependencies

```bash
pip install flask pdfplumber flask-cors
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in your browser

```text
http://127.0.0.1:5000/
```

## Application Workflow

1. Upload a candidate resume.
2. Extract resume text.
3. Identify skills and relevant information.
4. Compare the resume against job requirements.
5. Calculate the ATS match and resume score.
6. Display the screening results.

## Future Enhancements

- Improve skill extraction accuracy.
- Enhance ATS matching algorithms.
- Add advanced resume ranking.
- Integrate machine learning-based candidate evaluation.
- Improve the user interface and reporting features.

## Author

**Lavanyasri Velpuri**

GitHub: [Lavanya204](https://github.com/Lavanya204)

---

*Developed as a Python and Flask-based resume screening project.*