from plotly import graph_objects as go


class _DashboardReadyFigure(go.Figure):
    # Just for IDE completion and to define new attribute
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = args[0] if args else None
        #  refers to the data argument of https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html
        if isinstance(data, dict):
            self._captured_callable = data.get("_captured_callable", None)

    # This fixes copy.deepcopy(_DashboardReadyFigure), but pickling fails in case of functions decorated with `capture`
    # https://stackoverflow.com/questions/52185507/pickle-and-decorated-classes-picklingerror-not-the-same-object
    # If wanting to save _DashboardReadyFigure objects, we currently recommend "dill" (see also example in link)
    # https://pypi.org/project/dill/
    def __reduce__(self):
        _, (props,) = super().__reduce__()
        props["_captured_callable"] = self._captured_callable
        return self.__class__, (props,)
