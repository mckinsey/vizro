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
