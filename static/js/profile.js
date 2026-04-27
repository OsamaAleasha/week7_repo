async function loadProfile() {
    const token = localStorage.getItem("token");

    const response = await fetch("/api/users/me", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await response.json();

    if (!response.ok) {
        console.error(data.error);
        return;
    }

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