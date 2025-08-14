// Check if current page is homepage
function isHomePage() {
  const currentPath = window.location.pathname;

  // Homepage patterns: ends with /stable/ or /latest/
  const isHome =
    currentPath.endsWith("/stable/index.html") ||
    currentPath.endsWith("/latest/index.html") ||
    currentPath.endsWith("/stable/") ||
    currentPath.endsWith("/latest/") ||
    currentPath === "/stable" ||
    currentPath === "/latest" ||
    currentPath === "/";

  return isHome;
}

// Generate markdown URL from current page URL
function generateMarkdownUrl() {
  const currentUrl = window.location.href;
  const cleanUrl = currentUrl.split("#")[0].split("?")[0];

  let markdownUrl;
  if (cleanUrl.endsWith("/")) {
    markdownUrl = cleanUrl + "index.md";
  } else if (cleanUrl.endsWith(".html")) {
    markdownUrl = cleanUrl.replace(".html", ".md");
  } else {
    markdownUrl = cleanUrl + "/index.md";
  }

  return markdownUrl;
}

function openMarkdownInNewTab() {
  const markdownUrl = generateMarkdownUrl();
  window.open(markdownUrl, "_blank");
}

async function copyMarkdownContent() {
  const markdownUrl = generateMarkdownUrl();

  // Find the copy button and store original text
  const copyButton = document.querySelector(".markdown-buttons #md-copy");
  const originalText = copyButton ? copyButton.textContent : "Copy for LLM";

  try {
    // Update button text to show loading state
    if (copyButton) {
      copyButton.textContent = "Copying...";
      copyButton.disabled = true;
    }

    // Fetch the markdown file
    const response = await fetch(markdownUrl);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const markdown = await response.text();

    // Copy to clipboard
    navigator.clipboard.writeText(markdown);

    setTimeout(() => {
      copyButton.textContent = originalText;
      copyButton.disabled = false;
    }, 1500);
  } catch (fetchError) {
    console.error("Error fetching markdown:", fetchError);
  }
}

// Add markdown buttons if not homepage and buttons don't exist
function addMarkdownButtons() {
  // Don't add buttons on homepage
  if (isHomePage()) {
    return;
  }

  // Check if buttons already exist
  const existingButtons = document.querySelector(".markdown-buttons");

  if (existingButtons) {
    return;
  }

  // Find the h1 in md-content
  const h1Title = document.querySelector(".md-content h1");

  if (!h1Title) {
    return;
  }

  // Create buttons HTML safely using DOM methods
  const buttonsDiv = document.createElement("div");
  buttonsDiv.className = "markdown-buttons";

  // Create Copy button
  const copyButton = document.createElement("button");
  copyButton.id = "md-copy";
  copyButton.textContent = "Copy for LLM";
  copyButton.addEventListener("click", copyMarkdownContent);

  // Create View button
  const viewButton = document.createElement("button");
  viewButton.id = "md-open";
  viewButton.textContent = "View as Markdown";
  viewButton.addEventListener("click", openMarkdownInNewTab);

  // Append buttons to container
  buttonsDiv.appendChild(copyButton);
  buttonsDiv.appendChild(viewButton);

  // Insert after h1
  h1Title.parentNode.insertBefore(buttonsDiv, h1Title.nextSibling);
}

document$.subscribe(function () {
  console.log("Page loaded/changed - checking for buttons");
  addMarkdownButtons();
});
