const API_BASE_URL = "http://127.0.0.1:8000";
const FALLBACK_POSTER = "img/poster1.png";

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}

function buildPosterUrl(posterPath) {
  if (!posterPath) {
    return FALLBACK_POSTER;
  }

  if (posterPath.startsWith("http://") || posterPath.startsWith("https://")) {
    return posterPath;
  }

  return posterPath;
}

window.fetchJson = fetchJson;
window.buildPosterUrl = buildPosterUrl;
