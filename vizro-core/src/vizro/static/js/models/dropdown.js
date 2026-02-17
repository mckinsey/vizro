/**
 * Cleans up dropdown value count display by removing " selected" text
 * and showing only the number in a styled bubble.
 */
function cleanDropdownValueCount() {
  // Use MutationObserver to watch for changes to dropdown count elements
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === "childList" || mutation.type === "characterData") {
        const countElements = document.querySelectorAll(
          ".dash-dropdown-value-count",
        );
        countElements.forEach((element) => {
          const text = element.textContent;
          // Extract just the number from "X selected" format
          const match = text.match(/^(\d+)/);
          if (match && text.includes("selected")) {
            element.textContent = match[1];
          }
        });
      }
    });
  });

  // Observe the entire document for changes
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
    characterDataOldValue: true,
  });

  // Also run once on initial load
  const countElements = document.querySelectorAll(".dash-dropdown-value-count");
  countElements.forEach((element) => {
    const text = element.textContent;
    const match = text.match(/^(\d+)/);
    if (match && text.includes("selected")) {
      element.textContent = match[1];
    }
  });
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", cleanDropdownValueCount);
} else {
  cleanDropdownValueCount();
}
