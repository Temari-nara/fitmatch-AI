"""
analyzer.py — Handles all communication with the Groq LLM API.

This file sends the resume + job info to the LLM and parses the response.
We use Groq's free tier with the Llama 3 model.
"""

import json
import os
from groq import Groq
from utils.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_role_only_prompt,
    REWRITER_SYSTEM_PROMPT,
    build_rewriter_prompt,
    ATS_SYSTEM_PROMPT,
    build_ats_keyword_prompt,
)


def get_groq_client():
    """
    Create and return a Groq API client.

    The API key is read from the GROQ_API_KEY environment variable.
    Returns None if the key is missing.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def analyze_resume(resume_text: str, job_description: str = "", job_role: str = "") -> dict:
    """
    Send resume + job info to Groq LLM and get back structured analysis.

    Either job_description or job_role must be provided:
    - If job_description is given, we compare directly.
    - If only job_role is given, the LLM generates a JD first.

    Args:
        resume_text: Cleaned resume text.
        job_description: Full job description (optional).
        job_role: Short job title like "Data Analyst" (optional).

    Returns:
        A dictionary with fit_score, matched_skills, missing_skills,
        strengths, and suggestions. Returns an error dict if something fails.
    """
    # --- Step 1: Get the Groq client ---
    client = get_groq_client()
    if client is None:
        return {"error": "GROQ_API_KEY not found. Please set it in your .env file or environment."}

    # --- Step 2: Pick the right prompt ---
    if job_description.strip():
        user_prompt = build_analysis_prompt(resume_text, job_description)
    elif job_role.strip():
        user_prompt = build_role_only_prompt(resume_text, job_role)
    else:
        return {"error": "Please provide a job description or a job role."}

    # --- Step 3: Call the Groq API ---
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Free Llama 3.1 70B on Groq
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,       # Lower = more consistent output
            max_tokens=2048,       # Enough for our JSON response
        )

        # Extract the text content from the API response
        raw_response = response.choices[0].message.content

    except Exception as e:
        return {"error": f"Groq API call failed: {e}"}

    # --- Step 4: Parse the JSON response ---
    return parse_llm_response(raw_response)


def parse_llm_response(raw_text: str) -> dict:
    """
    Safely parse the LLM's JSON response.

    Sometimes the LLM wraps JSON in markdown code blocks or adds extra text.
    This function tries to extract and parse the JSON cleanly.

    Args:
        raw_text: The raw string returned by the LLM.

    Returns:
        Parsed dictionary, or an error dict if parsing fails.
    """
    # Remove markdown code fences if the LLM added them
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        # Strip opening fence (```json or ```)
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)
        return result
    except json.JSONDecodeError:
        return {
            "error": "The AI returned an invalid response. Please try again.",
            "raw_response": raw_text,
        }


def rewrite_resume(resume_text: str, missing_skills: list, suggestions: list) -> str:
    """
    Ask the LLM to rewrite the resume incorporating improvements.

    The LLM will strengthen bullet points and add missing keywords
    WITHOUT fabricating any experience or credentials.

    Args:
        resume_text: Original resume text.
        missing_skills: Skills the analysis found missing.
        suggestions: Improvement tips from the analysis.

    Returns:
        Rewritten resume as a string, or an error message.
    """
    client = get_groq_client()
    if client is None:
        return "[Error] GROQ_API_KEY not found."

    user_prompt = build_rewriter_prompt(resume_text, missing_skills, suggestions)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,   # Slightly creative for better phrasing
            max_tokens=3000,   # Resumes can be long
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[Error] Resume rewrite failed: {e}"


def analyze_ats_keywords(resume_text: str, job_description: str) -> dict:
    """
    Compare resume against job description for ATS keyword matching.

    Identifies which keywords from the JD are present/missing in the
    resume and provides suggestions for adding missing ones.

    Args:
        resume_text: Cleaned resume text.
        job_description: The job description to compare against.

    Returns:
        Dictionary with found_keywords, missing_keywords, keyword_score,
        and insert_suggestions. Returns error dict on failure.
    """
    client = get_groq_client()
    if client is None:
        return {"error": "GROQ_API_KEY not found."}

    user_prompt = build_ats_keyword_prompt(resume_text, job_description)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": ATS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,   # Low temp for consistent keyword extraction
            max_tokens=2048,
        )
        raw_response = response.choices[0].message.content
        return parse_llm_response(raw_response)

    except Exception as e:
        return {"error": f"ATS keyword analysis failed: {e}"}
