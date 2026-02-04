// DEVIATION FROM ORIGINAL DCC:
// The original splits this across two files:
//   - utils/mathjax.js: imports 'mathjax/es5/tex-svg' and configures it
//   - utils/LazyLoader/mathjax.js: uses dynamic import() to lazy-load the above
//     into a separate webpack chunk
//
// Webpack dynamic imports create separate chunk files (e.g. 682.vizro_dash_components.js)
// that Dash's _dash-component-suites handler cannot serve for custom components
// (returns 500 — chunk filenames lack the version fingerprint Dash expects).
// We merge both files and import MathJax synchronously so it is bundled into
// the main JS file.
// Moved out of LazyLoader/ since it no longer lazy-loads.

import "mathjax/es5/tex-svg";

window.MathJax.config.startup.typeset = false;

export default () => Promise.resolve(window.MathJax);
