// DEVIATION FROM ORIGINAL DCC:
// In the original Dash, propTypes are defined in components/Markdown.react.js
// and imported by fragments/Markdown.react.js via:
//   import {propTypes} from '../components/Markdown.react';
//
// We can't do this because our component wrapper (Markdown.tsx) directly imports
// the fragment, which would create a circular dependency:
//   Markdown.tsx -> Markdown.react.js -> Markdown.tsx
//
// The original avoids this because it lazy-loads the fragment via asyncDecorator
// rather than importing it directly. We use a shared file instead so both the
// component and the fragment can import propTypes without a circular dependency.

import PropTypes from "prop-types";

export const propTypes = {
  /**
   * The ID of this component, used to identify dash components
   * in callbacks. The ID needs to be unique across all of the
   * components in an app.
   */
  id: PropTypes.string,
  /**
   * Class name of the container element
   */
  className: PropTypes.string,

  /**
   * If true, loads mathjax v3 (tex-svg) into the page and use it in the markdown
   */
  mathjax: PropTypes.bool,

  /**
   * A boolean to control raw HTML escaping.
   * Setting HTML from code is risky because it's easy to
   * inadvertently expose your users to a cross-site scripting (XSS)
   * (https://en.wikipedia.org/wiki/Cross-site_scripting) attack.
   */
  dangerously_allow_html: PropTypes.bool,

  /**
   * A string for the target attribute to use on links (such as "_blank")
   */
  link_target: PropTypes.string,

  /**
   * A markdown string (or array of strings) that adheres to the CommonMark spec
   */
  children: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]),

  /**
   * Remove matching leading whitespace from all lines.
   * Lines that are empty, or contain *only* whitespace, are ignored.
   * Both spaces and tab characters are removed, but only if they match;
   * we will not convert tabs to spaces or vice versa.
   */
  dedent: PropTypes.bool,

  /**
   * Config options for syntax highlighting.
   */
  highlight_config: PropTypes.exact({
    /**
     * Color scheme; default 'light'
     */
    theme: PropTypes.oneOf(["dark", "light"]),
  }),

  /**
   * User-defined inline styles for the rendered Markdown
   */
  style: PropTypes.object,
};

export const defaultProps = {
  mathjax: false,
  dangerously_allow_html: false,
  highlight_config: {},
  dedent: true,
};
