async function apiFetch(endpoint, options = {}) {
    let accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");

    // Prepare headers
    options.headers = {
        ...options.headers,
        "Content-Type": "application/json"
    };

    if (accessToken) {
        options.headers["Authorization"] = `Bearer ${accessToken}`;
    }

    // 1. Initial Request
    let response = await fetch(endpoint, options);

    // 2. Handle Unauthorized (Expired Access Token)
    if (response.status === 401 && refreshToken) {
        console.warn("Access token expired, attempting refresh...");

        const refreshResponse = await fetch("/api/auth/refresh", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            
            // Update local storage with the new token
            localStorage.setItem("access_token", data.access_token);
            
            // Update the Authorization header and RETRY
            options.headers["Authorization"] = `Bearer ${data.access_token}`;
            response = await fetch(endpoint, options);
        } else {
            // Both tokens failed - kick user to login
            logoutUser();
        }
    }

    return response;
}

function logoutUser() {
    localStorage.clear();
    window.location.href = "/login";
}