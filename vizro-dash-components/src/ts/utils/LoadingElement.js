import React from "react";

/**
 * The loading element is used to add `data-dash-is-loading` attribute
 * on html elements. This is used to customize CSS when a component is
 * loading.
 *
 * See: https://dash.plotly.com/loading-states#check-loading-states-from-components
 */
// eslint-disable-next-line react/prop-types
function LoadingElement({ elementType = "div", ...props }, ref) {
  // biome-ignore lint/correctness/useHookAtTopLevel: this is a forwardRef component, hooks are valid here
  const ctx = window.dash_component_api.useDashContext();
  // biome-ignore lint/correctness/useHookAtTopLevel: this is a forwardRef component, hooks are valid here
  const loading = ctx.useLoading();

  const givenProps = {
    ...props,
    ref,
  };
  if (loading) {
    givenProps["data-dash-is-loading"] = true;
  }

  return React.createElement(elementType, givenProps);
}

export default React.forwardRef(LoadingElement);
