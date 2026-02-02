/**
 * Ensure accordion containing active nav-link is opened.
 * Runs on page load and navigation to auto-open the accordion for the active page
 * while preserving manually opened accordions via Bootstrap's persistence.
 */
function openActiveAccordion() {
  const activeLinks = document.querySelectorAll('.nav-link.active');
  
  activeLinks.forEach((link) => {
    const accordionCollapse = link.closest('.accordion-collapse');
    
    if (accordionCollapse && !accordionCollapse.classList.contains('show')) {
      accordionCollapse.classList.add('show');
      
      // Update accordion button state
      const accordionItem = accordionCollapse.closest('.accordion-item');
      if (accordionItem) {
        const accordionButton = accordionItem.querySelector('.accordion-button');
        if (accordionButton) {
          accordionButton.setAttribute('aria-expanded', 'true');
          accordionButton.classList.remove('collapsed');
        }
      }
    }
  });
}

// Run on initial page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', openActiveAccordion);
} else {
  openActiveAccordion();
}

// Run when URL changes (for navigation within the app)
const originalPushState = history.pushState;
history.pushState = function() {
  originalPushState.apply(this, arguments);
  setTimeout(openActiveAccordion, 100);
};

window.addEventListener('popstate', () => {
  setTimeout(openActiveAccordion, 100);
});

// Catch when .active class is added to nav-links (fallback)
const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
      const target = mutation.target;
      if (target.classList.contains('nav-link') && target.classList.contains('active')) {
        openActiveAccordion();
        break;
      }
    }
  }
});

// Start observing once DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['class'],
      subtree: true
    });
  });
} else {
  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['class'],
    subtree: true
  });
}
