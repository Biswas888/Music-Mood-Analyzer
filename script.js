// -------------------
// Configuration
// -------------------
const API_BASE = "http://localhost:8000"; // Change if using Docker or different host

// -------------------
// Tableau Dashboard
// -------------------
let viz;

function initViz() {
    const containerDiv = document.getElementById("vizContainer");
    if (!containerDiv) return;

    const url = "https://public.tableau.com/views/Book1_17431322165620/Dashboard1";

    const options = {
        hideTabs: true,
        width: "100%",
        height: "90vh",
        onFirstInteractive: () => {
            console.log("✅ Tableau dashboard loaded");
            applyTableauFilters();
        }
    };

    viz = new tableau.Viz(containerDiv, url, options);
}

function applyTableauFilters() {
    if (!viz) return;

    const workbook = viz.getWorkbook();
    const activeSheet = workbook.getActiveSheet();

    const moodValue = document.getElementById("moodFilter")?.value;
    const yearValue = document.getElementById("yearFilter")?.value;

    const applyFiltersToSheet = (sheet) => {
        if (moodValue) sheet.applyFilterAsync("Mood", moodValue, tableau.FilterUpdateType.REPLACE);
        else sheet.clearFilterAsync("Mood");

        if (yearValue) sheet.applyFilterAsync("Year", yearValue, tableau.FilterUpdateType.REPLACE);
        else sheet.clearFilterAsync("Year");
    };

    if (activeSheet.getSheetType() === "dashboard") {
        const worksheets = activeSheet.getWorksheets();
        worksheets.forEach(sheet => applyFiltersToSheet(sheet));
    } else {
        applyFiltersToSheet(activeSheet);
    }
}

// -------------------
// Load Mood Cards
// -------------------
async function loadMoodCards() {
    try {
        const res = await fetch(`${API_BASE}/api/moods`);
        const data = await res.json();

        const container = document.getElementById("moodCards");
        if (!container) return;
        container.innerHTML = "";

        data.forEach(item => {
            const card = document.createElement("div");
            card.className = "mood-card";
            card.innerHTML = `
                <h3>${item.mood}</h3>
                <p>${item.count} songs</p>
            `;
            card.onclick = () => {
                const moodFilter = document.getElementById("moodFilter");
                if (moodFilter) {
                    moodFilter.value = item.mood;
                    applyFilters();
                }
            };
            container.appendChild(card);
        });
    } catch (err) {
        console.error("❌ Error loading mood cards:", err);
    }
}

// -------------------
// Load Songs Table
// -------------------
async function loadSongs() {
    try {
        const mood = document.getElementById("moodFilter")?.value || "";
        const year = document.getElementById("yearFilter")?.value || "";

        let url = `${API_BASE}/api/songs?`;
        if (mood) url += `mood=${encodeURIComponent(mood)}&`;
        if (year) url += `year=${year}`;

        const res = await fetch(url);
        const songs = await res.json();

        const tbody = document.querySelector("#songTable tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        if (!songs || songs.length === 0) {
            tbody.innerHTML = "<tr><td colspan='5'>No songs found.</td></tr>";
            return;
        }

        songs.forEach(song => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${song.name}</td>
                <td>${song.artists}</td>
                <td>${song.mood || "-"}</td>
                <td>${song.energy || "-"}</td>
                <td>${song.tempo || "-"}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error("❌ Error loading songs:", err);
    }
}

// -------------------
// Apply Filters
// -------------------
function applyFilters() {
    applyTableauFilters();
    loadSongs();
}

// -------------------
// Event Listeners
// -------------------
const moodFilter = document.getElementById("moodFilter");
const yearFilter = document.getElementById("yearFilter");

if (moodFilter) moodFilter.addEventListener("change", applyFilters);
if (yearFilter) yearFilter.addEventListener("change", applyFilters);

// Back to Home button
const backBtn = document.getElementById("backHomeBtn");
if (backBtn) backBtn.addEventListener("click", () => {
    window.location.href = "index.html";
});

// -------------------
// Initialize Everything on Page Load
// -------------------
window.onload = () => {
    initViz();
    loadMoodCards();
    loadSongs();
};
