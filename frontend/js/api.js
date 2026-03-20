const API_BASE_URL = "http://127.0.0.1:8000";
const FALLBACK_POSTER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 480'%3E%3Crect width='320' height='480' fill='%231b263d'/%3E%3Crect x='24' y='24' width='272' height='432' rx='18' fill='%230f1829' stroke='%232c3a58' stroke-width='4'/%3E%3Ctext x='160' y='220' text-anchor='middle' fill='%23e8edf7' font-family='Segoe UI, Arial, sans-serif' font-size='30' font-weight='700'%3EMovieAI%3C/text%3E%3Ctext x='160' y='260' text-anchor='middle' fill='%23b6bfd1' font-family='Segoe UI, Arial, sans-serif' font-size='20'%3EПостер відсутній%3C/text%3E%3C/svg%3E";
const TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500";

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

  if (posterPath.startsWith("/")) {
    return `${TMDB_IMAGE_BASE_URL}${posterPath}`;
  }

  return `${API_BASE_URL}/movies/posters/${posterPath}`;
}

window.fetchJson = fetchJson;
window.buildPosterUrl = buildPosterUrl;
