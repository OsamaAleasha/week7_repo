document.addEventListener("DOMContentLoaded", () => {
    loadRecommendations();
});

async function loadRecommendations() {
    const container = document.querySelector(".app-container div[style*='flex-direction: column']");
    const introText = document.querySelector("p[style*='color: var(--text-muted)']");

    try {
        // Use your existing apiFetch helper
        const response = await apiFetch("/api/recommend", {
            method: "POST"
        });

        const data = await response.json();

        if (response.ok) {
            // Update the "Based on your interests" text
            if (data.user_major) {
                introText.innerHTML = `Personalized path for <strong>${data.user_major}</strong> majors.`;
            }

            // Clear the hardcoded placeholder cards
            container.innerHTML = "";

            if (data.recommendations.length === 0) {
                container.innerHTML = "<p>No recommendations found. Try adding more skills to your profile!</p>";
                return;
            }

            // Generate cards dynamically
            data.recommendations.forEach(course => {
                const card = createCourseCard(course);
                container.appendChild(card);
            });
        } else {
            console.error("Error fetching recommendations:", data.error);
        }
    } catch (err) {
        console.error("Network error:", err);
    }
}

function createCourseCard(course) {
    const article = document.createElement("article");
    article.className = "card horizontal-card";
    
    // Similarity score calculation for the badge (assuming score is 0 to 1)
    const matchPercentage = Math.round((course.similarity_score || 0.85) * 100);
    
    article.innerHTML = `
        <div class="course-preview-box"></div>
        <div style="flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span class="match-badge">${matchPercentage}% Match</span>
                <span style="color: #FFD700;">★★★★★</span>
            </div>
            <h3 style="font-size: 20px; margin-bottom: 8px;">${course.title}</h3>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 15px;">
                ${course.description.substring(0, 120)}...
            </p>
            
            <div style="width: 100%; height: 6px; background: #eee; border-radius: 3px; overflow: hidden;">
                <div style="width: ${matchPercentage}%; height: 100%; background: var(--accent);"></div>
            </div>
            <p style="font-size: 11px; margin-top: 5px; color: var(--text-muted); text-transform: uppercase;">
                Instructor: ${course.instructor}
            </p>
        </div>
        <button onclick="window.location.href='/course-details_page?id=${course.id}'" 
                style="width: auto; padding: 10px 20px; font-size: 14px;">VIEW</button>
    `;
    return article;
}

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
}