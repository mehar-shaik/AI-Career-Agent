from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pypdf import PdfReader

from .agent import run_career_agent
from .models import Resume
from .tools import analyze_resume


# ==========================================
# CAREER ANALYSIS
# ==========================================

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def analyze_career(request):

    career_goal = request.data.get("career_goal", "")
    skills = request.data.get("skills", "")

    if not career_goal or not skills:
        return Response(
            {
                "error": "Career goal and skills are required."
            },
            status=400
        )

    result = run_career_agent(
        career_goal,
        skills
    )

    return Response({
        "result": result
    })


# ==========================================
# RESUME UPLOAD AND ANALYSIS
# ==========================================

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def upload_resume(request):

    print("REAL UPLOAD VIEW REACHED")

    if "resume" not in request.FILES:
        return Response(
            {
                "error": "Please upload a resume."
            },
            status=400
        )

    uploaded_file = request.FILES["resume"]
    if not uploaded_file.name.lower().endswith(".pdf"):
        return Response(
            {
                "error":"only PDF resumes are supported."
            },status=400
        )

    MAX_FILE_SIZE=5*1024*1024
    if uploaded_file.size > MAX_FILE_SIZE:
        return Response(
            {
                "error":"Resume File must be Smaller than 5MB."
            },status=400
        )

    # Save uploaded resume
    resume = Resume.objects.create(
        file=uploaded_file
    )

    # Extract text from PDF
    reader = PdfReader(resume.file.path)

    resume_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            resume_text += text + "\n"

    # Analyze extracted resume text
    result = analyze_resume(resume_text)

    return Response({
        "filename": uploaded_file.name,
        "detected_skills": result["detected_skills"]
    })