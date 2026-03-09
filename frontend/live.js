// ----------------------------
// Config
// ----------------------------
const backendBase = "http://127.0.0.1:8000";
const MOODS = ["pop", "hip hop", "sad", "chill", "party", "workout", "lofi", "romantic"];

// ----------------------------
// Initialization
// ----------------------------
window.onload = () => {
  document.getElementById("searchBtn").addEventListener("click", searchSongs);
  loadCategories();
  renderMoodButtons();
};

async function loadCategories() {
  const container = document.getElementById("categoryContainer");

  try {
    const res = await fetch(`${backendBase}/live/categories`);
    const categories = await res.json();

    categories.forEach(cat => {
      const btn = document.createElement("button");
      btn.textContent = cat;  // category is just a string
      btn.className = "category-btn";

      btn.onclick = () => fetchSongsByMood(cat);

      container.appendChild(btn);
    });

  } catch (err) {
    console.error("Failed to load categories:", err);
  }
}

// ----------------------------
// Render Mood Buttons
// ----------------------------
function renderMoodButtons() {
  const container = document.getElementById("mood-buttons");
  MOODS.forEach(mood => {
    const btn = document.createElement("button");
    btn.textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
    btn.className = "mood-btn";
    btn.onclick = () => fetchSongsByMood(mood);
    container.appendChild(btn);
  });
}

// ----------------------------
// Update UI Helper
// ----------------------------
function updateView(title, data) {
  document.getElementById("view-title").textContent = title;
  const list = document.getElementById("songList");
  list.innerHTML = "";

  if (!Array.isArray(data) || data.length === 0) {
    list.innerHTML = "<p>No results found.</p>";
    return;
  }

  data.forEach(item => {
    const card = document.createElement("div");
    card.className = "song-card";

    const displayName = item.name || "Unknown Track";
    const artistHTML = item.artist ? `<div class="song-artist">${item.artist}</div>` : "";
    const spotifyURL = item.spotify_url || "#";

    card.innerHTML = `
      <span class="song-title">${displayName}</span>
      ${artistHTML}
      <a href="${spotifyURL}" class="spotify-link" target="_blank">🔗 Open in Spotify</a>
    `;

    list.appendChild(card);
  });
}

// ----------------------------
// API Calls
// ----------------------------
async function searchSongs() {
  const query = document.getElementById("searchInput").value.trim();
  if (!query) return;

  try {
    const res = await fetch(`${backendBase}/live/search?song_name=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();

    console.log("SEARCH RESPONSE:", data); // debug

    const songs = data.results || data;

    updateView(`Search results for "${query}"`, songs);

  } catch (err) {
    console.error("Search failed:", err);
    updateView("Search Results", []);
  }
}

/*async function fetchCategoryPlaylists(categoryId, categoryName) {
  try {
    const res = await fetch(`${backendBase}/live/category_tracks?category_id=${categoryId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const playlists = await res.json();
    updateView(`${categoryName} Playlists`, Array.isArray(playlists) ? playlists : []);
  } catch (err) {
    console.error("Category fetch failed:", err);
    updateView(`${categoryName} Playlists`, []);
  }
}
*/

async function fetchSongsByMood(mood) {
  const list = document.getElementById("songList");
  list.innerHTML = "<div>Loading recommendations...</div>";

  try {
    const res = await fetch(`${backendBase}/live/songs_by_mood?mood=${encodeURIComponent(mood)}`);
    const songs = await res.json();

    if (songs.error) {
      console.error("Backend error:", songs.error);
      list.innerHTML = `<p>Error loading songs: ${songs.error}</p>`;
      return;
    }

    updateView(`Vibe: ${mood.charAt(0).toUpperCase() + mood.slice(1)}`, Array.isArray(songs) ? songs : []);
  } catch (err) {
    console.error("Mood fetch failed:", err);
    list.innerHTML = "<p>Error loading songs. Check console.</p>";
  }
}