document.addEventListener("DOMContentLoaded", async () => {
    // 1. First, populate the dropdown with real skills from the DB
    await loadSkillDropdown();
    
    // 2. Then, perform the initial course load
    loadCourses();
});

// NEW: Function to fetch skills and fill the <select>
async function loadSkillDropdown() {
    const skillSelect = document.getElementById("skill-filter");
    
    try {
        const response = await fetch("/api/skills");
        const data = await response.json(); // Data format: { "skills": [...] }

        let html = '<option value="All Skills">All Skills</option>';
        
        data.skills.forEach(skill => {
            html += `<option value="${skill.name}">${skill.name}</option>`;
        });

        skillSelect.innerHTML = html;
    } catch (error) {
        console.error("Error loading skills:", error);
    }
}

async function loadCourses() {
    const search = document.querySelector(".search-bar").value;
    // Note: ensure your HTML select has id="skill-filter"
    const skill = document.getElementById("skill-filter").value;
    const sort = document.getElementById("sort-filter") ? document.getElementById("sort-filter").value : "relevance";

    let url = `/api/courses?q=${encodeURIComponent(search)}&skill=${encodeURIComponent(skill)}&sort=${sort}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        renderCourses(data.courses);
    } catch (error) {
        console.error("Error fetching courses:", error);
    }
}

function renderCourses(courses) {
    const grid = document.querySelector(".courses-grid");
    if (courses.length === 0) {
        grid.innerHTML = "<p>No courses found matching your criteria.</p>";
        return;
    }

    let html = ""
    courses.forEach(course => {
        html += `
            <article class="card">
                <div style="height: 140px; background: #eee; border-radius: 10px; margin-bottom: 15px;"></div>
                <h1>${course.title}</h1>
                <p style="color: #666; font-size: 14px; margin-bottom: 20px;">${course.description || "No description available"}</p>
                <button onclick="location.href='/course-details_page?id=${course.id}'">View Details</button>
            </article>
        `;
    });
    grid.innerHTML = html;
}

// Optimized Event Listeners
document.addEventListener("input", (e) => {
    if (e.target.classList.contains("search-bar")) {
        loadCourses();
    }
});

document.addEventListener("change", (e) => {
    if (e.target.tagName === "SELECT") {
        loadCourses();
    }
});