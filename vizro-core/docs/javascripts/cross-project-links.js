/* Rewrite the project-switcher dropdown's cross-docset links so they preserve
   the language, version segment, and host of the page the user is currently
   on, instead of bouncing them to each subproject's RTD default version.

   Examples:
     User on  https://vizro.readthedocs.io/en/latest/foo
     ->       https://vizro.readthedocs.io/projects/vizro-ai/en/latest/

     User on  https://vizro--1754.org.readthedocs.build/en/1754/foo (PR build)
     ->       https://vizro--1754.org.readthedocs.build/projects/vizro-ai/en/1754/

   On localhost only one docset is served, so the rewrite is skipped and the
   hardcoded production URLs in zensical.toml stand. The current-docset link
   inside the dropdown is unaffected because it's rendered as a same-host URL
   that doesn't match the production prefix below.

   This file is duplicated byte-for-byte across the four docsets and is loaded
   via `extra_javascript` in each zensical.toml. Keep them in sync alongside
   docs/overrides/partials/tabs-item.html and docs/stylesheets/extra.css. */

(function () {
  if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    return;
  }

  // Match the language and version segment of the current path, allowing for
  // an optional /projects/<sub>/ prefix when we're on a subproject docset.
  const match = location.pathname.match(
    /^(?:\/projects\/[^/]+)?\/([a-z]{2}(?:-[A-Z]{2})?)\/([^/]+)\//,
  );
  if (!match) return;

  const lang = match[1];
  const version = match[2];
  const origin = location.origin;

  // Order matters: subproject prefixes must come before the bare site root,
  // otherwise every subproject href would match the root prefix first.
  const rewrites = [
    [
      "https://vizro.readthedocs.io/projects/vizro-ai/",
      `${origin}/projects/vizro-ai/${lang}/${version}/`,
    ],
    [
      "https://vizro.readthedocs.io/projects/vizro-mcp/",
      `${origin}/projects/vizro-mcp/${lang}/${version}/`,
    ],
    [
      "https://vizro.readthedocs.io/projects/vizro-experimental/",
      `${origin}/projects/vizro-experimental/${lang}/${version}/`,
    ],
    [
      "https://vizro.readthedocs.io/",
      `${origin}/${lang}/${version}/`,
    ],
  ];

  document.querySelectorAll(".md-tabs__dropdown-link").forEach((link) => {
    const href = link.getAttribute("href");
    if (!href) return;
    for (const [from, to] of rewrites) {
      if (href.startsWith(from)) {
        link.setAttribute("href", to + href.slice(from.length));
        return;
      }
    }
  });
})();
