import { CodeHighlight } from "@mantine/code-highlight";
import { MantineProvider } from "@mantine/core";
import { isNil, mergeDeepRight, pick, type } from "ramda";
import { Component } from "react";
import JsxParser from "react-jsx-parser";
import Markdown from "react-markdown";
import RemarkMath from "remark-math";
import LoadingElement from "../utils/LoadingElement";
import DashMath from "./Math.react";
import { propTypes } from "./markdownPropTypes";

// Import Mantine styles
import "@mantine/core/styles.css";
import "@mantine/code-highlight/styles.css";

export default class DashMarkdown extends Component {
  constructor(props) {
    super(props);
    this.dedent = this.dedent.bind(this);
  }

  dedent(text) {
    const lines = text.split(/\r\n|\r|\n/);
    let commonPrefix = null;
    for (const line of lines) {
      const preMatch = line?.match(/^\s*(?=\S)/);
      if (preMatch) {
        const prefix = preMatch[0];
        if (commonPrefix !== null) {
          for (let i = 0; i < commonPrefix.length; i++) {
            // Like Python's textwrap.dedent, we'll remove both
            // space and tab characters, but only if they match
            if (prefix[i] !== commonPrefix[i]) {
              commonPrefix = commonPrefix.substr(0, i);
              break;
            }
          }
        } else {
          commonPrefix = prefix;
        }

        if (!commonPrefix) {
          break;
        }
      }
    }

    const commonLen = commonPrefix ? commonPrefix.length : 0;
    return lines
      .map((line) => {
        return line.match(/\S/) ? line.substr(commonLen) : "";
      })
      .join("\n");
  }

  render() {
    const {
      id,
      style,
      className,
      highlight_config,
      dangerously_allow_html,
      link_target,
      mathjax,
      children,
      dedent,
    } = this.props;

    const textProp =
      type(children) === "Array" ? children.join("\n") : children;
    const displayText = dedent && textProp ? this.dedent(textProp) : textProp;

    const componentTransforms = {
      // DEVIATION FROM ORIGINAL DCC:
      // Client-side navigation logic from the original Dash Link component:
      // https://github.com/plotly/dash/blob/dev/components/dash-core-components/src/components/Link.react.js
      //
      // In the original, this uses `import DccLink from '../components/Link.react'`
      // which is a full Dash component with propTypes, loading state, and URL
      // sanitization via `window.dash_clientside.clean_url`.
      //
      // We inline the core pushState routing logic here instead of importing
      // DccLink because Link.react is a separate Dash component that doesn't
      // exist in our package, and creating it as a file in src/ts/components/
      // would cause dash-generate-components to produce an unwanted Python
      // `vizro_dash_components.Link` class.
      dccLink: (props) => {
        const handleClick = (e) => {
          const hasModifiers = e.metaKey || e.shiftKey || e.altKey || e.ctrlKey;
          if (hasModifiers) {
            return;
          }
          if (props.target !== "_self" && !isNil(props.target)) {
            return;
          }
          e.preventDefault();
          window.history.pushState({}, "", props.href);
          window.dispatchEvent(new CustomEvent("_dashprivate_pushstate"));
          window.scrollTo(0, 0);
        };
        return (
          <a href={props.href} onClick={handleClick} {...props}>
            {isNil(props.children) ? props.href : props.children}
          </a>
        );
      },
      dccMarkdown: (props) => (
        <Markdown
          {...mergeDeepRight(
            pick(["dangerously_allow_html", "dedent"], this.props),
            pick(["children"], props),
          )}
        />
      ),
      dashMathjax: (props) => (
        <DashMath tex={props.value} inline={props.inline} />
      ),
    };

    // Regex to convert $...$ and $$...$$ math notation to dashMathjax components
    const regexMath = (value) => {
      const newValue = value.replace(
        /(\${1,2})((?:\\.|[^$])+)\1/g,
        (_m, tag, src) => {
          const inline = tag.length === 1 || src.indexOf("\n") === -1;
          return `<dashMathjax value='${src}' inline='${inline}'/>`;
        },
      );
      return newValue;
    };

    // DEVIATION FROM ORIGINAL DCC:
    // The original uses highlight.js via manual DOM manipulation in
    // componentDidMount/componentDidUpdate (MarkdownHighlighter).
    // We use Mantine CodeHighlight as a React component via renderers.code
    // for built-in copy button and to avoid DOM manipulation anti-patterns.
    const codeRenderer = ({ language, value }) => {
      return (
        <CodeHighlight
          code={value}
          language={language || "text"}
          withCopyButton={true}
        />
      );
    };

    // DEVIATION FROM ORIGINAL DCC:
    // MantineProvider is required for Mantine CodeHighlight to function.
    // The original has no wrapper here.
    return (
      <MantineProvider>
        <LoadingElement
          id={id}
          ref={(node) => {
            this.mdContainer = node;
          }}
          style={style}
          className={
            (highlight_config?.theme || className) &&
            `${className ? className : ""} ${
              highlight_config?.theme === "dark" ? "hljs-dark" : ""
            }`
          }
        >
          <Markdown
            source={displayText}
            escapeHtml={!dangerously_allow_html}
            linkTarget={link_target}
            plugins={mathjax ? [RemarkMath] : []}
            renderers={{
              // Math block rendering (when mathjax is enabled)
              math: (props) => <DashMath tex={props.value} inline={false} />,

              // Inline math rendering (when mathjax is enabled)
              inlineMath: (props) => (
                <DashMath tex={props.value} inline={true} />
              ),

              // Code block rendering using Mantine CodeHighlight
              // This is the ONLY deviation from original Dash
              code: codeRenderer,

              // HTML rendering with JSX parsing support
              // This enables dccLink, dccMarkdown, and dashMathjax in HTML blocks
              html: (props) =>
                props.escapeHtml ? (
                  props.value
                ) : (
                  <JsxParser
                    jsx={mathjax ? regexMath(props.value) : props.value}
                    components={componentTransforms}
                    renderInWrapper={false}
                  />
                ),
            }}
          />
        </LoadingElement>
      </MantineProvider>
    );
  }
}

DashMarkdown.propTypes = propTypes;
