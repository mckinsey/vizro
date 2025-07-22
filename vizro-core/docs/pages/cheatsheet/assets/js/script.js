function copyCode(button) {
  // Find the code block next to this button
  const codeBlock = button.parentElement.querySelector(".code-block");

  // Get the text content without HTML tags
  const codeText = codeBlock.innerText || codeBlock.textContent;

  // Copy to clipboard
  navigator.clipboard
    .writeText(codeText)
    .then(function () {
      // Change button text and style to show success
      const originalText = button.textContent;
      button.textContent = "Copied!";
      button.classList.add("copied");

      // Reset button after 2 seconds
      setTimeout(function () {
        button.textContent = originalText;
        button.classList.remove("copied");
      }, 2000);
    })
    .catch(function (err) {
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = codeText;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);

      // Show success feedback
      const originalText = button.textContent;
      button.textContent = "Copied!";
      button.classList.add("copied");

      setTimeout(function () {
        button.textContent = originalText;
        button.classList.remove("copied");
      }, 2000);
    });
}

// Add double-click to copy functionality for inline code
document.addEventListener("DOMContentLoaded", function () {
  const inlineCodes = document.querySelectorAll(".code-inline");
  inlineCodes.forEach(function (code) {
    code.addEventListener("dblclick", function () {
      const text = this.textContent;
      navigator.clipboard
        .writeText(text)
        .then(function () {
          // Visual feedback for inline code
          code.style.backgroundColor = "#e8f5e8";
          setTimeout(function () {
            code.style.backgroundColor = "";
          }, 1000);
        })
        .catch(function () {
          // Fallback
          const textArea = document.createElement("textarea");
          textArea.value = text;
          document.body.appendChild(textArea);
          textArea.select();
          document.execCommand("copy");
          document.body.removeChild(textArea);

          // Visual feedback
          code.style.backgroundColor = "#e8f5e8";
          setTimeout(function () {
            code.style.backgroundColor = "";
          }, 1000);
        });
    });
  });
});
