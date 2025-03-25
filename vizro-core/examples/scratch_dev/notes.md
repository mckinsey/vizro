# Future ideas

- Pythonic shortcut (not possible in YAML) for specifying outputs like `my_custom_action(points_data="scatter_chart.clickData") >> "x.y"`
- Not giving explicit property

# Improvements to note

## Built-in actions

- clearer signatures
- no mapping needed for inputs/outputs - these are done next to function definition
- don't need to look in model manager for e.g. `filter_function`
- no need to wrap inside Action model
- specify inputs directly - much clearer
- can use reserved arguments like `controls` directly
- no more `action_function == _parameter.__wrapped__`

## Custom actions

- realized significance of captured callable and ability to pass runtime arguments correctly

- specify inputs directly - much clearer

- can use reserved arguments like `controls` directly

- TODO future:

- add trigger or similar to builtin args. Not until actions chain handled and have new interact action to understand what it needs 

- look at actions chain next. Should each component only be allowed one single action?

- something that validates target has _output_component_property

- something that does lookup to enable shortcut for input/output component name only

- rename \_on_page_load if desired and make \_filter etc. public.

- Add deprecation warnings etc. for when legacy=True ActionsChain.add_type("actions", f) is needed as well as vm.Graph.add_type("actions", f). Remove ActionsChain and then this will be possible. Should you need to add_type at all though compared to just having AbstractAction as an allowed type? Probably yes.

- enable both list and dict for outputs for Action and AbstractAction get structure of controls right and make public

- built in download (and then other) components - see https://github.com/mckinsey/vizro/pull/1054#discussion_r1989405177

# Put in PR/docs

Note need to do `add_type` for udf.
