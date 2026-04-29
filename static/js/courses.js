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
    
    if (!courses || courses.length === 0) {
        grid.innerHTML = "<p style='text-align:center; grid-column: 1/-1; padding: 40px;'>No courses found matching your criteria.</p>";
        return;
    }

    let html = "";
    courses.forEach(course => {
        const icon = getCourseEmoji(course.title + " " + (course.description || ""));
        
        html += `
            <article class="card" style="
                display: flex; 
                flex-direction: column; 
                padding: 0; 
                overflow: hidden; 
                height: 100%; /* Ensures all cards in a row are equal height */
            ">
                <!-- 1. Top Image/Emoji Box -->
                <div class="course-preview-box" style="
                    height: 150px; 
                    width: 100%;
                    background: #f3f4f6; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    border-bottom: 1px solid var(--border);
                ">
                    <span style="font-size: 50px; opacity: 0.5;">${icon}</span>
                </div>

                <!-- 2. Content Area -->
                <div style="
                    padding: 20px; 
                    display: flex; 
                    flex-direction: column; 
                    flex-grow: 1; /* Pushes the button to the bottom */
                ">
                    <h1 style="
                        font-size: 18px; 
                        margin: 0 0 10px 0; 
                        color: var(--text-main);
                        display: -webkit-box;
                        -webkit-line-clamp: 2;
                        -webkit-box-orient: vertical;
                        overflow: hidden;
                        height: 44px; /* Fixes title height for alignment */
                    ">
                        ${course.title}
                    </h1>
                    
                    <p style="
                        color: var(--text-muted); 
                        font-size: 14px; 
                        margin-bottom: 20px;
                        display: -webkit-box;
                        -webkit-line-clamp: 3;
                        -webkit-box-orient: vertical;
                        overflow: hidden;
                        flex-grow: 1; /* Takes up available space */
                    ">
                        ${course.description || "No description available"}
                    </p>

                    <!-- 3. Button: Anchored at the bottom -->
                    <button 
                        onclick="location.href='/course-details_page?id=${course.id}'"
                        style="width: 100%; margin-top: auto;"
                    >
                        View Details
                    </button>
                </div>
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