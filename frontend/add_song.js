const API_BASE = "http://localhost:8000";

// SAFE ELEMENT GETTER
function $(id) {
    return document.getElementById(id);
}

// -------------------
// STATE
// -------------------
let currentPage = 0;
const pageSize = 50; // number of songs per page
let currentSearch = "";
let currentMood = "";

// -------------------
// LOAD SONGS (SEARCH + FILTER + PAGINATION)
// -------------------
async function loadSearchResults(page = 0) {
    currentPage = page;

    try {
        const params = new URLSearchParams();
        params.append("limit", pageSize);
        params.append("offset", currentPage * pageSize);

        if (currentSearch) params.append("search", currentSearch);
        if (currentMood) params.append("mood", currentMood);

        const res = await fetch(`${API_BASE}/api/songs?${params.toString()}&ts=${Date.now()}`);
        if (!res.ok) throw new Error("Fetch failed");

        const songs = await res.json();

        const tbody = document.querySelector("#searchTable tbody");
        if (!tbody) return;

        tbody.innerHTML = "";

        if (!songs.length) {
            tbody.innerHTML = `<tr><td colspan="4">No songs found.</td></tr>`;
            $("pagination").innerHTML = "";
            return;
        }

        songs.forEach(song => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${song.name}</td>
                <td>${song.artists}</td>
                <td>${song.mood || "Neutral"}</td>
                <td>${song.year}</td>
            `;
            tbody.appendChild(row);
        });

        renderPagination(songs.length < pageSize ? 0 : currentPage + 1);

    } catch (err) {
        console.error("Load error:", err);
    }
}

// -------------------
// RENDER PAGINATION
// -------------------
function renderPagination(nextPage) {
    const container = $("pagination");
    if (!container) return;

    container.innerHTML = "";

    if (currentPage > 0) {
        const prevBtn = document.createElement("button");
        prevBtn.textContent = "Prev";
        prevBtn.onclick = () => loadSearchResults(currentPage - 1);
        container.appendChild(prevBtn);
    }

    if (nextPage > 0) {
        const nextBtn = document.createElement("button");
        nextBtn.textContent = "Next";
        nextBtn.onclick = () => loadSearchResults(nextPage);
        container.appendChild(nextBtn);
    }
}

// -------------------
// LOAD MOODS DROPDOWN
// -------------------
async function loadMoods() {
    if (!$("moodSelect")) return;

    try {
        const res = await fetch(`${API_BASE}/api/moods`);
        if (!res.ok) throw new Error("Failed");

        const moods = await res.json();
        $("moodSelect").innerHTML = `<option value="">All Moods</option>`;
        moods.forEach(m => {
            const option = document.createElement("option");
            option.value = m.mood;
            option.textContent = `${m.mood} (${m.count})`;
            $("moodSelect").appendChild(option);
        });
    } catch (err) {
        console.error("Mood load error:", err);
    }
}

// -------------------
// SEARCH EVENTS
// -------------------
if ($("searchBtn")) {
    $("searchBtn").addEventListener("click", () => {
        currentSearch = $("searchInput").value.trim();
        currentMood = $("moodSelect")?.value || "";
        loadSearchResults(0);
    });
}

if ($("searchInput")) {
    $("searchInput").addEventListener("keyup", e => {
        if (e.key === "Enter") {
            currentSearch = $("searchInput").value.trim();
            currentMood = $("moodSelect")?.value || "";
            loadSearchResults(0);
        }
    });
}

if ($("moodSelect")) {
    $("moodSelect").addEventListener("change", () => {
        currentSearch = $("searchInput")?.value.trim() || "";
        currentMood = $("moodSelect").value;
        loadSearchResults(0);
    });
}

// -------------------
// ADD SONG LOGIC
// -------------------
const addForm = $("addSongForm"); // Make sure your form has id="addSongForm"
if (addForm) {
    addForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // prevent page reload

        const newSong = {
            id: $("songId").value,
            name: $("songName").value,
            artists: $("songArtists").value,
            year: parseInt($("songYear").value),
            valence: parseFloat($("songValence").value),
            energy: parseFloat($("songEnergy").value),
            danceability: parseFloat($("songDanceability").value),
            acousticness: parseFloat($("songAcousticness").value),
            instrumentalness: parseFloat($("songInstrumentalness").value),
            speechiness: parseFloat($("songSpeechiness").value),
            liveness: parseFloat($("songLiveness").value),
            tempo: parseFloat($("songTempo").value),
            duration_ms: parseInt($("songDuration").value),
            popularity: parseInt($("songPopularity").value),
            loudness: parseFloat($("songLoudness").value),
            mode: parseInt($("songMode").value),
            explicit: parseInt($("songExplicit").value),
            key: parseInt($("songKey").value),
            release_date: $("songReleaseDate").value
        };

        try {
            const res = await fetch(`${API_BASE}/api/songs`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newSong)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.message || "Failed to add song");

            alert(data.message);               // show success
            loadSearchResults(currentPage);    // refresh table
            addForm.reset();                   // clear form
        } catch (err) {
            console.error("Add song error:", err);
            alert("Error adding song: " + err.message);
        }
    });
}

// -------------------
// INITIAL LOAD
// -------------------
window.addEventListener("load", () => {
    loadSearchResults();
    loadMoods();
});

let tableauViz;

function initTableau() {
    const containerDiv = document.getElementById("vizContainer");
    if (!containerDiv) return;

    const url = "https://public.tableau.com/views/YourDashboard/Sheet1"; // replace with your dashboard URL
    const options = {
        width: containerDiv.offsetWidth,
        height: containerDiv.offsetHeight,
        hideTabs: true,
        hideToolbar: true
    };

    // Remove old viz if exists
    if (tableauViz) tableauViz.dispose();

    tableauViz = new tableau.Viz(containerDiv, url, options);
}

// Resize Tableau on window resize
window.addEventListener("resize", () => {
    const containerDiv = document.getElementById("vizContainer");
    if (tableauViz && containerDiv) {
        tableauViz.setFrameSize(containerDiv.offsetWidth, containerDiv.offsetHeight);
    }
});

// Initialize Tableau after page load
window.addEventListener("load", () => {
    initTableau();
});