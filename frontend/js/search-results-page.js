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
          <img src="${window.buildPosterUrl(movie.poster_path)}" alt="Постер: ${movie.title}">
          <div class="card-body">
            <h2>${movie.title}</h2>
            <p class="muted">${movie.year ?? "Рік невідомий"} | IMDb ${movie.imdb_rating ?? "Н/Д"}</p>
            <a class="btn btn-ghost" href="movie-details.html?id=${movie.id}">Деталі</a>
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
    searchTitle.textContent = "Результати пошуку";
    searchSummary.textContent = "Пошуковий запит не передано.";
    showSearchStatus("Введіть запит у формі пошуку на головній сторінці.", "is-warning");
    return;
  }

  searchTitle.textContent = `Результати пошуку: "${query}"`;
  searchSummary.textContent = "Пошук фільмів...";
  showSearchStatus("Завантаження результатів пошуку...");

  try {
    const movies = await window.fetchJson(`/movies/search?q=${encodeURIComponent(query)}&limit=12`);

    if (movies.length === 0) {
      searchSummary.textContent = "Збігів не знайдено";
      showSearchStatus("За вашим запитом фільмів не знайдено.", "is-warning");
      return;
    }

    renderSearchResults(movies);
    searchSummary.textContent = `Знайдено результатів: ${movies.length}`;
    showSearchStatus("Пошук завершено успішно.", "is-success");
  } catch (error) {
    console.error(error);
    searchSummary.textContent = "Помилка пошуку";
    showSearchStatus("Не вдалося завантажити результати пошуку. Перевір роботу бекенду.", "is-error");
  }
}

loadSearchResults();
