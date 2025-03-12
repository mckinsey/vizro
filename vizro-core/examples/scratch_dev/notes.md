# Future ideas

* Pythonic shortcut (not possible in YAML) for specifying outputs like `my_custom_action(points_data="scatter_chart.clickData") >> "x.y"`
* Not giving explicit property

# Improvements to note


## Built-in actions
* clearer signatures
* no mapping needed for inputs/outputs - these are done next to function definition
* don't need to look in model manager for e.g. `filter_function`
* no need to wrap inside Action model
* specify inputs directly - much clearer
* can use reserved arguments like `controls` directly
* no more `action_function == _parameter.__wrapped__`

## Custom actions
* realised significance of captured callable and ability to pass runtime arguments correctly
* specify inputs directly - much clearer
* can use reserved arguments like `controls` directly
 

TODO future: rename _on_page_load if desired and make _filter etc. public.
Add deprecation warnings etc. for when legacy=True

# Put in PR/docs

Note need to do `add_type` for udf. TODO NOW: actually try this out.