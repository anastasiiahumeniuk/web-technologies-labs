const PAGE_SIZE = 12;

const moviesGrid = document.querySelector("[data-movies-list]");
const moviesStatus = document.querySelector("[data-movies-status]");
const moviesSearchForm = document.querySelector("[data-movies-search-form]");
const moviesSearchInput = document.querySelector("[data-movies-search-input]");
const loadMoreButton = document.querySelector("[data-load-more-button]");

let currentQuery = "";
let currentOffset = 0;
let hasMoreMovies = true;

function createMovieCard(movie) {
  return `
    <article class="card">
      <img src="${window.buildPosterUrl(movie.poster_path)}" alt="Постер: ${movie.title}">
      <div class="card-body">
        <h2>${movie.title}</h2>
        <p class="muted">${movie.year ?? "Рік невідомий"} | IMDb ${movie.imdb_rating ?? "Н/Д"}</p>
        <a class="btn btn-ghost" href="movie-details.html?id=${movie.id}">Деталі</a>
      </div>
    </article>
  `;
}

function renderMovies(movies, append = false) {
  const html = movies.map(createMovieCard).join("");

  if (append) {
    moviesGrid.insertAdjacentHTML("beforeend", html);
    return;
  }

  moviesGrid.innerHTML = html;
}

function showStatus(message, variant = "") {
  moviesStatus.textContent = message;
  moviesStatus.className = `catalog-status ${variant}`.trim();
}

function updateLoadMoreButton() {
  loadMoreButton.hidden = !hasMoreMovies;

  if (!hasMoreMovies) {
    loadMoreButton.disabled = true;
  }
}

async function loadMovies(query = "", append = false) {
  if (!append) {
    currentOffset = 0;
    currentQuery = query;
    hasMoreMovies = true;
    moviesGrid.innerHTML = "";
    loadMoreButton.hidden = true;
    loadMoreButton.disabled = false;
    showStatus("Завантаження фільмів...");
  } else {
    loadMoreButton.disabled = true;
    showStatus("Завантаження наступної порції фільмів...");
  }

  try {
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE),
      offset: String(currentOffset)
    });

    let endpoint = `/movies?${params.toString()}`;
    if (currentQuery) {
      endpoint = `/movies/search?q=${encodeURIComponent(currentQuery)}&limit=${PAGE_SIZE}&offset=${currentOffset}`;
    }

    const movies = await window.fetchJson(endpoint);

    if (movies.length === 0 && !append) {
      hasMoreMovies = false;
      updateLoadMoreButton();
      showStatus("За цим запитом нічого не знайдено.", "is-warning");
      return;
    }

    renderMovies(movies, append);
    currentOffset += movies.length;
    hasMoreMovies = movies.length === PAGE_SIZE;
    updateLoadMoreButton();

    if (!hasMoreMovies) {
      showStatus(`Завантажено всі доступні фільми: ${currentOffset}.`, "is-success");
      return;
    }

    showStatus(`Завантажено фільмів: ${currentOffset}.`, "is-success");
  } catch (error) {
    console.error(error);
    showStatus("Не вдалося завантажити фільми. Перевір, чи бекенд працює на http://127.0.0.1:8000.", "is-error");
    updateLoadMoreButton();
  } finally {
    if (!loadMoreButton.hidden && hasMoreMovies) {
      loadMoreButton.disabled = false;
    }
  }
}

moviesSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadMovies(moviesSearchInput.value.trim());
});

loadMoreButton.addEventListener("click", () => {
  loadMovies(currentQuery, true);
});

loadMovies();
