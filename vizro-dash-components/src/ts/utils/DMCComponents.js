import React from "react";

const POLL_INTERVAL_MS = 50;
const TIMEOUT_MS = 10000;

const createDMCLazyComponent = (componentName) => {
  return React.lazy(() => {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const check = () => {
        const component = window.dash_mantine_components?.[componentName];
        if (component) {
          resolve({ default: component });
        } else if (Date.now() - startTime > TIMEOUT_MS) {
          reject(
            new Error(
              `dash-mantine-components "${componentName}" failed to load within ${TIMEOUT_MS / 1000}s. ` +
                "Ensure MantineProvider wraps your app.",
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

export const DMCCodeHighlight = createDMCLazyComponent("CodeHighlight");
export const DMCInlineCodeHighlight = createDMCLazyComponent(
  "InlineCodeHighlight",
);
