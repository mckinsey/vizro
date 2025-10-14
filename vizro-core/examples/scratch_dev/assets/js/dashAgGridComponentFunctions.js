var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.statusCellRenderer = function (params) {
  // You may want to sync this color map with your Python COLOR_MAP_STATUS
  var colorMap = {
    "In Transit": "#1a85ff",
    Processing: "#f6c343",
    Delivered: "#60c96c",
  };
  var color = colorMap[params.value] || "#ccc";
  return React.createElement(
    "div",
    { style: { display: "flex", alignItems: "center", gap: "8px" } },
    React.createElement("span", {
      style: {
        display: "inline-block",
        width: "12px",
        height: "12px",
        background: color,
        borderRadius: "50%",
      },
    }),
    React.createElement("span", null, params.value),
  );
};
