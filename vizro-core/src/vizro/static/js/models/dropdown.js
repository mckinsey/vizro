/**
 * Removes " selected" text from dropdown count elements, showing only the number.
 */
(function () {
  function updateCountElements() {
    document
      .querySelectorAll(".dash-dropdown-value-count")
      .forEach((element) => {
        const text = element.textContent;
        const match = text.match(/^(\d+)/);
        if (match && text.includes("selected")) {
          element.textContent = match[1];
        }
      });
  }

  // Run on initial load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateCountElements);
  } else {
    updateCountElements();
  }

  // Watch for dynamic updates
  new MutationObserver(updateCountElements).observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
  });
})();
