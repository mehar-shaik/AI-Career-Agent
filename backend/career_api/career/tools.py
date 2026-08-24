from .models import Career


def get_required_skills(role):
    normalized_role = " ".join(role.split()).strip()

    try:
        career = Career.objects.get(
            role__iexact=normalized_role
        )

        return career.skills

    except Career.DoesNotExist:
        return []


def analyze_skills(role, current_skills):

    required_skills = get_required_skills(role)

    normalized_current = {
        " ".join(skill.lower().split())
        for skill in current_skills
    }

    matched = []
    missing = []

    for skill in required_skills:

        normalized_required = " ".join(
            skill.lower().split()
        )

        if normalized_required in normalized_current:
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched_skills": matched,
        "missing_skills": missing
    }


def analyze_resume(resume_text):
    skills_database = [
        "Python",
        "Django",
        "FastAPI",
        "REST APIs",
        "SQL",
        "Git",
        "GitHub",
        "React",
        "JavaScript",
        "Docker"
    ]

    text = resume_text.lower()

    detected = []

    for skill in skills_database:
        if skill.lower() in text:
            detected.append(skill)

    return {
        "detected_skills": detected
    }