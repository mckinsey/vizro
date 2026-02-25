import { mergeDeepRight, pick, type } from "ramda";
// biome-ignore lint/correctness/noUnusedImports: React must be in scope for classic JSX transform ("jsx": "react" in tsconfig)
import React, { Component, Suspense } from "react";
import JsxParser from "react-jsx-parser";
import Markdown from "react-markdown";
import RemarkMath from "remark-math";
import { propTypes } from "../components/Markdown";
import { DCCLink } from "../utils/DCCComponents";
import {
  DMCCodeHighlight,
  DMCInlineCodeHighlight,
} from "../utils/DMCComponents";
import LoadingElement from "../utils/LoadingElement";
import DashMath from "./Math.react";

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
      // Uses the real dcc.Link component loaded from window.dash_core_components
      // via React.lazy (same pattern as DMC components). This provides full
      // functionality including URL sanitization and refresh prop support.
      dccLink: (props) => (
        <Suspense fallback={<a href={props.href}>{props.children}</a>}>
          <DCCLink {...props} />
        </Suspense>
      ),
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

    // DEVIATION FROM ORIGINAL DCC:
    // Regex to convert $...$ and $$...$$ math notation to dashMathjax components.
    // Original pattern: /(\${1,2})((?:\\.|[^$])+)\1/g
    // Fixed pattern avoids catastrophic backtracking (ReDoS) by being explicit
    // about escaped dollar signs vs other escaped chars vs plain characters.
    const regexMath = (value) => {
      const newValue = value.replace(
        /(\${1,2})((?:\\\$|[^$\\]|\\(?!\$))+)\1/g,
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
    // We use DMC's CodeHighlight via window.dash_mantine_components globals
    // for built-in copy button and to avoid DOM manipulation anti-patterns.
    // These are loaded via React.lazy from DMCComponents.js.
    const codeRenderer = ({ language, value }) => {
      return (
        <Suspense
          fallback={
            <pre>
              <code>{value}</code>
            </pre>
          }
        >
          <DMCCodeHighlight
            code={value}
            language={language || "text"}
            withCopyButton={true}
          />
        </Suspense>
      );
    };

    // NOTE: MantineProvider is provided by the host Dash app via DMC.
    // We no longer need to wrap in our own MantineProvider since we consume
    // DMC components which already have the required context from the app.
    return (
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
            inlineMath: (props) => <DashMath tex={props.value} inline={true} />,

            // Code block rendering using Mantine CodeHighlight
            code: codeRenderer,

            // DEVIATION FROM ORIGINAL DCC:
            // Inline code rendering using DMC's InlineCodeHighlight via window global
            inlineCode: ({ value }) => (
              <Suspense fallback={<code>{value}</code>}>
                <DMCInlineCodeHighlight code={value} language="text" />
              </Suspense>
            ),

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
    );
  }
}

DashMarkdown.propTypes = propTypes;
