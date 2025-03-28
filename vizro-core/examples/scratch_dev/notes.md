# Future ideas

- Pythonic shortcut (not possible in YAML) for specifying outputs like `my_custom_action(points_data="scatter_chart.clickData") >> "x.y"`
- Not giving explicit property

# Improvements to note

- ModelID public and now alias instead of NewType
- fix filter_interaction so targets not optional

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
