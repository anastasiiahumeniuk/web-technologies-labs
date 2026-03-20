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
  const genres = movie.genres.length > 0 ? movie.genres.join(", ") : "Жанри не вказані";
  return `${movie.year ?? "Рік невідомий"} | ${genres}`;
}

function renderPeople(people) {
  if (people.length === 0) {
    return '<li class="muted">Інформація про акторів відсутня.</li>';
  }

  return people.map((person) => `<li>${person}</li>`).join("");
}

function renderMovieDetails(movie) {
  detailTitle.textContent = movie.title;
  detailMeta.textContent = formatMovieMeta(movie);
  detailOverview.textContent = movie.overview || "Опис фільму відсутній.";
  detailRating.innerHTML = `Рейтинг IMDb: <strong>${movie.imdb_rating ?? "Н/Д"}</strong>`;
  detailPoster.src = window.buildPosterUrl(movie.poster_path);
  detailPoster.alt = `Постер: ${movie.title}`;
  detailPeople.innerHTML = renderPeople(movie.people);
  detailContent.hidden = false;
}

async function loadMovieDetails() {
  const params = new URLSearchParams(window.location.search);
  const movieId = params.get("id");

  if (!movieId) {
    showDetailStatus("У URL не передано ідентифікатор фільму.", "is-warning");
    return;
  }

  showDetailStatus("Завантаження деталей фільму...");

  try {
    const movie = await window.fetchJson(`/movies/${encodeURIComponent(movieId)}`);
    renderMovieDetails(movie);
    showDetailStatus("Дані про фільм успішно завантажено.", "is-success");
  } catch (error) {
    console.error(error);
    showDetailStatus("Не вдалося завантажити деталі фільму. Перевір `id` і роботу бекенду.", "is-error");
  }
}

loadMovieDetails();
