// recommendations.js

async function loadRecommendations() {
    const container = document.querySelector(".app-container div:last-child");
    container.innerHTML = "<p style='text-align:center;'>Calculating matches...</p>";

    try {
        const response = await apiFetch("/api/recommend", { method: "POST" });
        const data = await response.json();

        if (!response.ok) throw new Error(data.error);

        document.querySelector("p strong").textContent = data.user_major || "Your Skills";
        container.innerHTML = "";

        data.recommendations.forEach(course => {
            const icon = getCourseEmoji(course.title + " " + course.description);
            
            container.innerHTML += `
        <article class="card horizontal-card" style="
            display: flex; 
            flex-direction: row;     /* Forces horizontal layout */
            width: 100%;
            max-width: 850px;
            height: 180px;           /* Fixed height to keep everything level */
            margin-bottom: 25px;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #eee;
            align-items: center;     /* This levels the Image, Text, and Button */
        ">
            <!-- 1. LEFT: IMAGE BOX (Locked Width) -->
            <div class="course-preview-box" style="
                width: 160px; 
                min-width: 160px;    /* Prevents shrinking */
                height: 100%;        /* Fills card height */
                background: #f8f9fa; 
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;      /* Absolute protection against shrinking */
            ">
                <span style="font-size: 40px; opacity: 0.4;">${icon}</span>
            </div>
            
            <!-- 2. CENTER: CONTENT (Flexible Width) -->
            <div style="
                flex-grow: 1; 
                padding: 0 25px;      /* Side padding only to stay level */
                display: flex; 
                flex-direction: column; 
                justify-content: center; /* Centers text vertically */
                min-width: 0;
                height: 100%;
            ">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <span class="match-badge" style="margin:0;">${course.match_score}% Match</span>
                    </div>
                    <h3 style="margin: 5px 0; font-size: 19px; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        ${course.title}
                    </h3>
                    <p style="font-size: 14px; color: #666; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 15px;">
                        ${course.description}
                    </p>
                </div>
                
                <!-- Match Bar -->
                <div style="width: 100%;">
                    <div style="width: 100%; height: 6px; background: #eee; border-radius: 10px; overflow: hidden;">
                        <div style="width: ${course.match_score}%; height: 100%; background: var(--accent);"></div>
                    </div>
                </div>
            </div>

            <!-- 3. RIGHT: ACTION (Locked Width) -->
            <div style="
                width: 140px; 
                min-width: 140px; 
                height: 100%; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                flex-shrink: 0;      /* Prevents shrinking */
                padding-right: 10px;
            ">
                <button onclick="viewCourse(${course.id})" style="width: 90px; padding: 12px 0; cursor: pointer;">VIEW</button>
            </div>
        </article>
    `;
        });

    } catch (err) {
        container.innerHTML = `<p style="color:red; text-align:center;">${err.message}</p>`;
    }
}

function viewCourse(id) {
    window.location.href = `/course-details_page?id=${id}`;
}

document.addEventListener("DOMContentLoaded", loadRecommendations);