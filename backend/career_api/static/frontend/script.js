let detectedResumeSkills = [];

const analyzeBtn = document.getElementById("analyzeBtn");
const result = document.getElementById("result");


// =============================
// CAREER ANALYSIS
// =============================

analyzeBtn.addEventListener("click", async () => {

    const careerGoal = document.getElementById("career").value.trim();

    const manualSkills =
        document.getElementById("skills").value.trim();

    const skills=manualSkills;

    console.log("CAREER GOAL:", careerGoal);
    console.log("SKILLS SENT:", skills);

    if (!careerGoal) {
        result.innerHTML = "Please enter your career goal.";
        return;
    }

    if (!skills) {
        result.innerHTML =
            "Please enter your skills or upload a resume.";
        return;
    }

    result.innerHTML = `
        <div class="loading">
            🤖 AI is thinking
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

try {

    const response = await fetch(
        "/api/analyze/",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                career_goal: careerGoal,
                skills: skills
            })
        }
    );

    const data = await response.json();

    console.log("CAREER RESPONSE:", data);

    if (!response.ok || data.error) {

        result.innerHTML = `
            <p>❌ ${data.error || "Career analysis failed."}</p>
        `;

        return;
    }

    const score = data.result.score;
    const analysisText = data.result.analysis;

    const formattedResult = analysisText
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^### (.*)$/gm, "<h4>$1</h4>")
    .replace(/^## (.*)$/gm, "<h4>$1</h4>")
    .replace(/^# (.*)$/gm, "<h3>$1</h3>")
    .replace(/^- (.*)$/gm, "<li>$1</li>")
    .replace(/^\d+\.\s+(.*)$/gm, "<li>$1</li>")
    .replace(/\n/g, "<br>");

result.innerHTML = `
    <h3>🤖 AI Career Agent</h3>

    <div class="skill-score">
        <strong>Skill Match: ${score}%</strong>

        <div class="score-bar">
            <div
                class="score-fill"
                style="width: ${score}%"
            ></div>
        </div>
    </div>

    <div class="ai-response">
        ${formattedResult}
    </div>
`;

} catch (error) {

    console.error("CAREER ERROR:", error);

    result.innerHTML = `
        <p>❌ Could not connect to the Django server.</p>
    `;
}
});


// =============================
// RESUME UPLOAD
// =============================

async function uploadResume() {

    const fileInput = document.getElementById("resume");
    const resumeResult = document.getElementById("resumeResult");

    if (!fileInput.files.length) {

        resumeResult.innerHTML =
            "Please select a resume.";

        return;
    }

    const formData = new FormData();

    formData.append(
        "resume",
        fileInput.files[0]
    );

    resumeResult.innerHTML =
        "🔍 Analyzing your resume...";

    try {

        const response = await fetch(
            "/api/upload-resume/",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        console.log("RESUME STATUS:", response.status);
        console.log("RESUME RESPONSE:", data);

        if (!response.ok) {

            resumeResult.innerHTML = `
                <p>❌ ${data.error || "Upload failed."}</p>
            `;

            return;
        }

        // Store detected resume skills
        detectedResumeSkills =
            data.detected_skills || [];

        document.getElementById("skills").value=detectedResumeSkills.join(", ")

        console.log(
            "DETECTED RESUME SKILLS:",
            detectedResumeSkills
        );

        resumeResult.innerHTML = `
            <h3>📄 Resume Analysis</h3>

            <p>
                <strong>File:</strong>
                ${data.filename}
            </p>

            <p>
                <strong>Detected Skills:</strong>
            </p>

            <ul>
                ${detectedResumeSkills
                    .map(skill => `<li>${skill}</li>`)
                    .join("")}
            </ul>
            <p class="skill-source"> ✨Skills detected automatically from your resume</p>
        `;

    } catch (error) {

        console.error("RESUME ERROR:", error);

        resumeResult.innerHTML =
            "Something went wrong while uploading the resume.";
    }
}

const resetBtn = document.getElementById("resetBtn");

resetBtn.addEventListener("click", () => {

    document.getElementById("career").value = "";
    document.getElementById("skills").value = "";
    document.getElementById("resume").value = "";

    document.getElementById("result").innerHTML = "";
    document.getElementById("resumeResult").innerHTML = "";

    detectedResumeSkills = [];

});