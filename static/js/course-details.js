document.addEventListener("DOMContentLoaded", () => {
    loadCourse();
});

function getCourseId() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

async function loadCourse() {
    const courseId = getCourseId();

    if (!courseId) {
        console.error("No course ID found");
        return;
    }

    const response = await fetch(`/api/courses/${courseId}`);
    const data = await response.json();

    if (!response.ok) {
        console.error(data.error);
        return;
    }

    renderCourse(data.course);
}

function renderCourse(course) {
    const icon = getCourseEmoji(course.title + " " + course.description);
    
    const heroImg = document.querySelector(".course-hero-img");
    if (heroImg) {
        heroImg.innerHTML = `<span style="font-size: 100px;">${icon}</span>`;
        heroImg.style.display = "flex";
        heroImg.style.alignItems = "center";
        heroImg.style.justifyContent = "center";
        heroImg.style.background = "#f3f4f6";
    }

    document.querySelector("h1").textContent = course.title;
    document.querySelector("p").textContent = course.description;

    let skills = [];

    if (course.skill_requirements) {
        try {
            skills = JSON.parse(course.skill_requirements);
        } catch (e) {
            console.log("Invalid JSON:", e);
            skills = [];
        }
    }


    const skillsContainer = document.querySelector(".skills-container");

    if (skillsContainer) {
        skillsContainer.innerHTML = skills
            .map(skill => `<span class="skill-tag">${skill}</span>`)
            .join("");
    }

    // Instructor
    const instructor = document.querySelector(".instructor-card p:nth-child(2)");
    if (instructor) {
        instructor.textContent = course.instructor;
    }
}