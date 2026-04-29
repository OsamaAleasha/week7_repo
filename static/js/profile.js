async function loadProfile() {
    // 1. Use apiFetch
    const response = await apiFetch("/api/users/me");

    // 2. Handle errors (apiFetch only redirects on total failure)
    if (!response.ok) {
            const errorData = await response.json();
            console.error("Profile Error:", errorData.error);
            return;
        }

    const data = await response.json();
    const { user, skills } = data;

    // --- Populate User Info ---
    document.getElementById("username").textContent = user.username;
    document.getElementById("major").textContent = user.major || "No major";
    document.getElementById("email").textContent = `Email: ${user.email}`;
    document.getElementById("phone").textContent = `Phone: ${user.phone || "N/A"}`;

    // --- Render Skills ---
    const container = document.getElementById("skillsContainer");
    container.innerHTML = ""; // Clear the placeholder

    skills.forEach(skill => {
        // Skill name and Proficiency (both as raw text from your DB)
        container.innerHTML += `
            <div class="skill-row" style="
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                padding: 12px 0; 
                border-bottom: 1px solid var(--border);
            ">
                <span style="font-weight: 500; color: var(--text-main);">${skill.name}</span>
                <span style="
                    background: var(--bg-app); 
                    color: var(--accent); 
                    padding: 4px 12px; 
                    border-radius: 15px; 
                    font-size: 13px; 
                    font-weight: bold;
                    text-transform: capitalize;
                ">
                    ${skill.proficiency_level}
                </span>
            </div>
        `;
    });
}

loadProfile();