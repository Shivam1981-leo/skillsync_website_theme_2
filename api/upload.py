from http.server import BaseHTTPRequestHandler
import json
import re
import io
import string
from collections import Counter

# ── Try to import PyPDF2 ──────────────────────────────────────────────────────
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

# ── Stopwords ─────────────────────────────────────────────────────────────────
STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "have",
    "has", "was", "are", "will", "responsible", "worked", "experience",
    "project", "education", "company", "university", "also", "able",
    "using", "used", "work", "team", "our", "your", "etc"
}

# ── Target skill sets ─────────────────────────────────────────────────────────
TARGET_SKILLS = {
    "python", "java", "c++", "flask", "spring boot",
    "sql", "nosql", "git", "docker", "algorithms",
    "system design", "api", "machine learning",
    "android", "data structures", "kotlin", "rest",
    "kubernetes", "aws", "linux", "react", "node"
}


# ──────────────────────────────────────────────────────────────────────────────
# PDF TEXT EXTRACTION
# ──────────────────────────────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not HAS_PDF:
        return ""

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
        return text.lower()
    except:
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# SKILL EXTRACTION
# ──────────────────────────────────────────────────────────────────────────────
def extract_skills_from_text(text: str):
    words = [
        w.strip(string.punctuation).lower()
        for w in text.split()
        if w.strip(string.punctuation)
    ]

    phrases = []
    for i in range(len(words)):
        phrases.append(words[i])
        if i < len(words) - 1:
            phrases.append(words[i] + " " + words[i + 1])
        if i < len(words) - 2:
            phrases.append(words[i] + " " + words[i + 1] + " " + words[i + 2])

    cleaned = [
        p for p in phrases
        if all(w not in STOPWORDS for w in p.split())
        and not any(c.isdigit() for c in p)
        and len(p) > 2
    ]

    freq = Counter(cleaned)
    skills = [s for s, c in freq.items() if c >= 2 and len(s.split()) <= 3]

    return skills[:25]


def find_matched_and_missing(resume_text: str):
    matched, missing = [], []
    for skill in TARGET_SKILLS:
        if skill in resume_text:
            matched.append(skill.title())
        else:
            missing.append(skill.title())
    return matched, missing


# ──────────────────────────────────────────────────────────────────────────────
# SCORING LOGIC
# ──────────────────────────────────────────────────────────────────────────────
def keyword_similarity(text_a: str, text_b: str) -> float:
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.5
    intersection = words_a & words_b
    return len(intersection) / (len(words_a | words_b) ** 0.5 + 1e-9)


def analyse(resume_text: str, job_description: str) -> dict:

    # 1. JD Match (40%)
    if job_description:
        sim = keyword_similarity(resume_text, job_description)
        jd_score = min(sim * 200, 100)
    else:
        jd_score = 58

    # 2. Experience (20%)
    exp_matches = re.findall(r'(\d+)\+?\s*(years|yrs)', resume_text)
    total_years = sum(int(m[0]) for m in exp_matches)

    if total_years >= 5:
        experience_score = 90
    elif total_years >= 3:
        experience_score = 75
    elif total_years >= 1:
        experience_score = 60
    else:
        experience_score = 40

    # 3. Skill Coverage (15%)
    matched_skills, missing_skills = find_matched_and_missing(resume_text)
    skill_score = min((len(matched_skills) / max(len(TARGET_SKILLS), 1)) * 100, 100)
    auto_skills = extract_skills_from_text(resume_text)

    # 4. Project Detection (15%)
    project_kw = ["project", "developed", "built", "implemented", "designed", "created"]
    project_count = sum(resume_text.count(w) for w in project_kw)

    if project_count >= 6:
        project_score = 90
    elif project_count >= 3:
        project_score = 72
    elif project_count >= 1:
        project_score = 55
    else:
        project_score = 35

    # 5. Quality Signals (10%)
    quality_score = 45

    if len(resume_text) > 1500:
        quality_score += 10
    if re.search(r'\b\d+%|\$\d+|₹\d+|\d+\+', resume_text):
        quality_score += 20
    if "education" in resume_text:
        quality_score += 10
    if "experience" in resume_text:
        quality_score += 15

    quality_score = min(quality_score, 100)

    # Final Score
    final_score = int(
        0.40 * jd_score +
        0.20 * experience_score +
        0.15 * skill_score +
        0.15 * project_score +
        0.10 * quality_score
    )

    # Status
    if final_score >= 80:
        status = "Excellent Match"
    elif final_score >= 65:
        status = "Strong Candidate"
    elif final_score >= 50:
        status = "Good Foundation"
    else:
        status = "Needs Optimisation"

    # Recommendations
    recommendations = []

    if jd_score < 60:
        recommendations.append("Align resume keywords with job description.")
    if experience_score < 60:
        recommendations.append("Highlight experience clearly.")
    if project_score < 60:
        recommendations.append("Add 2–3 strong projects.")
    if quality_score < 65:
        recommendations.append("Include measurable achievements.")
    if len(missing_skills) > 5:
        recommendations.append(f"Add skills: {', '.join(missing_skills[:3])}")

    if not recommendations:
        recommendations.append("Great resume! Tailor for each role.")

    return {
        "match_score": final_score,
        "status": status,
        "strengths": [s.title() for s in (matched_skills or auto_skills)[:6]],
        "weak_points": missing_skills[:6],
        "recommendations": recommendations[:4],
        "radar_scores": [
            round(skill_score, 1),
            round(experience_score, 1),
            round(project_score, 1),
            round(jd_score, 1),
            round(quality_score, 1),
        ],
    }


# ──────────────────────────────────────────────────────────────────────────────
# SERVER HANDLER (NO CGI ✅)
# ──────────────────────────────────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            # ---- Extract boundary ----
            boundary = content_type.split("boundary=")[-1].encode()
            parts = body.split(b"--" + boundary)

            file_bytes = None
            job_description = ""

            for part in parts:
                if b'Content-Disposition' not in part:
                    continue

                headers, _, value = part.partition(b"\r\n\r\n")
                value = value.rstrip(b"\r\n")

                if b'name="file"' in headers:
                    file_bytes = value

                elif b'name="job_description"' in headers:
                    job_description = value.decode(errors="ignore").strip()

            if not file_bytes:
                self._json_response(400, {"error": "No file uploaded"})
                return

            resume_text = extract_text_from_pdf(file_bytes)

            if not resume_text.strip():
                self._json_response(400, {"error": "Could not extract text from PDF"})
                return

            result = analyse(resume_text, job_description)
            self._json_response(200, result)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._json_response(500, {"error": str(e)})

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, status: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass