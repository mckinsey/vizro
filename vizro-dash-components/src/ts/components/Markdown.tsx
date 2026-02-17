// biome-ignore lint/style/useImportType: React must be a value import for JSX with classic transform ("jsx": "react")
import React from "react";
import DashMarkdown from "../fragments/Markdown.react";
import { defaultProps, propTypes } from "../fragments/markdownPropTypes";
import type { DashComponentProps } from "../props";

type Props = {
  /**
   * A markdown string (or array of strings) that will be rendered to HTML.
   */
  children?: string | string[];

  /**
   * Class name of the container element.
   */
  className?: string;

  /**
   * A style object for the container element.
   */
  style?: React.CSSProperties;

  /**
   * A boolean to control raw HTML escaping.
   * Setting HTML from code is risky because it's easy to
   * inadvertently expose your users to a cross-site scripting (XSS)
   * attack.
   */
  dangerously_allow_html?: boolean;

  /**
   * A string for the target attribute to use on links.
   */
  link_target?: string;

  /**
   * A boolean to enable LaTeX math rendering.
   * Requires MathJax to be loaded.
   */
  mathjax?: boolean;

  /**
   * Remove matching leading whitespace from all lines.
   * Lines that are empty, or contain only whitespace, are not considered
   * for determining the common prefix.
   */
  dedent?: boolean;

  /**
   * Config options for syntax highlighting.
   */
  highlight_config?: {
    /**
     * Color theme for syntax highlighting.
     * Set to 'dark' for dark mode styling.
     */
    theme?: string;
  };
} & DashComponentProps;

/**
 * A component that renders Markdown text as specified by the
 * GitHub Markdown spec. These component uses
 * [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.
 */
const Markdown = (props: Props) => {
  const {
    id,
    children,
    className,
    style,
    dangerously_allow_html = false,
    link_target,
    mathjax = false,
    dedent = true,
    highlight_config,
  } = props;

  return (
    <DashMarkdown
      id={id}
      className={className}
      style={style}
      dangerously_allow_html={dangerously_allow_html}
      link_target={link_target}
      mathjax={mathjax}
      dedent={dedent}
      highlight_config={highlight_config}
    >
      {children}
    </DashMarkdown>
  );
};

Markdown.defaultProps = defaultProps;
Markdown.propTypes = propTypes;

export default Markdown;
