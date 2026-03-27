"""
prompts.py — All LLM prompt templates for FitMatch AI

This file stores the system and user prompts we send to the LLM.
Keeping prompts separate makes them easy to find and tweak.
"""


# --- System prompt (same for both analysis modes) ---
SYSTEM_PROMPT = (
    "You are an expert ATS (Applicant Tracking System) resume analyst "
    "and career coach. You give clear, actionable advice."
)


def build_analysis_prompt(resume_text: str, job_description: str) -> str:
    """
    Build the user prompt when a full job description is provided.

    Args:
        resume_text: The plain-text content of the user's resume.
        job_description: The full job description to compare against.

    Returns:
        A formatted prompt string asking the LLM for JSON analysis.
    """
    return f"""Analyze the following resume against the job description.

Return ONLY valid JSON (no markdown, no explanation) with these keys:
- "fit_score": integer from 0 to 100
- "matched_skills": list of skills from the resume that match the job
- "missing_skills": list of important skills NOT found in the resume
- "strengths": list of 3-4 resume strengths
- "suggestions": list of 3-5 actionable tips to improve the resume

RESUME:
\"\"\"
{resume_text}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

Respond with JSON only."""


def build_role_only_prompt(resume_text: str, job_role: str) -> str:
    """
    Build the user prompt when only a job role/title is provided (no JD).

    The LLM will first generate a typical job description for that role,
    then perform the same analysis.

    Args:
        resume_text: The plain-text content of the user's resume.
        job_role: A short job title like "Data Analyst" or "Python Developer".

    Returns:
        A formatted prompt string asking the LLM for JSON analysis.
    """
    return f"""The user wants to target the role: "{job_role}".

Step 1 — Generate a realistic job description for this role.
Step 2 — Analyze the resume against that generated job description.

Return ONLY valid JSON (no markdown, no explanation) with these keys:
- "generated_jd": the job description you created (string)
- "fit_score": integer from 0 to 100
- "matched_skills": list of skills from the resume that match the role
- "missing_skills": list of important skills NOT found in the resume
- "strengths": list of 3-4 resume strengths
- "suggestions": list of 3-5 actionable tips to improve the resume

RESUME:
\"\"\"
{resume_text}
\"\"\"

Respond with JSON only."""


# --- System prompt for the resume rewriter ---
REWRITER_SYSTEM_PROMPT = (
    "You are a professional resume writer. "
    "You improve resumes while keeping them truthful and accurate."
)


def build_rewriter_prompt(
    resume_text: str, missing_skills: list, suggestions: list
) -> str:
    """
    Build the prompt that asks the LLM to rewrite the resume.

    The LLM should incorporate missing skills and suggestions naturally,
    but NEVER fabricate experience, companies, or degrees.

    Args:
        resume_text: The original resume text.
        missing_skills: Skills the analysis found missing.
        suggestions: Improvement tips from the analysis.

    Returns:
        A formatted prompt string for the rewriter.
    """
    skills_str = "\n".join(f"- {s}" for s in missing_skills)
    suggestions_str = "\n".join(f"- {s}" for s in suggestions)

    return f"""Rewrite the resume below to be stronger and more ATS-friendly.

RULES:
- Do NOT fabricate any experience, companies, degrees, or certifications.
- Only use information already present in the resume.
- Naturally weave in relevant keywords from the missing skills WHERE the
  person's existing experience supports them.
- Strengthen bullet points with action verbs and measurable results.
- Improve formatting and phrasing for clarity.
- Return ONLY the rewritten resume text. No explanation. No markdown formatting.

MISSING SKILLS TO ADDRESS (incorporate where truthful):
{skills_str}

IMPROVEMENT SUGGESTIONS TO APPLY:
{suggestions_str}

ORIGINAL RESUME:
\"\"\"
{resume_text}
\"\"\"

Return the rewritten resume text only."""


# --- System prompt for ATS keyword analysis ---
ATS_SYSTEM_PROMPT = (
    "You are an ATS (Applicant Tracking System) keyword optimization expert."
)


def build_ats_keyword_prompt(resume_text: str, job_description: str) -> str:
    """
    Build the prompt for ATS keyword analysis.

    Compares the resume against the job description and identifies
    exact keywords/phrases that are missing.

    Args:
        resume_text: The plain-text content of the user's resume.
        job_description: The job description (real or AI-generated).

    Returns:
        A formatted prompt string for ATS keyword extraction.
    """
    return f"""Compare the resume against the job description below.

Extract keywords and phrases from the job description and check if they
appear in the resume.

Return ONLY valid JSON (no markdown, no explanation) with these keys:
- "found_keywords": list of keywords/phrases from the JD that ARE in the resume
- "missing_keywords": list of keywords/phrases from the JD that are NOT in the resume
- "keyword_score": integer 0-100 (percentage of JD keywords found in resume)
- "insert_suggestions": list of objects, each with:
    - "keyword": the missing keyword
    - "suggestion": a short sentence showing how to naturally add it to the resume

RESUME:
\"\"\"
{resume_text}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

Respond with JSON only."""
