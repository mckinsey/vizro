document.addEventListener("DOMContentLoaded", function () {
  const isHomepage = document.title.trim() === "Vizro";

  if (isHomepage) {
    const sidebar = document.querySelector(".md-sidebar--primary");
    if (sidebar) {
      sidebar.style.display = "none";
    }
  }
});
