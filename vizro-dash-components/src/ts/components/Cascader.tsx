import PropTypes from "prop-types";
// biome-ignore lint/correctness/noUnusedImports: React must be in scope for classic JSX transform
import React, { Component } from "react";
import CascaderFragment, { type CascaderProps } from "../fragments/Cascader";

/**
 * A hierarchical cascading dropdown component inspired by AntdCascader
 * (https://fac.feffery.tech/AntdCascader), built to visually match dcc.Dropdown.
 * Users navigate and select leaf values from a recursive tree of options
 * via cascading side-by-side panels.
 * Supports single-select and multi-select.
 */
export default class Cascader extends Component<CascaderProps> {
  static propTypes: Record<string, unknown>;
  static defaultProps: Record<string, unknown>;

  render() {
    return <CascaderFragment {...this.props} />;
  }
}

Cascader.propTypes = {
  /**
   * Unique ID to identify this component in Dash callbacks.
   */
  id: PropTypes.string,
  /**
   * Dash-assigned callback that gets fired when the value changes.
   */
  setProps: PropTypes.func,
  /**
   * Tree-structured options. Accepts either the standard list-of-dicts format
   * or a nested dict/list shorthand:
   *   {"Asia": ["Japan", "China"], "Europe": {"Western": ["France"]}}
   * Each dict key becomes a parent node (label = value = key).
   * List items become leaves; scalars use the scalar as both label and value.
   * In the standard format each node has a `label` and `value`; nodes with a
   * `children` array are parents, nodes without are leaves.
   * Only leaf values are ever stored in `value`.
   */
  options: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.object),
    PropTypes.object,
  ]).isRequired,
  /**
   * Selected value(s).
   * When `multi=false`: a single leaf value (string or number) or null.
   * When `multi=true`: an array of leaf values.
   */
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
    PropTypes.arrayOf(
      PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ),
  ]),
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
  multi: false,
  searchable: true,
  clearable: true,
  placeholder: "Select...",
  disabled: false,
  maxHeight: 300,
  optionHeight: "auto",
  debounce: false,
  persisted_props: ["value"],
  persistence_type: "local",
};

export const propTypes = Cascader.propTypes;
export const defaultProps = Cascader.defaultProps;
