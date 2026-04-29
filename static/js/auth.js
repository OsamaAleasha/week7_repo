async function registerUser(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const phone = document.getElementById("phone").value;
    const age = document.getElementById("age").value;
    const major = document.getElementById("major").value;

    // collect checked skills
    const skillCheckboxes = document.querySelectorAll("input[name='skills']:checked");

    const skills = Array.from(skillCheckboxes).map(cb => {
        const id = cb.value;

        const levelSelect = document.querySelector(`select[name='level_${id}']`);

        return {
            id: parseInt(id),
            level: levelSelect ? levelSelect.value : "beginner"
        };
    });

    const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username,
            email,
            password,
            phone,
            age,
            major,
            skills
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Registration failed");
        return;
    }

    localStorage.setItem("access_token", data.token); // Your backend returns 'token' currently
    localStorage.setItem("refresh_token", data.refresh_token || ""); // Save refresh if provided
    window.location.href = "/courses_page";
}


// ---------------- LOGIN ----------------
async function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Login failed");
        return;
    }

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    window.location.href = "/courses_page";
}


// ---------------- LOAD SKILLS ----------------
document.addEventListener("DOMContentLoaded", () => {
    loadSkills();
});

async function loadSkills() {
    try {
        const response = await fetch("/api/skills");
        const data = await response.json();

        const container = document.getElementById("skillsContainer");

        if (!container) return;

        container.innerHTML = data.skills.map(skill => `
            <div class="skill-item">
                <div class="skill-main">
                    <input type="checkbox"
                           id="skill_${skill.id}"
                           value="${skill.id}"
                           name="skills">

                    <label for="skill_${skill.id}">
                        ${skill.name}
                    </label>
                </div>

                <select name="level_${skill.id}">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                </select>
            </div>
        `).join("");

    } catch (error) {
        console.error("Error loading skills:", error);
    }
}