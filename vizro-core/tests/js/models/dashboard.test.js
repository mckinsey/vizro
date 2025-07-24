/**
 * @jest-environment jsdom
 */

// Mock console.debug
console.debug = jest.fn();

const dimensions = {
  innerWidth: 1024,
  innerHeight: 768,
};

// Mock dash_clientside first
global.dash_clientside = {
  no_update: "no_update",
  PreventUpdate: "PreventUpdate",
};

// Mock document for DOM manipulation tests
global.document = {
  documentElement: {
    setAttribute: jest.fn(),
  },
};

// Mock window object with dimensions
global.window = {
  dash_clientside: global.dash_clientside,
  ...dimensions,
};

require("../../../src/vizro/static/js/models/dashboard.js");

describe("dashboard.js functions", () => {
  let setAttributeSpy;

  beforeEach(() => {
    jest.clearAllMocks();

    // Reset window dimensions to default desktop size
    global.window = { ...global.window, ...dimensions };

    // Spy on document.documentElement.setAttribute
    setAttributeSpy = jest.spyOn(
      global.document.documentElement,
      "setAttribute",
    );
  });

  afterEach(() => {
    // Restore spy after each test
    if (setAttributeSpy) {
      setAttributeSpy.mockRestore();
    }
  });

  describe("update_dashboard_theme", () => {
    test("should set light theme when theme_selector_checked is true", () => {
      const result =
        global.dash_clientside.dashboard.update_dashboard_theme(true);

      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-bs-theme",
        "light",
      );
      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-mantine-color-scheme",
        "light",
      );
      expect(result).toBe(global.dash_clientside.no_update);
    });

    test("should set dark theme when theme_selector_checked is false", () => {
      const result =
        global.dash_clientside.dashboard.update_dashboard_theme(false);

      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-bs-theme",
        "dark",
      );
      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-mantine-color-scheme",
        "dark",
      );
      expect(result).toBe(global.dash_clientside.no_update);
    });

    test("should handle null theme_selector_checked as falsy", () => {
      const result =
        global.dash_clientside.dashboard.update_dashboard_theme(null);

      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-bs-theme",
        "dark",
      );
      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-mantine-color-scheme",
        "dark",
      );
      expect(result).toBe(global.dash_clientside.no_update);
    });

    test("should handle undefined theme_selector_checked as falsy", () => {
      const result =
        global.dash_clientside.dashboard.update_dashboard_theme(undefined);

      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-bs-theme",
        "dark",
      );
      expect(global.document.documentElement.setAttribute).toHaveBeenCalledWith(
        "data-mantine-color-scheme",
        "dark",
      );
      expect(result).toBe(global.dash_clientside.no_update);
    });
  });

  describe("update_ag_grid_theme", () => {
    test("should return light theme classes when theme_selector_checked is true", () => {
      const result =
        global.dash_clientside.dashboard.update_ag_grid_theme(true);
      expect(result).toBe("ag-theme-quartz ag-theme-vizro");
    });

    test("should return dark theme classes when theme_selector_checked is false", () => {
      const result =
        global.dash_clientside.dashboard.update_ag_grid_theme(false);
      expect(result).toBe("ag-theme-quartz-dark ag-theme-vizro");
    });

    test("should handle null theme_selector_checked as falsy", () => {
      const result =
        global.dash_clientside.dashboard.update_ag_grid_theme(null);
      expect(result).toBe("ag-theme-quartz-dark ag-theme-vizro");
    });

    test("should handle undefined theme_selector_checked as falsy", () => {
      const result =
        global.dash_clientside.dashboard.update_ag_grid_theme(undefined);
      expect(result).toBe("ag-theme-quartz-dark ag-theme-vizro");
    });
  });

  describe("update_graph_theme", () => {
    const mockFigure = {
      data: [{ x: [1, 2, 3], y: [4, 5, 6] }],
      layout: {
        title: "Test Chart",
        xaxis: { title: "X Axis" },
        yaxis: { title: "Y Axis" },
      },
    };

    const mockVizroThemes = {
      vizro_light: {
        layout: {
          paper_bgcolor: "white",
          plot_bgcolor: "white",
          font: { color: "black" },
        },
      },
      vizro_dark: {
        layout: {
          paper_bgcolor: "black",
          plot_bgcolor: "black",
          font: { color: "white" },
        },
      },
    };

    test("should apply light theme when theme_selector_checked is true", () => {
      const result = global.dash_clientside.dashboard.update_graph_theme(
        mockFigure,
        true,
        mockVizroThemes,
      );

      expect(result).toHaveLength(2);
      expect(result[0].layout.template).toBe(mockVizroThemes.vizro_light);
      expect(result[1]).toEqual({});
    });

    test("should apply dark theme when theme_selector_checked is false", () => {
      const result = global.dash_clientside.dashboard.update_graph_theme(
        mockFigure,
        false,
        mockVizroThemes,
      );

      expect(result).toHaveLength(2);
      expect(result[0].layout.template).toBe(mockVizroThemes.vizro_dark);
      expect(result[1]).toEqual({});
    });

    test("should preserve original figure data and layout properties", () => {
      const result = global.dash_clientside.dashboard.update_graph_theme(
        mockFigure,
        true,
        mockVizroThemes,
      );

      const updatedFigure = result[0];
      expect(updatedFigure.data).toEqual(mockFigure.data);
      expect(updatedFigure.layout.title).toBe(mockFigure.layout.title);
      expect(updatedFigure.layout.xaxis).toEqual(mockFigure.layout.xaxis);
      expect(updatedFigure.layout.yaxis).toEqual(mockFigure.layout.yaxis);
    });

    test("should handle empty figure", () => {
      const emptyFigure = {};
      const result = global.dash_clientside.dashboard.update_graph_theme(
        emptyFigure,
        true,
        mockVizroThemes,
      );

      expect(result[0].layout.template).toBe(mockVizroThemes.vizro_light);
      expect(result[1]).toEqual({});
    });

    test("should handle figure with no layout", () => {
      const figureNoLayout = { data: [{ x: [1], y: [1] }] };
      const result = global.dash_clientside.dashboard.update_graph_theme(
        figureNoLayout,
        false,
        mockVizroThemes,
      );

      expect(result[0].layout.template).toBe(mockVizroThemes.vizro_dark);
      expect(result[0].data).toEqual(figureNoLayout.data);
    });

    test("should handle null theme_selector_checked as falsy", () => {
      const result = global.dash_clientside.dashboard.update_graph_theme(
        mockFigure,
        null,
        mockVizroThemes,
      );

      expect(result[0].layout.template).toBe(mockVizroThemes.vizro_dark);
      expect(result[1]).toEqual({});
    });

    test("should handle undefined theme_selector_checked as falsy", () => {
      const result = global.dash_clientside.dashboard.update_graph_theme(
        mockFigure,
        undefined,
        mockVizroThemes,
      );

      expect(result[0].layout.template).toBe(mockVizroThemes.vizro_dark);
      expect(result[1]).toEqual({});
    });

    test("should handle missing vizro_themes object", () => {
      const result = global.dash_clientside.dashboard.update_graph_theme(
        mockFigure,
        true,
        {},
      );

      expect(result[0].layout.template).toBeUndefined();
      expect(result[1]).toEqual({});
    });

    test("should preserve deeply nested layout properties", () => {
      const complexFigure = {
        data: [{ x: [1, 2, 3], y: [4, 5, 6], type: "scatter" }],
        layout: {
          title: { text: "Complex Chart", font: { size: 18 } },
          xaxis: { title: "X Axis", range: [0, 10] },
          yaxis: { title: "Y Axis", range: [0, 20] },
          annotations: [{ text: "annotation", x: 1, y: 5 }],
          showlegend: true,
        },
      };

      const result = global.dash_clientside.dashboard.update_graph_theme(
        complexFigure,
        true,
        mockVizroThemes,
      );

      const updatedFigure = result[0];
      expect(updatedFigure.data).toEqual(complexFigure.data);
      expect(updatedFigure.layout.title).toEqual(complexFigure.layout.title);
      expect(updatedFigure.layout.xaxis).toEqual(complexFigure.layout.xaxis);
      expect(updatedFigure.layout.yaxis).toEqual(complexFigure.layout.yaxis);
      expect(updatedFigure.layout.annotations).toEqual(
        complexFigure.layout.annotations,
      );
      expect(updatedFigure.layout.showlegend).toBe(
        complexFigure.layout.showlegend,
      );
      expect(updatedFigure.layout.template).toBe(mockVizroThemes.vizro_light);
    });
  });

  describe("collapse_nav_panel", () => {
    test("should return correct values when n_clicks is not 0 and is_open is true", () => {
      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        1,
        true,
      );
      const expected = [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];
      expect(result).toEqual(expected);
    });

    test("should return correct values when n_clicks is not 0 and is_open is false", () => {
      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        1,
        false,
      );
      const expected = [
        true,
        {
          transform: "rotate(0deg)",
          transition: "transform 0.35s ease-in-out",
        },
        "Hide Menu",
      ];
      expect(result).toEqual(expected);
    });

    test("should auto-collapse on mobile width (< 768px) when n_clicks is 0", () => {
      global.window.innerWidth = 500;
      global.window.innerHeight = 800;

      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        0,
        true,
      );
      const expected = [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];
      expect(result).toEqual(expected);
    });

    test("should auto-collapse on mobile height (< 768px) when n_clicks is 0", () => {
      global.window.innerWidth = 1000;
      global.window.innerHeight = 500;

      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        0,
        false,
      );
      const expected = [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];
      expect(result).toEqual(expected);
    });

    test("should throw PreventUpdate on desktop when n_clicks is 0", () => {
      global.window.innerWidth = 1024;
      global.window.innerHeight = 768;

      expect(() => {
        global.dash_clientside.dashboard.collapse_nav_panel(0, true);
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when n_clicks is null", () => {
      global.window.innerWidth = 1024;
      global.window.innerHeight = 768;

      expect(() => {
        global.dash_clientside.dashboard.collapse_nav_panel(null, true);
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when n_clicks is undefined", () => {
      global.window.innerWidth = 1024;
      global.window.innerHeight = 768;

      expect(() => {
        global.dash_clientside.dashboard.collapse_nav_panel(undefined, false);
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should handle edge case of exactly 768px width", () => {
      global.window.innerWidth = 768;
      global.window.innerHeight = 800;

      expect(() => {
        global.dash_clientside.dashboard.collapse_nav_panel(0, true);
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should handle edge case of exactly 768px height", () => {
      global.window.innerWidth = 1000;
      global.window.innerHeight = 768;

      expect(() => {
        global.dash_clientside.dashboard.collapse_nav_panel(0, true);
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should handle zero and falsy values for is_open", () => {
      const result1 = global.dash_clientside.dashboard.collapse_nav_panel(1, 0);
      const result2 = global.dash_clientside.dashboard.collapse_nav_panel(
        1,
        "",
      );
      const result3 = global.dash_clientside.dashboard.collapse_nav_panel(
        1,
        null,
      );

      const expected = [
        true,
        {
          transform: "rotate(0deg)",
          transition: "transform 0.35s ease-in-out",
        },
        "Hide Menu",
      ];

      expect(result1).toEqual(expected);
      expect(result2).toEqual(expected);
      expect(result3).toEqual(expected);
    });

    test("should handle truthy non-boolean values for is_open", () => {
      const result1 = global.dash_clientside.dashboard.collapse_nav_panel(
        1,
        "true",
      );
      const result2 = global.dash_clientside.dashboard.collapse_nav_panel(1, 1);
      const result3 = global.dash_clientside.dashboard.collapse_nav_panel(
        1,
        {},
      );

      const expected = [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];

      expect(result1).toEqual(expected);
      expect(result2).toEqual(expected);
      expect(result3).toEqual(expected);
    });

    test("should handle multiple clicks", () => {
      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        5,
        true,
      );
      const expected = [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];
      expect(result).toEqual(expected);
    });

    test("should handle negative n_clicks as truthy", () => {
      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        -1,
        false,
      );
      const expected = [
        true,
        {
          transform: "rotate(0deg)",
          transition: "transform 0.35s ease-in-out",
        },
        "Hide Menu",
      ];
      expect(result).toEqual(expected);
    });

    test("should auto-collapse on very small mobile screens", () => {
      global.window.innerWidth = 320; // Small mobile width
      global.window.innerHeight = 568; // Small mobile height

      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        0,
        true,
      );
      const expected = [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];
      expect(result).toEqual(expected);
    });

    test("should auto-collapse when both dimensions are exactly under mobile threshold", () => {
      global.window.innerWidth = 767; // Just under mobile width threshold
      global.window.innerHeight = 767; // Just under mobile height threshold

      const result = global.dash_clientside.dashboard.collapse_nav_panel(
        0,
        false,
      );
      const expected = [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];
      expect(result).toEqual(expected);
    });
  });
});
