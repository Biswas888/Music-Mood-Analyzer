const API_BASE = "http://localhost:8000"; // Adjust if using Docker

// Fetch summary of moods and total songs
async function loadGeneralInfo() {
    try {
        const res = await fetch(`${API_BASE}/api/moods`);
        const data = await res.json();

        // Total songs
        const total = data.reduce((sum, item) => sum + item.count, 0);
        document.getElementById("totalSongs").innerText = total;

        // Individual mood counts
        data.forEach(item => {
            const mood = item.mood.toLowerCase();
            if (document.getElementById(`${mood}Songs`)) {
                document.getElementById(`${mood}Songs`).innerText = item.count;
            }
        });

    } catch (err) {
        console.error("Error loading general info:", err);
    }
}

// Navigate to dashboard page
document.getElementById("dashboardBtn").addEventListener("click", () => {
    window.location.href = "dashboard.html";
});

// Initialize on load
window.onload = () => {
    loadGeneralInfo();
};
