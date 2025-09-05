var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.ColorCellRenderer = (props) => {
  const value = props.value;
  let backgroundColor = "#ffffff";

  // Map tier values to proper colors
  if (value === "Gold") {
    backgroundColor = "#FFD700";
  } else if (value === "Silver") {
    backgroundColor = "#C0C0C0";
  } else if (value === "Bronze") {
    backgroundColor = "#CD7F32";
  }

  const circleStyles = {
    verticalAlign: "middle",
    borderRadius: "50%",
    margin: "0 8px 0 0",
    display: "inline-block",
    width: 12,
    height: 12,
    backgroundColor: backgroundColor,
  };

  const containerStyles = {
    display: "flex",
    alignItems: "center",
    color: "white",
  };

  return React.createElement("div", { style: containerStyles }, [
    React.createElement("span", { style: circleStyles, key: "circle" }),
    React.createElement("span", { key: "text" }, value),
  ]);
};
