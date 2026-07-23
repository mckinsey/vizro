import PropTypes from "prop-types";
// biome-ignore lint/style/useImportType: "jsx": "react" requires React in scope at runtime
import React, { Component } from "react";
import CascaderFragment, { type CascaderProps } from "../fragments/Cascader";
import type { CascaderOptionsRaw } from "../fragments/cascaderUtils";

interface CascaderComponentProps {
  /**
   * Unique ID to identify this component in Dash callbacks.
   */
  id?: string;
  /**
   * Tree-structured options. Accepts either the standard list-of-dicts format
   * or a nested dict/list shorthand:
   *   {"Asia": ["Japan", "China"], "Europe": {"Western": ["France"]}}
   * Each dict key becomes a parent node (label = value = key).
   * List items become leaves; scalars use the scalar as both label and value.
   * In the standard format each node has a `label` and `value`; nodes with a
   * `children` array are parents, nodes without are leaves.
   * Selections are addressed by full root-to-leaf path (see `value`).
   * Optional; defaults to an empty tree (renders as an empty dropdown).
   */
  options?: CascaderOptionsRaw;
  /**
   * Selected value(s). The shape depends on `full_path`:
   * - `full_path=false` (default, LEAF MODE): a bare leaf scalar when `multi=false`
   *   (e.g. "france", or null), or a list of leaf scalars when `multi=true`
   *   (e.g. ["france", "japan"]). Leaf values must be unique across the tree.
   * - `full_path=true` (PATH MODE): a full root-to-leaf path when `multi=false`
   *   (e.g. ["europe", "france"], or null), or a list of such paths when
   *   `multi=true` (e.g. [["europe", "france"], ["asia", "japan"]]). Paths address
   *   duplicate leaf labels across different branches unambiguously.
   */
  value?:
    | string
    | number
    | boolean
    | (string | number | boolean)[]
    | (string | number | boolean)[][]
    | null;
  /**
   * Selection value mode.
   * - `false` (default, LEAF MODE): `value` is a bare leaf scalar (or list of them
   *   when `multi=true`). Leaf values must be unique across the tree; duplicates
   *   are ambiguous and logged as an error.
   * - `true` (PATH MODE): `value` is a full root-to-leaf path (or list of paths).
   *   Duplicate leaf labels across branches are supported.
   */
  full_path?: boolean;
  /**
   * Enable multi-select. When true, `value` is an array and checkboxes
   * are shown alongside options.
   */
  multi?: boolean;
  /**
   * Show a search input at the top of the panel.
   */
  searchable?: boolean;
  /**
   * Show a clear button to reset the selection.
   */
  clearable?: boolean;
  /**
   * Placeholder text shown in the trigger when nothing is selected.
   */
  placeholder?: string;
  /**
   * Disable the component entirely.
   */
  disabled?: boolean;
  /**
   * Maximum height of the panel in pixels.
   */
  maxHeight?: number;
  /**
   * Additional CSS class applied to the outer wrapper div.
   */
  className?: string;
  /**
   * Inline CSS style applied to the outer wrapper div.
   */
  style?: React.CSSProperties;
  /**
   * Height in pixels for each option row. When omitted, rows size naturally.
   */
  optionHeight?: "auto" | number;
  /**
   * If true, the component will not fire its callback until the panel is
   * closed (by clicking outside, pressing Escape, or clicking the trigger).
   * This reduces the number of callbacks fired during multi-select interactions.
   */
  debounce?: boolean;
  /**
   * If false, the menu will not close when a value is selected.
   * Defaults to `!multi`.
   */
  closeOnSelect?: boolean;
  /**
   * The value typed in the search input for filtering options.
   */
  search_value?: string;
  /**
   * Text for customizing the labels rendered by this component.
   */
  labels?: {
    select_all?: string;
    deselect_all?: string;
    selected_count?: string;
    search?: string;
    clear_search?: string;
    clear_selection?: string;
    no_options_found?: string;
  };
  /**
   * Used to allow user interactions in this component to be persisted when
   * the component - or the page - is refreshed. If `persistence` is truthy and
   * hasn't changed from its previous value, a `value` that the user has
   * changed while using the app will keep that change, as long as the new
   * `value` also matches what was given originally.
   * Used in conjunction with `persistence_type`.
   */
  persistence?: boolean | string | number;
  /**
   * Properties whose user interactions will persist after refreshing the
   * component or the page. Since only `value` is allowed this prop can
   * normally be ignored.
   */
  persisted_props?: string[];
  /**
   * Where persisted user changes will be stored:
   * memory: only kept in memory, reset on page refresh.
   * local: window.localStorage, data is kept after the browser quit.
   * session: window.sessionStorage, data is cleared once the browser quit.
   */
  persistence_type?: "local" | "session" | "memory";
}

/**
 * A hierarchical cascading dropdown component inspired by AntdCascader
 * (https://fac.feffery.tech/AntdCascader), built to visually match dcc.Dropdown.
 * Users navigate and select leaf values from a recursive tree of options
 * via cascading side-by-side panels.
 * Supports single-select and multi-select.
 */
export default class Cascader extends Component<CascaderComponentProps> {
  static propTypes: Record<string, unknown>;
  static defaultProps: Record<string, unknown>;

  render() {
    return <CascaderFragment {...(this.props as CascaderProps)} />;
  }
}

