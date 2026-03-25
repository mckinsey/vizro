import PropTypes from "prop-types";
// biome-ignore lint/correctness/noUnusedImports: React must be in scope for classic JSX transform
import React, { Component } from "react";
import CascadeFragment, { CascadeProps } from "../fragments/Cascade";

/**
 * A hierarchical cascading dropdown component.
 * Users navigate and select leaf values from a recursive tree of options
 * via cascading side-by-side panels.
 *
 * Visually identical to dcc.Dropdown; supports single-select and multi-select.
 */
export default class Cascade extends Component<CascadeProps> {
  static propTypes: Record<string, unknown>;
  static defaultProps: Record<string, unknown>;

  render() {
    return <CascadeFragment {...this.props} />;
  }
}

Cascade.propTypes = {
  /**
   * Unique ID to identify this component in Dash callbacks.
   */
  id: PropTypes.string,
  /**
   * Dash-assigned callback that gets fired when the value changes.
   */
  setProps: PropTypes.func.isRequired,
  /**
   * Tree-structured options. Each node has a `label` and `value`.
   * Nodes with a `children` array are parents; nodes without are leaves.
   * Only leaf values are ever stored in `value`.
   */
  options: PropTypes.arrayOf(PropTypes.object).isRequired,
  /**
   * Selected value(s).
   * When `multi=false`: a single leaf value (string or number) or null.
   * When `multi=true`: an array of leaf values.
   */
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
    PropTypes.arrayOf(
      PropTypes.oneOfType([PropTypes.string, PropTypes.number])
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
   * Inline styles applied to the outer wrapper div.
   */
  style: PropTypes.object,
};

Cascade.defaultProps = {
  options: [],
  value: null,
  multi: false,
  searchable: true,
  clearable: true,
  placeholder: "Select...",
  disabled: false,
  maxHeight: 300,
};

export const propTypes = Cascade.propTypes;
export const defaultProps = Cascade.defaultProps;
