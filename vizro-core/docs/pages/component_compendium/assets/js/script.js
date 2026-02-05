/*  Collapsible categories */
(function initCollapsibleCategories() {
  document.querySelectorAll(".category").forEach((category) => {
    const title = category.querySelector(".category__title");
    const content = category.querySelector(".category__content");
    if (!title || !content) return;

    const toggle = () => {
      const expanded = category.classList.toggle("expanded");
      title.setAttribute("aria-expanded", expanded);
    };

    title.addEventListener("click", toggle);
    title.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggle();
      }
    });

    category.classList.add("expanded");
    title.setAttribute("role", "button");
    title.setAttribute("tabindex", "0");
    title.setAttribute("aria-expanded", "true");
  });
})();

/* Carousel */
(function initCarousel() {
  const carousel = document.querySelector(".carousel");
  if (!carousel) return;

  const track = carousel.querySelector(".carousel__track");
  const items = [...track.querySelectorAll(".carousel__item")];
  const leftButton = carousel.querySelector(".carousel__button--left");
  const rightButton = carousel.querySelector(".carousel__button--right");

  if (!track || !items.length || !leftButton || !rightButton) return;

  let currentIndex = 0;
  let autoRotateInterval;
  const AUTO_ROTATE_DELAY = 4000;

  const getScrollAmount = () => {
    const gap = parseFloat(getComputedStyle(track).gap) || 16;
    return items[0].offsetWidth + gap;
  };

  const getVisibleItems = () => {
    const container = carousel.querySelector(".carousel__track-container");
    return Math.floor(container.offsetWidth / getScrollAmount());
  };

  const updateCarousel = () => {
    track.style.transform = `translateX(${-currentIndex * getScrollAmount()}px)`;

    const maxIndex = Math.max(0, items.length - getVisibleItems());
    leftButton.disabled = currentIndex === 0;
    rightButton.disabled = currentIndex >= maxIndex;
  };

  const scrollLeft = () => {
    if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
    }
  };

  const scrollRight = () => {
    const maxIndex = Math.max(0, items.length - getVisibleItems());
    currentIndex = currentIndex < maxIndex ? currentIndex + 1 : 0;
    updateCarousel();
  };

  const stopAutoRotate = () => {
    clearInterval(autoRotateInterval);
    autoRotateInterval = null;
  };

  const startAutoRotate = () => {
    stopAutoRotate();
    autoRotateInterval = setInterval(scrollRight, AUTO_ROTATE_DELAY);
  };

  const pauseAndRestart = () => {
    stopAutoRotate();
    setTimeout(startAutoRotate, AUTO_ROTATE_DELAY);
  };

  leftButton.addEventListener("click", () => {
    scrollLeft();
    pauseAndRestart();
  });

  rightButton.addEventListener("click", () => {
    scrollRight();
    pauseAndRestart();
  });

  [leftButton, rightButton].forEach((button) => {
    button.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        button.click();
      }
    });
  });

  carousel.addEventListener("mouseenter", stopAutoRotate);
  carousel.addEventListener("mouseleave", startAutoRotate);
  carousel.addEventListener("focusin", stopAutoRotate);
  carousel.addEventListener("focusout", startAutoRotate);

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      currentIndex = 0;
      updateCarousel();
      pauseAndRestart();
    }, 250);
  });

  updateCarousel();
  startAutoRotate();
})();

/*  Copy code */
(function initCopyButtons() {
  document.querySelectorAll(".code-block__copy-button").forEach((button) => {
    const copy = () => {
      const code = button.closest(".code-block")?.querySelector("code");
      if (!code) return;

      const text = code.textContent;

      if (navigator.clipboard?.writeText) {
        navigator.clipboard.writeText(text).then(
          () => showFeedback(button),
          () => fallbackCopy(text, button),
        );
      } else {
        fallbackCopy(text, button);
      }
    };

    button.addEventListener("click", copy);
    button.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        copy();
      }
    });
  });

  function showFeedback(button) {
    const textEl = button.querySelector(".code-block__copy-text");
    const original = textEl.textContent;

    button.classList.add("copied");
    textEl.textContent = "Copied!";

    setTimeout(() => {
      button.classList.remove("copied");
      textEl.textContent = original;
    }, 2000);
  }

  function fallbackCopy(text, button) {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";

    document.body.appendChild(textarea);
    textarea.select();

    try {
      document.execCommand("copy");
      showFeedback(button);
    } catch (e) {
      console.error("Copy failed", e);
    }

    document.body.removeChild(textarea);
  }
})();

