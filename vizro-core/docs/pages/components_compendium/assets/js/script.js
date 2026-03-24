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

/* Carousel - infinite loop with cloned slides */
(function initCarousel() {
  const carouselSection = document.querySelector(".carousel-section");
  if (!carouselSection) return;

  const carousel = carouselSection.querySelector(".carousel");
  const track = carousel?.querySelector(".carousel__track");
  const leftButton = carouselSection.querySelector(".carousel__button--left");
  const rightButton = carouselSection.querySelector(".carousel__button--right");

  if (!carousel || !track) return;

  /* Clone first slide to end and last slide to start for seamless loop */
  const originalItems = [...track.querySelectorAll(".carousel__item")];
  if (!originalItems.length || !leftButton || !rightButton) return;

  const firstClone = originalItems[0].cloneNode(true);
  const lastClone = originalItems[originalItems.length - 1].cloneNode(true);
  track.insertBefore(lastClone, track.firstChild);
  track.appendChild(firstClone);

  const items = [...track.querySelectorAll(".carousel__item")];
  const realFirstIndex = 1;
  const realLastIndex = items.length - 2;

  let currentIndex = realFirstIndex;
  let autoRotateTimeoutId = null;
  let isTransitioning = false;
  const AUTO_ROTATE_DELAY = 7000;
  const WRAP_DELAY = 7000;

  const getScrollAmount = () => {
    const gap = parseFloat(getComputedStyle(track).gap) || 16;
    return items[0].offsetWidth + gap;
  };

  const getVisibleItems = () => {
    const trackContainer = carousel.querySelector(".carousel__track-container");
    return Math.floor(trackContainer.offsetWidth / getScrollAmount());
  };

  const updateCarousel = (withoutTransition = false) => {
    if (withoutTransition) {
      track.style.transition = "none";
    }
    track.style.transform = `translateX(${-currentIndex * getScrollAmount()}px)`;
    if (withoutTransition) {
      requestAnimationFrame(() => {
        track.offsetHeight;
        track.style.transition = "";
      });
    }
    leftButton.disabled = false;
    rightButton.disabled = false;
  };

  const jumpToRealSlide = () => {
    if (currentIndex === 0) {
      currentIndex = realLastIndex;
    } else if (currentIndex === items.length - 1) {
      currentIndex = realFirstIndex;
    }
    updateCarousel(true);
    isTransitioning = false;
  };

  const handleTransitionEnd = (e) => {
    if (e.target !== track || e.propertyName !== "transform") return;
    track.removeEventListener("transitionend", handleTransitionEnd);
    jumpToRealSlide();
  };

  const scrollLeft = () => {
    if (isTransitioning) return;
    currentIndex--;
    if (currentIndex === 0) {
      isTransitioning = true;
      track.addEventListener("transitionend", handleTransitionEnd);
    }
    updateCarousel();
  };

  const scrollRight = () => {
    if (isTransitioning) return;
    currentIndex++;
    if (currentIndex === items.length - 1) {
      isTransitioning = true;
      track.addEventListener("transitionend", handleTransitionEnd);
    }
    updateCarousel();
  };

  const stopAutoRotate = () => {
    if (autoRotateTimeoutId !== null) {
      clearTimeout(autoRotateTimeoutId);
      autoRotateTimeoutId = null;
    }
  };

  const scheduleNextTick = () => {
    const isOnLastRealSlide = currentIndex >= realLastIndex;
    const delay = isOnLastRealSlide ? WRAP_DELAY : AUTO_ROTATE_DELAY;
    autoRotateTimeoutId = setTimeout(() => {
      scrollRight();
      scheduleNextTick();
    }, delay);
  };

  const startAutoRotate = () => {
    stopAutoRotate();
    scheduleNextTick();
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

  carouselSection.addEventListener("mouseenter", stopAutoRotate);
  carouselSection.addEventListener("mouseleave", startAutoRotate);
  carouselSection.addEventListener("focusin", stopAutoRotate);
  carouselSection.addEventListener("focusout", startAutoRotate);

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      currentIndex = realFirstIndex;
      updateCarousel(true);
      pauseAndRestart();
    }, 250);
  });

  updateCarousel(true);
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

/* Long code blocks: collapse after 30 lines with "Show full code" button */
(function initLongCodeBlocks() {
  const MAX_VISIBLE_LINES = 30;

  document.querySelectorAll(".code-block").forEach((block) => {
    const pre = block.querySelector("pre");
    const code = block.querySelector("code");
    if (!pre || !code) return;

    const lineCount = code.textContent.split("\n").length;
    if (lineCount <= MAX_VISIBLE_LINES) return;

    const wrapper = document.createElement("div");
    wrapper.className = "code-block__pre-wrapper";
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);

    const showMoreBtn = document.createElement("button");
    showMoreBtn.className = "code-block__show-more";
    showMoreBtn.setAttribute("type", "button");
    showMoreBtn.textContent = "Show full code";
    showMoreBtn.addEventListener("click", () => {
      const collapsed = block.classList.toggle("code-block--collapsed");
      showMoreBtn.textContent = collapsed ? "Show full code" : "Show less";
    });

    block.classList.add("code-block--collapsed");
    block.appendChild(showMoreBtn);
  });
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

document.addEventListener("DOMContentLoaded", () => {});
