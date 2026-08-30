import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .models import Career

from career.tools import (
    get_required_skills,
    analyze_skills,
    analyze_resume
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


system_instruction = """
You are an AI Career Agent.

Help users understand their career skill gaps.

Use the available tools when appropriate.

Always give your answer in a clear, structured format.

Follow this format:

🎯 Career Goal
Briefly state the target career.

✅ Skills You Already Have
- List the skills the user already has that are relevant to the career.

❌ Skill Gaps
- List the important skills the user is missing.

📚 What You Should Learn Next
1. First recommended skill or topic.
2. Second recommended skill or topic.
3. Third recommended skill or topic.

🚀 Recommended Project
Suggest one practical project that helps the user practice the missing skills.

💡 Final Advice
Give a short, practical recommendation.

Keep sections separated by blank lines.
Use bullet points and numbered lists.
Do not write the entire answer as one large paragraph.
"""


# ---------- TOOL DECLARATIONS ----------

get_required_skills_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_required_skills",
            description="Returns skills required for a technology career role.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "role": types.Schema(
                        type="STRING",
                        description="Target career role."
                    )
                },
                required=["role"]
            )
        )
    ]
)


analyze_skills_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="analyze_skills",
            description="Compares current skills with required skills.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "role": types.Schema(
                        type="STRING",
                        description="Target career role."
                    ),
                    "current_skills": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description="Current user skills."
                    )
                },
                required=["role", "current_skills"]
            )
        )
    ]
)


analyze_resume_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="analyze_resume",
            description="Detects technical skills from resume text.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "resume_text": types.Schema(
                        type="STRING",
                        description="Resume text."
                    )
                },
                required=["resume_text"]
            )
        )
    ]
)


# ---------- MAIN AGENT FUNCTION ----------

def run_career_agent(career_goal, skills):

    # Convert user's comma-separated skills into a list
    current_skills = [
        skill.strip()
        for skill in skills.split(",")
        if skill.strip()
    ]

    try:

        # ==========================================
        # GET REQUIRED SKILLS FROM DATABASE
        # ==========================================

        required_skills = get_required_skills(career_goal)

        if not required_skills:
            return (
                f"I couldn't find '{career_goal}' in the career database. "
                "Please try a career that is available in the database."
            )
        career=Career.objects.get(
            role__iexact=career_goal.strip()
        )
        career_description=career.description

        # ==========================================
        # COMPARE USER SKILLS WITH REQUIRED SKILLS
        # ==========================================

        analysis = analyze_skills(
            career_goal,
            current_skills
        )
        total_required = len(required_skills)
        matched_count = len(analysis["matched_skills"])

        skill_score = round(
            (matched_count / total_required) * 100
        ) if total_required else 0

        # ==========================================
        # SEND DATABASE ANALYSIS TO GEMINI
        # ==========================================

        user_input = f"""
Target career: {career_goal}

Career description:
{career_description}

Current skills:
{current_skills}

Required skills from our career database:
{required_skills}

Matched skills:
{analysis["matched_skills"]}

Missing skills:
{analysis["missing_skills"]}

Skill match score:
{skill_score}%

The database-required skills are the authoritative skill gaps.

Create a clear, concise and beginner-friendly career skill-gap analysis.

IMPORTANT:
Do NOT write the entire response as one large paragraph.

Use EXACTLY the following sections and headings:

### Skill Match Score
Write:
{skill_score}%

### Skills You Already Have
List the matched database skills as bullet points.
Briefly explain how these skills relate to the target career.

### Database Required Skills
List the required skills from the career database.

### Skills You Are Missing
List ONLY the missing database-required skills.
Do not add additional skills here.

### What You Should Learn First
Identify the most important missing skill to learn first.
Explain briefly why it should come first.

### Additional Recommendations
Recommend useful industry skills that are NOT already included in the database-required skills.

Clearly label these as additional recommendations.
Do not present them as required database skills.

### Learning Roadmap

Create a practical beginner-friendly roadmap using these phases:

#### Phase 1 — Foundations
Focus on foundational missing skills.

#### Phase 2 — Practical Development
Focus on building real projects and applying the skills.

#### Phase 3 — Deployment & Production
Focus on deployment, cloud, web servers, containers and CI/CD where relevant.

#### Phase 4 — Advanced Industry Skills
Focus on advanced skills that can help the user become job-ready.

For each phase:
- Give a realistic learning order.
- Keep recommendations practical.
- Avoid unnecessary skills.
- Mention projects or practical exercises where useful.

Keep the response concise and easy to scan.

Do not repeat the same skill unnecessarily.
Do not invent database-required skills.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )

        return {
            "score":skill_score,
            "analysis":response.text
        }

    except Exception as e:

        print("CAREER AGENT ERROR:", str(e))

        if "429" in str(e):

            return {
                "career": career_goal,
                "matched_skills": analysis["matched_skills"],
                "missing_skills": analysis["missing_skills"],
                "message": (
                    "Gemini quota exceeded, but the database "
                    "skill analysis is available."
                )
            }

        return f"AI Agent Error: {str(e)}"