/* Search */
(function initSearch() {
  const searchInput = document.getElementById("component-search");
  const searchClear = document.getElementById("search-clear");
  const searchResults = document.getElementById("search-results");
  const compendiumSection = document.querySelector(".compendium-section");

  if (!searchInput) return;

  const getSearchableItems = () => {
    const regularComponents = Array.from(
      document.querySelectorAll(".component"),
    );
    const selectorCards = Array.from(
      document.querySelectorAll(".component_card"),
    );

    return {
      regular: regularComponents.map((el) => ({
        element: el,
        name:
          el.querySelector(".component__name")?.textContent.toLowerCase() || "",
        nameEl: el.querySelector(".component__name"),
      })),
      selectors: selectorCards.map((el) => ({
        element: el,
        name:
          el
            .querySelector(".component_card_title")
            ?.textContent.toLowerCase() || "",
        nameEl: el.querySelector(".component_card_title"),
      })),
    };
  };

  function performSearch() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const items = getSearchableItems();
    const allItems = [...items.regular, ...items.selectors];

    toggleSearchState(!!searchTerm);

    if (!searchTerm) {
      resetSearch(allItems);
      return;
    }

    const matchCount = searchItems(allItems, searchTerm);
    updateCategoryVisibility();
    updateSearchResults(matchCount, allItems.length);
  }

  function toggleSearchState(isSearching) {
    searchClear.classList.toggle("visible", isSearching);
    compendiumSection?.classList.toggle("searching", isSearching);
  }

  function resetSearch(items) {
    clearHighlights(items);
    updateSearchResults(0, 0);

    document.querySelectorAll(".category").forEach((cat) => {
      cat.classList.add("expanded");
    });

    items.forEach((item) => item.element.classList.remove("search-match"));
  }

  function searchItems(items, searchTerm) {
    let matchCount = 0;

    items.forEach((item) => {
      const isMatch = item.name.includes(searchTerm);

      item.element.classList.toggle("search-match", isMatch);

      if (isMatch) {
        matchCount++;
        highlightText(item.nameEl, searchTerm);
      }
    });

    return matchCount;
  }

  function updateCategoryVisibility() {
    document.querySelectorAll(".category").forEach((category) => {
      const hasRegularMatches =
        category.querySelectorAll(".component.search-match").length > 0;
      const hasSelectorMatches =
        category.querySelectorAll(".component_card.search-match").length > 0;

      const hasMatches = hasRegularMatches || hasSelectorMatches;

      category.classList.toggle("has-results", hasMatches);
      category.classList.toggle("expanded", hasMatches);
    });
  }

  function highlightText(element, searchTerm) {
    if (!element) return;

    const originalText =
      element.getAttribute("data-original-text") || element.textContent;

    if (!element.getAttribute("data-original-text")) {
      element.setAttribute("data-original-text", originalText);
    }

    if (!searchTerm) {
      element.textContent = originalText;
      return;
    }

    const regex = new RegExp(`(${escapeRegex(searchTerm)})`, "gi");
    element.innerHTML = originalText.replace(
      regex,
      '<span class="search-highlight">$1</span>',
    );
  }

  function clearHighlights(items) {
    items.forEach((item) => {
      if (item.nameEl?.getAttribute("data-original-text")) {
        item.nameEl.textContent =
          item.nameEl.getAttribute("data-original-text");
      }
    });
  }

  function updateSearchResults(matches) {
    const hasSearchTerm = searchInput.value.trim().length > 0;

    if (hasSearchTerm && matches === 0) {
      searchResults.textContent = "No components found";
      searchResults.classList.add("visible");
    } else if (matches > 0) {
      searchResults.textContent = `Found ${matches} component${matches !== 1 ? "s" : ""}`;
      searchResults.classList.add("visible");
    } else {
      searchResults.textContent = "";
      searchResults.classList.remove("visible");
    }
  }

  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function clearSearch() {
    searchInput.value = "";
    searchInput.focus();
    performSearch();
  }

  searchInput.addEventListener("input", performSearch);
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Escape") clearSearch();
  });
  searchClear.addEventListener("click", clearSearch);
})();

/* Navigation */
function toggleNav() {
  document.getElementById("leftNav")?.classList.toggle("open");
}

const sections = document.querySelectorAll("[id]");
const navLinks = document.querySelectorAll(".nav-link");

window.addEventListener("scroll", () => {
  let current = "";

  sections.forEach((section) => {
    if (pageYOffset >= section.offsetTop - 100) {
      current = section.id;
    }
  });

  navLinks.forEach((link) => {
    link.classList.toggle(
      "active",
      link.getAttribute("href") === `#${current}`,
    );
  });
});

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    if (window.innerWidth <= 968) {
      document.getElementById("leftNav")?.classList.remove("open");
    }
  });
});

function toggleNavCategory(header) {
  header.classList.toggle("collapsed");
}

function toggleNavSubcategory(header) {
  header.classList.toggle("collapsed");
}

document.addEventListener("DOMContentLoaded", function () {});
