// Check if current page is homepage
function isHomePage() {
  const currentPath = window.location.pathname;

  // If URL contains 'pages', it's definitely not homepage
  if (!currentPath.includes("/pages/")) return true;
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

  // Find the copy button and store original HTML
  const copyButton = document.querySelector(".markdown-buttons #md-copy");
  const originalHTML = copyButton
    ? copyButton.innerHTML
    : '<span class="material-symbols-outlined">chat_paste_go</span> Copy for LLM';

  try {
    // Update button text to show loading state
    if (copyButton) {
      copyButton.innerHTML =
        '<span class="material-symbols-outlined loading">progress_activity</span> Copying...';
      copyButton.disabled = true;
    }

    // Track timing to ensure minimum 500ms for copying state
    const startTime = Date.now();

    // Fetch the markdown file
    const response = await fetch(markdownUrl);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const markdown = await response.text();

    // Copy to clipboard
    navigator.clipboard.writeText(markdown);

    // Calculate remaining time to ensure minimum 300ms
    const elapsedTime = Date.now() - startTime;
    const remainingTime = Math.max(0, 300 - elapsedTime);

    // Show "Copied!" after minimum time has passed
    setTimeout(() => {
      if (copyButton) {
        copyButton.innerHTML =
          '<span class="material-symbols-outlined">check_circle</span> Copied!';

        setTimeout(() => {
          copyButton.innerHTML = originalHTML;
          copyButton.disabled = false;
        }, 1500);
      }

      // Reset to original state after 1.5 seconds total
    }, remainingTime);
  } catch (fetchError) {
    console.error("Error fetching markdown:", fetchError);

    // Reset button on error
    if (copyButton) {
      copyButton.innerHTML =
        '<span class="material-symbols-outlined">error</span> Error';
      setTimeout(() => {
        copyButton.innerHTML = originalHTML;
        copyButton.disabled = false;
      }, 1500);
    }
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

  // Button configuration
  const buttonConfigs = [
    {
      id: "md-copy",
      icon: "chat_paste_go",
      text: " Copy for LLM",
      handler: copyMarkdownContent,
    },
    {
      id: "md-open",
      icon: "markdown_copy",
      text: " View as Markdown",
      handler: openMarkdownInNewTab,
    },
  ];

  // Create buttons from configuration
  buttonConfigs.forEach((config) => {
    const button = document.createElement("button");
    button.id = config.id;

    // Add icon span
    const icon = document.createElement("span");
    icon.className = "material-symbols-outlined";
    icon.textContent = config.icon;

    button.appendChild(icon);
    button.appendChild(document.createTextNode(config.text));
    button.addEventListener("click", config.handler);

    buttonsDiv.appendChild(button);
  });

  // Insert after h1
  h1Title.parentNode.insertBefore(buttonsDiv, h1Title.nextSibling);
}

document$.subscribe(function () {
  console.log("Page loaded/changed - checking for buttons");
  addMarkdownButtons();
});
