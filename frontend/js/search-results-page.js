const searchTitle = document.querySelector("[data-search-title]");
const searchSummary = document.querySelector("[data-search-summary]");
const searchStatus = document.querySelector("[data-search-status]");
const searchGrid = document.querySelector("[data-search-grid]");

function showSearchStatus(message, variant = "") {
  searchStatus.textContent = message;
  searchStatus.className = `catalog-status ${variant}`.trim();
}

function renderSearchResults(movies) {
  searchGrid.innerHTML = movies
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

async function loadSearchResults() {
  const params = new URLSearchParams(window.location.search);
  const query = params.get("q")?.trim() ?? "";

  if (!query) {
    searchTitle.textContent = "Search Results";
    searchSummary.textContent = "No search query was provided.";
    showSearchStatus("Enter a query on the home page search form.", "is-warning");
    return;
  }

  searchTitle.textContent = `Search Results: "${query}"`;
  searchSummary.textContent = "Searching movies...";
  showSearchStatus("Loading search results...");

  try {
    const movies = await window.fetchJson(`/movies/search?q=${encodeURIComponent(query)}&limit=12`);

    if (movies.length === 0) {
      searchSummary.textContent = "0 results found";
      showSearchStatus("No movies matched your query.", "is-warning");
      return;
    }

    renderSearchResults(movies);
    searchSummary.textContent = `${movies.length} result(s) found`;
    showSearchStatus("Search completed.", "is-success");
  } catch (error) {
    console.error(error);
    searchSummary.textContent = "Search failed";
    showSearchStatus("Failed to load search results. Check that the backend is running.", "is-error");
  }
}

loadSearchResults();
