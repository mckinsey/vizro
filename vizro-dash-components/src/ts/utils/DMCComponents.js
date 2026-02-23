import React from "react";

const createDMCLazyComponent = (componentName) => {
  return React.lazy(() => {
    return new Promise((resolve) => {
      const check = () => {
        const component = window.dash_mantine_components?.[componentName];
        if (component) {
          resolve({ default: component });
        } else {
          setTimeout(check, 10);
        }
      };
      check();
    });
  });
};

export const DMCCodeHighlight = createDMCLazyComponent("CodeHighlight");
export const DMCInlineCodeHighlight =
  createDMCLazyComponent("InlineCodeHighlight");
