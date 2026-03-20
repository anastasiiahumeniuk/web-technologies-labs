const detailStatus = document.querySelector("[data-detail-status]");
const detailContent = document.querySelector("[data-detail-content]");
const detailTitle = document.querySelector("[data-detail-title]");
const detailMeta = document.querySelector("[data-detail-meta]");
const detailOverview = document.querySelector("[data-detail-overview]");
const detailRating = document.querySelector("[data-detail-rating]");
const detailPoster = document.querySelector("[data-detail-poster]");
const detailPeople = document.querySelector("[data-detail-people]");

function showDetailStatus(message, variant = "") {
  detailStatus.textContent = message;
  detailStatus.className = `catalog-status ${variant}`.trim();
}

function formatMovieMeta(movie) {
  const genres = movie.genres.length > 0 ? movie.genres.join(", ") : "Genres not specified";
  return `${movie.year ?? "Year unknown"} • ${genres}`;
}

function renderPeople(people) {
  if (people.length === 0) {
    return '<li class="muted">People data is not available.</li>';
  }

  return people.map((person) => `<li>${person}</li>`).join("");
}

function renderMovieDetails(movie) {
  detailTitle.textContent = movie.title;
  detailMeta.textContent = formatMovieMeta(movie);
  detailOverview.textContent = movie.overview || "Overview is not available.";
  detailRating.innerHTML = `IMDb rating: <strong>${movie.imdb_rating ?? "N/A"}</strong>`;
  detailPoster.src = window.buildPosterUrl(movie.poster_path);
  detailPoster.alt = `${movie.title} poster`;
  detailPeople.innerHTML = renderPeople(movie.people);
  detailContent.hidden = false;
}

async function loadMovieDetails() {
  const params = new URLSearchParams(window.location.search);
  const movieId = params.get("id");

  if (!movieId) {
    showDetailStatus("Movie id was not provided in the URL.", "is-warning");
    return;
  }

  showDetailStatus("Loading movie details...");

  try {
    const movie = await window.fetchJson(`/movies/${encodeURIComponent(movieId)}`);
    renderMovieDetails(movie);
    showDetailStatus("Movie details loaded.", "is-success");
  } catch (error) {
    console.error(error);
    showDetailStatus("Failed to load movie details. Check the id and backend server.", "is-error");
  }
}

loadMovieDetails();
