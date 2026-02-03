// ==============================
// API Base URL
// ==============================
const API_BASE = "http://localhost:8000"; // change if using Docker or different host

// ==============================
// Read initial filters from URL (landing page)
// ==============================
const urlParams = new URLSearchParams(window.location.search);
const initialMood = urlParams.get("mood") || "";
const initialYear = urlParams.get("year") || "";

// Set filter selects to initial values
document.getElementById("moodFilter").value = initialMood;
document.getElementById("yearFilter").value = initialYear;

// ==============================
// Tableau Dashboard Setup
// ==============================
let viz;

function initViz() {
    const containerDiv = document.getElementById("vizContainer");
    const url = "https://public.tableau.com/views/Book1_17431322165620/Dashboard1";

    const options = {
        hideTabs: true,
        width: "100%",
        height: "90vh",
        onFirstInteractive: () => {
            console.log("✅ Tableau dashboard loaded");
            // Apply initial filters if any
            applyTableauFilters();
        }
    };

    viz = new tableau.Viz(containerDiv, url, options);
}

// ==============================
// Tableau Filter Logic
// ==============================
function applyTableauFilters() {
    if (!viz) return;

    const workbook = viz.getWorkbook();
    const activeSheet = workbook.getActiveSheet();

    const moodValue = document.getElementById("moodFilter").value;
    const yearValue = document.getElementById("yearFilter").value;

    if (activeSheet.getSheetType() === "dashboard") {
        const worksheets = activeSheet.getWorksheets();
        worksheets.forEach(sheet => {
            applyFiltersToSheet(sheet, moodValue, yearValue);
        });
    } else {
        applyFiltersToSheet(activeSheet, moodValue, yearValue);
    }
}

function applyFiltersToSheet(sheet, moodValue, yearValue) {
    if (moodValue) sheet.applyFilterAsync("Mood", moodValue, tableau.FilterUpdateType.REPLACE);
    else sheet.clearFilterAsync("Mood");

    if (yearValue) sheet.applyFilterAsync("Year", yearValue, tableau.FilterUpdateType.REPLACE);
    else sheet.clearFilterAsync("Year");
}

// ==============================
// Backend Integration
// ==============================

// Load Mood Cards
async function loadMoodCards() {
    try {
        const res = await fetch(`${API_BASE}/api/moods`);
        const data = await res.json();

        const container = document.getElementById("moodCards");
        container.innerHTML = "";

        data.forEach(item => {
            const card = document.createElement("div");
            card.className = "mood-card";
            card.innerHTML = `
                <h3>${item.mood}</h3>
                <p>${item.count} songs</p>
            `;
            card.onclick = () => {
                document.getElementById("moodFilter").value = item.mood;
                applyFilters();
            };
            container.appendChild(card);
        });
    } catch (err) {
        console.error("❌ Error loading mood cards:", err);
    }
}

// Load Songs Table
async function loadSongs() {
    try {
        const mood = document.getElementById("moodFilter").value;
        const year = document.getElementById("yearFilter").value;

        let url = `${API_BASE}/api/songs?`;
        if (mood) url += `mood=${encodeURIComponent(mood)}&`;
        if (year) url += `year=${year}`;

        const res = await fetch(url);
        const songs = await res.json();

        const tbody = document.querySelector("#songTable tbody");
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

// ==============================
// Apply Filters (Both Tableau + Backend)
// ==============================
function applyFilters() {
    applyTableauFilters(); // Tableau dashboard
    loadSongs();           // Backend table
}

// ==============================
// Event Listeners
// ==============================
document.getElementById("moodFilter").addEventListener("change", applyFilters);
document.getElementById("yearFilter").addEventListener("change", applyFilters);

// Optional: Back to Home button
const backBtn = document.getElementById("backHomeBtn");
if (backBtn) backBtn.addEventListener("click", () => {
    window.location.href = "index.html";
});

// ==============================
// Initialize Everything on Page Load
// ==============================
window.onload = () => {
    initViz();
    loadMoodCards();
    loadSongs();
};
