#### Decide structure of controls, remove use of ctx.
#
# TODO-AV2 A 1: simplify this as in
#  https://github.com/mckinsey/vizro/pull/1054/commits/f4c8c5b153f3a71b93c018e9f8c6f1b918ca52f6

# TODO-AV2 A 1: improve this structure. See https://github.com/mckinsey/vizro/pull/880.

# TODO-AV2 A 1: _controls is not currently used but instead taken out of the Dash context. This
# will change in future once the structure of _controls has been worked out and we know how to pass ids through.
# See https://github.com/mckinsey/vizro/pull/880

# TODO-AV2 A 2: go through and finish tidying bits that weren't already. Potentially there won't be much code left here
#  at all. Think about where it should live so it might become public in future. Is it just apply_controls and helper
#  functions for that? Do we want public vizro.actions.utils/helpers?

# TODO-AV2 A 2: rename this, make sure it could become public in future but don't make public yet. Probably take in
#  controls + filter_interaction only once have worked out structure of filters/parameters. Then make public once
#  have removed filter_interaction.

# TODO-AV2 A 3: rename _on_page_load if desired and make public.

# TODO-AV2 A 3: can we simplify this to not use ActionsChain, just like we do for filters and parameters?

#### Tidy CapturedCallable.
# TODO-AV2 B 1: try to subclass Mapping. Check if anything requires MutableMapping (used in Vizro AI tests
#  and to set data_frame only?). Try to remove these by making special method for setting data_frame. Then
# can remove as many uses of _arguments as possible and use .items() where suitable instead.

# TODO-AV2 B 2: in future, if we improve wrapping of __call__ inside CapturedCallable (e.g. by using wrapt),
#  this could be done the same way as in AbstractAction and avoid looking at _function. Then we could remove
#  this _parameters property from both Action and AbstractAction. Possibly also the _action_name one.
#  Try and get IDE completion to work for action arguments.

#### Deprecation warnings.
# TODO-AV2 C 1: Put in deprecation warning.

#### Make Action and AbstractAction more powerful and easier to use.
# TODO-AV2 D 1: enable both list and dict for both Action and AbstractAction.

# TODO-AV2 D 2: in future we will expand this to also allow passing a model name without a property specified,
#  so long as _output_component_property exists - need to handle case it doesn't with error.
#  Possibly make a built in a type hint that we can use as field annotation for runtime arguments in
#  subclasses of AbstractAction instead of just using str. Possibly apply this to non-annotated arguments of
#  vm.Action.function and use pydantic's validate_call to apply the same validation there for function inputs.
#  We won't be able to do all the checks at validation time though if we need to look up a model in the model
#  manager. When this change is made the outputs property for filter, parameter and on_page_load should just become
#  `return self.targets` or similar. Consider again whether to do this translation automatically if
#  targets is defined as a field, but sounds like bad idea since it doesn't carry over into the capture("action")
# style of action.

# TODO-AV D 2: work out the best place to put this logic. It could feasibly go in _on_page_load instead.
#  Probably it's better where it is now since it avoid navigating up the model hierarchy
#  (action -> page -> figures) and instead just looks down (page -> figures).
#  Should there be validation inside _on_page_load to check that targets exist and are
#  on the page and target-able components (i.e. are dynamic and hence have _output_component_property)?
#  It's not needed urgently since we always calculate the targets ourselves so we know they are valid.
#  Similar comments apply to filter and parameter. Note that export_data has this logic built into the action
#  itself since the user specifies the target. In future we'll probably have a helper function like
#  get_all_targets_on_page() that's used in many actions. So maybe it makes sense to put it in the action for
#  on_page_load/filter/parameter too.

# TODO-AV D 3: try to enable properties that aren't Dash properties but are instead model fields e.g. header, title.
# See https://github.com/mckinsey/vizro/issues/1078.

# TODO-AV D 4: build in a vizro_download component. At some point after that consider changing export_data to use it,
#  but that's not urgent. See  https://github.com/mckinsey/vizro/pull/1054#discussion_r1989405177.

"""Other tickets:

- new interact action(s)
- override on_page_load by exposing page.actions
- try to remove actionschain. can then document doing `add_type` for user-defined class function. Should you need to
  add_type at all though compared to just having AbstractAction as an allowed type? Probably yes but I'm not sure.
  If we can't remove actions chain then need a better way of adding action that doesn't require two `add_type`.
- work out actions loop and Dash callback vs. Vizro action
- add trigger or similar to builtin args. Not until have new interact action(s) and actions chain sorted
- built in download (and then other) components - see https://github.com/mckinsey/vizro/pull/1054#discussion_r1989405177

Put in PR/docs

Note need to do `add_type` for udf. ActionsChain.add_type("actions", f) is needed as well as vm.Graph.add_type("actions", f).

Priorities:

Continue pondering:
Antony starts: work out details of new interact (or whatever it is)
actions loop and actions chain
dynamic parameter
cascading filters

P1
actions v2 PR
Dash persistence bug
drill through has two solutions:
  - ideal: create the new "interact" (or whatever it is) action and use this - relies on Dash persistence bug.
    Specify target filter on different page.
  - non-ideal: use current filter_interaction - doesn't rely on Dash persistence bug. Specify target figure on
    different page.
if easy: empty dataframe - columns exist but not populated

P2

P3
datetime picker
empty dataframe with unknown columns


"""
