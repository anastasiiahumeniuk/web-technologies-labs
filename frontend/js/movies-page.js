const moviesGrid = document.querySelector("[data-movies-list]");
const moviesStatus = document.querySelector("[data-movies-status]");
const moviesSearchForm = document.querySelector("[data-movies-search-form]");
const moviesSearchInput = document.querySelector("[data-movies-search-input]");

function renderMovies(movies) {
  moviesGrid.innerHTML = movies
    .map(
      (movie) => `
        <article class="card">
          <img src="${window.buildPosterUrl(movie.poster_path)}" alt="${movie.title} poster">
          <div class="card-body">
            <h2>${movie.title}</h2>
            <p class="muted">${movie.year ?? "Year unknown"} • IMDb ${movie.imdb_rating ?? "N/A"}</p>
            <a class="btn btn-ghost" href="movie-details.html?id=${movie.id}">Details</a>
          </div>
        </article>
      `
    )
    .join("");
}

function showStatus(message, variant = "") {
  moviesStatus.textContent = message;
  moviesStatus.className = `catalog-status ${variant}`.trim();
}

async function loadMovies(query = "") {
  showStatus("Loading movies...");
  moviesGrid.innerHTML = "";

  try {
    const endpoint = query
      ? `/movies/search?q=${encodeURIComponent(query)}&limit=12`
      : "/movies?limit=12";
    const movies = await window.fetchJson(endpoint);

    if (movies.length === 0) {
      showStatus("No movies found for this request.", "is-warning");
      return;
    }

    renderMovies(movies);
    showStatus(`Loaded ${movies.length} movie(s).`, "is-success");
  } catch (error) {
    console.error(error);
    showStatus("Failed to load movies. Check that the backend is running on http://127.0.0.1:8000.", "is-error");
  }
}

moviesSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadMovies(moviesSearchInput.value.trim());
});

loadMovies();
