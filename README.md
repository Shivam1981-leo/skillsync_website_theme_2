# ⚡ SkillSync — AI Resume Intelligence Platform

A full-stack resume analysis web app deployed on **Vercel** — no server required.  
Upload a PDF resume, paste a job description, and get an instant ATS score with skill gap analysis.

---

## 🌐 Live Pages

| Route | Page |
|---|---|
| `/` | Login / onboarding |
| `/dashboard.html` | Resume upload & AI analysis |
| `/hackathons.html` | Hackathon listings with filters |
| `/jobs.html` | Job & internship search |
| `/courses.html` | Learning roadmap & courses |
| `/buddies.html` | Study buddy finder |

---

## 📁 Project Structure

```
skillsync_vercel/
├── api/
│   └── upload.py          ← Vercel serverless function (resume analysis)
├── static/
│   ├── style.css          ← Shared design system
│   └── script.js          ← Shared JS (upload, radar chart, dropdowns)
├── index.html             ← Login / landing page
├── dashboard.html         ← Main analysis page
├── hackathons.html
├── jobs.html
├── courses.html
├── buddies.html
├── vercel.json            ← Routing & build config
├── requirements.txt       ← Python deps for serverless function
└── README.md
```

---

## 🚀 Deploy to Vercel

### Option A — Vercel Dashboard (easiest)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repo **or** drag-drop this folder
3. Click **Deploy** — no environment variables needed

### Option B — Vercel CLI

```bash
npm i -g vercel       # install CLI if you haven't
cd skillsync_vercel
vercel --prod
```

That's it. Vercel auto-detects `vercel.json` and wires everything up.

---

## 🔧 Local Development

### 1. Install dependencies

```bash
pip install PyPDF2 numpy
```

### 2. Run a local static server

Since the frontend is plain HTML, you can serve it with Python:

```bash
cd skillsync_vercel
python -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000).

> **Note:** The resume upload (`/api/upload`) won't work locally with the static server alone.  
> To test the API locally, use the Vercel CLI dev server instead:
> ```bash
> vercel dev
> ```
> This spins up both the static files and the Python serverless function at `http://localhost:3000`.

---

## 🧠 How the Resume Scoring Works

The API (`api/upload.py`) scores uploaded PDFs across five weighted dimensions:

| Dimension | Weight | What it measures |
|---|---|---|
| JD Match | 40% | Keyword overlap between resume and job description |
| Experience | 20% | Years of experience detected via regex |
| Skill Coverage | 15% | Match against a curated set of 22 target tech skills |
| Project Signals | 15% | Frequency of action words (built, developed, designed…) |
| Quality Signals | 10% | Length, quantified achievements, section completeness |

**Score thresholds:**

| Score | Status |
|---|---|
| 80+ | Excellent Match |
| 65–79 | Strong Candidate |
| 50–64 | Good Foundation |
| < 50 | Needs Optimisation |

---

## ⚙️ API Reference

### `POST /api/upload`

Accepts a `multipart/form-data` request.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File (PDF) | ✅ | The resume to analyse |
| `job_description` | String | ❌ | Paste the target job description for JD match scoring |

**Response (JSON):**

```json
{
  "match_score": 74,
  "status": "Strong Candidate",
  "strengths": ["Python", "Docker", "Git", "React", "Sql", "Api"],
  "weak_points": ["Kubernetes", "Spring Boot", "Kotlin"],
  "recommendations": [
    "Add 2–3 technical projects with measurable outcomes.",
    "Include quantified achievements (e.g. 'improved performance by 30%')."
  ],
  "radar_scores": [68.2, 75.0, 72.0, 81.4, 65.0]
}
```

`radar_scores` maps to: `[Skills, Experience, Projects, JD Match, Quality]`

---

## 📦 Dependencies

All Python dependencies are installed automatically by Vercel at build time via `requirements.txt`.

```
PyPDF2==3.0.1
numpy==1.26.4
```

No `sentence-transformers`, no MySQL — kept lean to stay within Vercel's **50MB bundle limit**.

---

## 💾 Adding a Database (optional)

The API is stateless by default — resumes are analysed in memory and not stored.  
To persist results, swap in a serverless-compatible database:

- **[Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)** — native, zero-config
- **[PlanetScale](https://planetscale.com/)** — MySQL-compatible, free tier available
- **[Supabase](https://supabase.com/)** — Postgres with a REST API, generous free tier

Add the connection string as a Vercel environment variable and import the client in `api/upload.py`.

---

## 🔄 Differences from the Original Flask Version

| Original (`app.py`) | Vercel version (`api/upload.py`) |
|---|---|
| Flask dev server on port 5000 | Vercel serverless function |
| `http://127.0.0.1:5000/api/upload` hardcoded | Relative `/api/upload` |
| `sentence-transformers` (500 MB) | Removed — keyword fallback used |
| `mysql-connector` | Removed — stateless by default |
| `index.html.html` (typo) | Fixed to `index.html` |
| `login.html` links | Updated to `index.html` |

---

## 📄 License

MIT — do whatever you like with it.
