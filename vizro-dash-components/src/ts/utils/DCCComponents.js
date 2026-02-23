import React from "react";

const POLL_INTERVAL_MS = 50;
const TIMEOUT_MS = 10000;

const createDCCLazyComponent = (componentName) => {
  return React.lazy(() => {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const check = () => {
        const component = window.dash_core_components?.[componentName];
        if (component) {
          resolve({ default: component });
        } else if (Date.now() - startTime > TIMEOUT_MS) {
          reject(
            new Error(
              `dash-core-components "${componentName}" failed to load within ${TIMEOUT_MS / 1000}s.`,
            ),
          );
        } else {
          setTimeout(check, POLL_INTERVAL_MS);
        }
      };
      check();
    });
  });
};

export const DCCLink = createDCCLazyComponent("Link");
