function update_checklist_values(value1 = [], value2 = [], options = []) {
    const ctx = dash_clientside.callback_context.triggered;
    if (!ctx.length) {
        return dash_clientside.no_update;
    } else {
        const triggeredId = dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
        if (triggeredId) {
            if (triggeredId.includes("select_all")) {
                if (value1.length) {
                    return [options, value1];
                }
                return [[], []];
            }
            else {
                const allSelected = value2.length === options.length;
                const noneSelected = value2.length === 0;
                if (value1.length) {
                    if (noneSelected) {
                        return [[], []];
                    }
                    if (!allSelected) {
                        return [value2, []];
                    }
                } else {
                    if (allSelected) {
                        return [options, ["Select All"]];
                    }
                    return [value2, []];
                }
            }
        }
    }
}

window.dash_clientside = {
  ...window.dash_clientside,
  checklist: {
    update_checklist_values: update_checklist_values,
  },
};