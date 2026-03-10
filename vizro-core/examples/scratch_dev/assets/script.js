var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.Button = (props) => {
  const { setData, data } = props;

  function onClick() {
    setData();
  }
  return React.createElement(
    "button",
    {
      onClick: onClick,
      className: props.className,
    },
    props.value,
  );
};
