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

/*
 * Search — fuzzy matching over title, aliases, description and code.
 * Backed by Fuse.js (loaded as a separate <script>); falls back to a
 * substring search if Fuse is unavailable. Aliases come from
 * assets/js/search-keywords.json keyed by element id.
 */
(function initSearch() {
  const MIN_SEARCH_LENGTH = 2;
  const SEARCH_DEBOUNCE_MS = 80;
  const KEYWORDS_URL = "assets/js/search-keywords.json";
  const SUGGESTED_TERMS = ["graph", "filter", "table"];

  const searchInput = document.getElementById("component-search");
  const searchClear = document.getElementById("search-clear");
  const searchResults = document.getElementById("search-results");
  const compendiumSection = document.querySelector(".compendium-section");

  if (!searchInput) return;

  let items = [];
  let fuse = null;
  let aliasesById = {};
  let categoryStateSnapshot = null;
  let debounceTimer = null;

  const getText = (el) =>
    el ? el.textContent.replace(/\s+/g, " ").trim() : "";

  function buildIndex() {
    const indexed = [];

    document.querySelectorAll(".component").forEach((el) => {
      const titleEl = el.querySelector(".component__name");
      const descEl = el.querySelector(".component__description");
      const id = el.id || "";
      indexed.push({
        id,
        element: el,
        kind: "component",
        titleEl,
        descEl,
        title: getText(titleEl),
        description: getText(descEl),
        code: Array.from(el.querySelectorAll("code"))
          .map((c) => c.textContent)
          .join("\n"),
        aliases: (aliasesById[id]?.aliases || []).join(" "),
      });
    });

    document.querySelectorAll(".component_card").forEach((el) => {
      const titleEl = el.querySelector(".component_card_title");
      const id = el.id || "";
      indexed.push({
        id,
        element: el,
        kind: "card",
        titleEl,
        descEl: null,
        title: getText(titleEl),
        description: "",
        code: Array.from(el.querySelectorAll("code"))
          .map((c) => c.textContent)
          .join("\n"),
        aliases: (aliasesById[id]?.aliases || []).join(" "),
      });
    });

    const selectorsParent = document.querySelector(
      ".component_selectors#selectors",
    );
    if (selectorsParent) {
      const titleEl = selectorsParent.querySelector(".component__name");
      const descEl = selectorsParent.querySelector(".component__description");
      indexed.push({
        id: "selectors",
        element: selectorsParent,
        kind: "selectors-parent",
        titleEl,
        descEl,
        title: getText(titleEl),
        description: getText(descEl),
        code: "",
        aliases: (aliasesById.selectors?.aliases || []).join(" "),
      });
    }

    return indexed;
  }

  function buildFuse(indexed) {
    if (typeof Fuse === "undefined") return null;
    return new Fuse(indexed, {
      keys: [
        { name: "title", weight: 0.5 },
        { name: "aliases", weight: 0.3 },
        { name: "description", weight: 0.15 },
        { name: "code", weight: 0.05 },
      ],
      threshold: 0.35,
      ignoreLocation: true,
      minMatchCharLength: 2,
    });
  }

  /* Highlighting */

  function escapeRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function walkTextNodes(root, fn) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        const tag = parent.tagName;
        if (
          tag === "CODE" ||
          tag === "PRE" ||
          tag === "SCRIPT" ||
          tag === "STYLE"
        ) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const collected = [];
    while (walker.nextNode()) collected.push(walker.currentNode);
    collected.forEach(fn);
  }

  function applyHighlight(originalHTML, regex) {
    const tmp = document.createElement("div");
    tmp.innerHTML = originalHTML;
    walkTextNodes(tmp, (node) => {
      const value = node.nodeValue;
      regex.lastIndex = 0;
      if (!regex.test(value)) return;
      regex.lastIndex = 0;
      const frag = document.createDocumentFragment();
      let lastIndex = 0;
      let match = regex.exec(value);
      while (match !== null) {
        if (match.index > lastIndex) {
          frag.appendChild(
            document.createTextNode(value.slice(lastIndex, match.index)),
          );
        }
        const mark = document.createElement("mark");
        mark.className = "search-highlight";
        mark.textContent = match[0];
        frag.appendChild(mark);
        lastIndex = match.index + match[0].length;
        if (match[0].length === 0) regex.lastIndex++;
        match = regex.exec(value);
      }
      if (lastIndex < value.length) {
        frag.appendChild(document.createTextNode(value.slice(lastIndex)));
      }
      node.parentNode.replaceChild(frag, node);
    });
    return tmp.innerHTML;
  }

  function highlightItem(item, term) {
    const regex = new RegExp(escapeRegex(term), "gi");
    [item.titleEl, item.descEl].forEach((el) => {
      if (!el) return;
      if (el.dataset.searchOriginal === undefined) {
        el.dataset.searchOriginal = el.innerHTML;
      }
      el.innerHTML = applyHighlight(el.dataset.searchOriginal, regex);
    });
  }

  function clearHighlights() {
    items.forEach((item) => {
      [item.titleEl, item.descEl].forEach((el) => {
        if (!el) return;
        if (el.dataset.searchOriginal !== undefined) {
          el.innerHTML = el.dataset.searchOriginal;
          delete el.dataset.searchOriginal;
        }
      });
    });
  }

  /* Category expand/collapse state */

  function snapshotCategoryState() {
    if (categoryStateSnapshot) return;
    categoryStateSnapshot = new Map();
    document.querySelectorAll(".category").forEach((cat) => {
      categoryStateSnapshot.set(cat, cat.classList.contains("expanded"));
    });
  }

  function restoreCategoryState() {
    if (!categoryStateSnapshot) return;
    categoryStateSnapshot.forEach((wasExpanded, cat) => {
      cat.classList.toggle("expanded", wasExpanded);
      cat.classList.remove("has-results");
    });
    categoryStateSnapshot = null;
  }

  /* Match application */

  function setMatchedClasses(matchedSet) {
    items.forEach((item) => {
      item.element.classList.toggle("search-match", matchedSet.has(item));
    });
  }

  function expandSelectorsParentIfChildMatches() {
    const selectorsParent = document.querySelector(
      ".component_selectors#selectors",
    );
    if (!selectorsParent) return;
    const hasChildMatch =
      selectorsParent.querySelectorAll(".component_card.search-match").length >
      0;
    selectorsParent.classList.toggle(
      "has-results",
      hasChildMatch || selectorsParent.classList.contains("search-match"),
    );
  }

  function updateCategoryVisibility() {
    document.querySelectorAll(".category").forEach((category) => {
      const hasMatches = category.querySelector(".search-match") !== null;
      category.classList.toggle("has-results", hasMatches);
      category.classList.toggle("expanded", hasMatches);
    });
    expandSelectorsParentIfChildMatches();
  }

  /* Result feedback */

  function renderMessage(payload) {
    if (!searchResults) return;
    if (!payload) {
      searchResults.textContent = "";
      searchResults.classList.remove("visible");
      return;
    }
    if (typeof payload === "string") {
      searchResults.textContent = payload;
      searchResults.classList.add("visible");
      return;
    }
    searchResults.textContent = "";
    searchResults.classList.add("visible");
    const text = document.createElement("span");
    text.textContent = payload.text;
    searchResults.appendChild(text);
    if (payload.clearable) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "search-results__clear";
      btn.textContent = "Clear search";
      btn.addEventListener("click", clearSearch);
      searchResults.appendChild(btn);
    }
  }

  function messageForCount(count, term) {
    if (count === 0) {
      return {
        text: `No components match "${term}". Try: ${SUGGESTED_TERMS.join(", ")}.`,
        clearable: true,
      };
    }
    return `Found ${count} component${count !== 1 ? "s" : ""}.`;
  }

  /* Search engine */

  function runFuzzySearch(term) {
    if (!fuse) {
      const lowered = term.toLowerCase();
      return items.filter((it) =>
        `${it.title} ${it.description} ${it.aliases} ${it.code}`
          .toLowerCase()
          .includes(lowered),
      );
    }
    return fuse.search(term).map((r) => r.item);
  }

  function expandMatchesWithSelectorsChildren(matchedSet) {
    const parent = items.find((it) => it.kind === "selectors-parent");
    if (!parent || !matchedSet.has(parent)) return;
    items.forEach((it) => {
      if (it.kind === "card") matchedSet.add(it);
    });
  }

  function performSearch() {
    const term = searchInput.value.trim();
    const len = term.length;
    searchClear?.classList.toggle("visible", len > 0);

    if (len === 0) {
      compendiumSection?.classList.remove("searching");
      clearHighlights();
      setMatchedClasses(new Set());
      restoreCategoryState();
      renderMessage("");
      return;
    }

    if (len < MIN_SEARCH_LENGTH) {
      compendiumSection?.classList.remove("searching");
      clearHighlights();
      setMatchedClasses(new Set());
      restoreCategoryState();
      renderMessage(`Type at least ${MIN_SEARCH_LENGTH} characters to search.`);
      return;
    }

    snapshotCategoryState();
    compendiumSection?.classList.add("searching");
    clearHighlights();

    const matchedItems = runFuzzySearch(term);
    const matchedSet = new Set(matchedItems);
    expandMatchesWithSelectorsChildren(matchedSet);
    matchedSet.forEach((m) => {
      highlightItem(m, term);
    });
    setMatchedClasses(matchedSet);
    updateCategoryVisibility();
    renderMessage(messageForCount(matchedSet.size, term));
  }

  function clearSearch() {
    searchInput.value = "";
    searchInput.focus();
    performSearch();
  }

  function onInput() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(performSearch, SEARCH_DEBOUNCE_MS);
  }

  /* Boot: load aliases, build index, then wire input. */
  fetch(KEYWORDS_URL, { credentials: "same-origin" })
    .then((res) => (res.ok ? res.json() : {}))
    .catch(() => ({}))
    .then((data) => {
      aliasesById = data || {};
      items = buildIndex();
      fuse = buildFuse(items);
      if (searchInput.value.trim().length > 0) performSearch();
    });

  searchInput.addEventListener("input", onInput);
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Escape") clearSearch();
  });
  searchClear?.addEventListener("click", clearSearch);
})();

/* Navigation — assigned to globalThis for inline handlers in index.html */
globalThis.toggleNav = () => {
  document.getElementById("leftNav")?.classList.toggle("open");
};

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

globalThis.toggleNavCategory = (header) => {
  header.classList.toggle("collapsed");
};

globalThis.toggleNavSubcategory = (header) => {
  header.classList.toggle("collapsed");
};