Cascader.propTypes = {
  /**
   * Unique ID to identify this component in Dash callbacks.
   */
  id: PropTypes.string,
  /**
   * Tree-structured options. Accepts either the standard list-of-dicts format
   * or a nested dict/list shorthand:
   *   {"Asia": ["Japan", "China"], "Europe": {"Western": ["France"]}}
   * Each dict key becomes a parent node (label = value = key).
   * List items become leaves; scalars use the scalar as both label and value.
   * In the standard format each node has a `label` and `value`; nodes with a
   * `children` array are parents, nodes without are leaves.
   * Selections are addressed by full root-to-leaf path (see `value`).
   */
  options: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.object),
    PropTypes.object,
  ]),
  /**
   * Selected value(s). The shape depends on `full_path`:
   * - `full_path=false` (default, LEAF MODE): a bare leaf scalar (or null) when
   *   `multi=false`, e.g. "france"; a list of leaf scalars when `multi=true`,
   *   e.g. ["france", "japan"]. Leaf values must be unique across the tree.
   * - `full_path=true` (PATH MODE): a full root-to-leaf path (or null) when
   *   `multi=false`, e.g. ["europe", "france"]; a list of paths when `multi=true`,
   *   e.g. [["europe", "france"], ["asia", "japan"]]. Paths address duplicate leaf
   *   labels across different branches unambiguously.
   */
  value: PropTypes.oneOfType([
    // A bare leaf scalar (leaf mode, multi=false), e.g. "france".
    PropTypes.string,
    PropTypes.number,
    PropTypes.bool,
    // A list of leaf scalars (leaf mode, multi=true) OR a single path (path mode,
    // multi=false): an array of scalars, e.g. ["france", "japan"] or ["europe", "france"].
    PropTypes.arrayOf(
      PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.bool]),
    ),
    // A list of paths (path mode, multi=true), e.g. [["europe", "france"], ["asia", "japan"]].
    PropTypes.arrayOf(
      PropTypes.arrayOf(
        PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
          PropTypes.bool,
        ]),
      ),
    ),
  ]),
  /**
   * Selection value mode.
   * - `false` (default, LEAF MODE): `value` is a bare leaf scalar (or list of them
   *   when `multi=true`). Leaf values must be unique across the tree; duplicates
   *   are ambiguous and logged as an error.
   * - `true` (PATH MODE): `value` is a full root-to-leaf path (or list of paths).
   *   Duplicate leaf labels across branches are supported.
   */
  full_path: PropTypes.bool,
  /**
   * Enable multi-select. When true, `value` is an array and checkboxes
   * are shown alongside options.
   */
  multi: PropTypes.bool,
  /**
   * Show a search input at the top of the panel.
   */
  searchable: PropTypes.bool,
  /**
   * Show a clear button to reset the selection.
   */
  clearable: PropTypes.bool,
  /**
   * Placeholder text shown in the trigger when nothing is selected.
   */
  placeholder: PropTypes.string,
  /**
   * Disable the component entirely.
   */
  disabled: PropTypes.bool,
  /**
   * Maximum height of the panel in pixels.
   */
  maxHeight: PropTypes.number,
  /**
   * Additional CSS class applied to the outer wrapper div.
   */
  className: PropTypes.string,
  /**
   * Inline CSS style applied to the outer wrapper div.
   */
  style: PropTypes.object,
  /**
   * Height in pixels for each option row. When omitted, rows size naturally.
   */
  optionHeight: PropTypes.number,
  /**
   * If true, the component will not fire its callback until the panel is
   * closed (by clicking outside, pressing Escape, or clicking the trigger).
   * This reduces the number of callbacks fired during multi-select interactions.
   */
  debounce: PropTypes.bool,
  /**
   * If false, the menu will not close when a value is selected.
   * Defaults to `!multi`.
   */
  closeOnSelect: PropTypes.bool,
  /**
   * The value typed in the search input for filtering options.
   */
  search_value: PropTypes.string,
  /**
   * Text for customizing the labels rendered by this component.
   */
  labels: PropTypes.exact({
    select_all: PropTypes.string,
    deselect_all: PropTypes.string,
    selected_count: PropTypes.string,
    search: PropTypes.string,
    clear_search: PropTypes.string,
    clear_selection: PropTypes.string,
    no_options_found: PropTypes.string,
  }),
  /**
   * Used to allow user interactions in this component to be persisted when
   * the component — or the page — is refreshed. If `persistence` is truthy and
   * hasn't changed from its previous value, a `value` that the user has
   * changed while using the app will keep that change, as long as the new
   * `value` also matches what was given originally.
   * Used in conjunction with `persistence_type`.
   */
  persistence: PropTypes.oneOfType([
    PropTypes.bool,
    PropTypes.string,
    PropTypes.number,
  ]),
  /**
   * Properties whose user interactions will persist after refreshing the
   * component or the page. Since only `value` is allowed this prop can
   * normally be ignored.
   */
  persisted_props: PropTypes.arrayOf(PropTypes.string),
  /**
   * Where persisted user changes will be stored:
   * - `"local"`: `window.localStorage`
   * - `"session"`: `window.sessionStorage`
   * - `"memory"`: in-memory, cleared on page refresh
   */
  persistence_type: PropTypes.oneOf(["local", "session", "memory"]),
};

Cascader.defaultProps = {
  options: [],
  value: null,
  full_path: false,
  multi: false,
  searchable: true,
  clearable: true,
  placeholder: "",
  disabled: false,
  maxHeight: 200,
  optionHeight: "auto",
  debounce: false,
  persisted_props: ["value"],
  persistence_type: "local",
};

export const propTypes = Cascader.propTypes;
export const defaultProps = Cascader.defaultProps;
