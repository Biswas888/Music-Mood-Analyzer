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

document.getElementById("addSongBtn").addEventListener("click", () => {
    window.location.href = "add_song.html";
});

// Initialize on load
window.onload = () => {
    loadGeneralInfo();
};

window.addEventListener("DOMContentLoaded", () => {

    const options = {
        width: "100%",
        height: "100%",
        hideTabs: true,
        hideToolbar: true,
        device: "desktop"
    };

    const container1 = document.getElementById("vizContainer1");
    const container2 = document.getElementById("vizContainer2");

    const url1 = "https://public.tableau.com/views/YourDashboard/Dashboard1";
    const url2 = "https://public.tableau.com/views/YourDashboard/Dashboard2";

    const viz1 = new tableau.Viz(container1, url1, options);
    const viz2 = new tableau.Viz(container2, url2, options);

});
