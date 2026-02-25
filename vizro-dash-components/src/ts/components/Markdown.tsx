import { asyncDecorator } from "@plotly/dash-component-plugins";
import PropTypes from "prop-types";
// biome-ignore lint/correctness/noUnusedImports: React must be in scope for classic JSX transform ("jsx": "react" in tsconfig)
import React, { Component, Suspense } from "react";
import markdown from "../utils/LazyLoader/markdown";
import lazyLoadMathJax from "../utils/LazyLoader/mathjax";

/**
 * A component that renders Markdown text as specified by the
 * GitHub Markdown spec. These component uses
 * [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.
 */
export default class DashMarkdown extends Component<DashMarkdownProps> {
  static _loadMathjax: boolean;
  static propTypes: Record<string, unknown>;
  static defaultProps: Record<string, unknown>;

  constructor(props: DashMarkdownProps) {
    super(props);

    if (props.mathjax) {
      DashMarkdown._loadMathjax = true;
    }
  }

  render() {
    return (
      <Suspense fallback={null}>
        <RealDashMarkdown {...this.props} />
      </Suspense>
    );
  }
}

interface DashMarkdownProps {
  /**
   * The ID of this component, used to identify dash components
   * in callbacks. The ID needs to be unique across all of the
   * components in an app.
   */
  id?: string;
  /**
   * Dash-assigned callback that gets fired when the value changes.
   */
  setProps?: (props: Record<string, unknown>) => void;
  /**
   * Class name of the container element
   */
  className?: string;
  /**
   * If true, loads mathjax v3 (tex-svg) into the page and use it in the markdown
   */
  mathjax?: boolean;
  /**
   * A boolean to control raw HTML escaping.
   * Setting HTML from code is risky because it's easy to
   * inadvertently expose your users to a cross-site scripting (XSS)
   * (https://en.wikipedia.org/wiki/Cross-site_scripting) attack.
   */
  dangerously_allow_html?: boolean;
  /**
   * A string for the target attribute to use on links (such as "_blank")
   */
  link_target?: string;
  /**
   * A markdown string (or array of strings) that adheres to the CommonMark spec
   */
  children?: string | string[];
  /**
   * Remove matching leading whitespace from all lines.
   * Lines that are empty, or contain *only* whitespace, are ignored.
   * Both spaces and tab characters are removed, but only if they match;
   * we will not convert tabs to spaces or vice versa.
   */
  dedent?: boolean;
  /**
   * Config options for syntax highlighting.
   */
  highlight_config?: {
    /**
     * Color scheme; default 'light'
     */
    theme?: "dark" | "light";
  };
  /**
   * User-defined inline styles for the rendered Markdown
   */
  style?: object;
}

DashMarkdown.propTypes = {
  /**
   * The ID of this component, used to identify dash components
   * in callbacks. The ID needs to be unique across all of the
   * components in an app.
   */
  id: PropTypes.string,
  /**
   * Dash-assigned callback that gets fired when the value changes.
   */
  setProps: PropTypes.func,
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

DashMarkdown.defaultProps = {
  mathjax: false,
  dangerously_allow_html: false,
  highlight_config: {},
  dedent: true,
};

const RealDashMarkdown = asyncDecorator(DashMarkdown, () =>
  Promise.all([
    markdown(),
    DashMarkdown._loadMathjax ? lazyLoadMathJax() : undefined,
  ]).then(([md]) => md),
);

export const propTypes = DashMarkdown.propTypes;
export const defaultProps = DashMarkdown.defaultProps;
