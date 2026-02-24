// biome-ignore lint/correctness/noUnusedVariables: called from HTML onclick
function copyCode(button) {
  // Find the code block next to this button
  const codeBlock = button.parentElement.querySelector(".code-block");

  // Get the text content without HTML tags
  const codeText = codeBlock.innerText || codeBlock.textContent;

  // Copy to clipboard
  navigator.clipboard
    .writeText(codeText)
    .then(() => {
      // Change button text and style to show success
      const originalText = button.textContent;
      button.textContent = "Copied!";
      button.classList.add("copied");

      // Reset button after 2 seconds
      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove("copied");
      }, 2000);
    })
    .catch(() => {
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

      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove("copied");
      }, 2000);
    });
}
