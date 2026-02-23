import React from "react";

const createDCCLazyComponent = (componentName) => {
  return React.lazy(() => {
    return new Promise((resolve) => {
      const check = () => {
        const component = window.dash_core_components?.[componentName];
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

export const DCCLink = createDCCLazyComponent("Link");
