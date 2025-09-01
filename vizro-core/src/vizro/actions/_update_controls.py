import base64
import json
from typing import Literal

from dash import get_relative_path
from pydantic import Field

from vizro._vizro_utils import _experimental
from vizro.actions._abstract_action import _AbstractAction
from vizro.models._models_utils import _log_call
from vizro.models.types import ModelID

# TODO NOW: decide whether to make it control or controls plural. For now I just wrote it as singular but there's
#  inconsistency with filename and type.
"""
I'm not sure what the right syntax would be for targeting multiple controls?

Copied from https://github.com/McK-Internal/vizro-internal/issues/1939:
It should be possible to target multiple controls in one click
(think e.g. clicking on a 2D heatmap, see Max example in mckinsey/vizro#1301).
So we need some way to do e.g. target="country_filter", lookup="country" as well as
target="continent_filter", lookup="continent". This could be multiple update_control calls
or better a single update_controls. In this case what would API be? How do you assign the
right values to the right targets? Maybe a dictionary like {"country_filter": "country",
"continent_filter": "continent"}?

Then in the (more common) case of targeting a single control, what would it look like? target = {"target_id":
"species"}? Then there would be no need for separate lookup argument which is maybe nicer overall? Not sure which of
these I prefer:
1. target="filter" lookup="x"
2. targets={"filter": "x"}
3. targets=["continet_filter", "country_filter"] lookups=["x", "y"]
4. something else?

Option 3 is effectively unzipped version of 2. I think I prefer 2 to 3 but can predict problems with it if we want to add more argument
in future (e.g. replace vs. append mode). Could have targets be a pydantic model itself if that helps but want to
keep simple cases simple. How would it work with a default lookup value also?

Overall I tend to preferring option 1 for now but then I have no idea how to extend it to multiple controls in
future. Maybe we should ask chatGPT if it has any ideas here... Possibly overall it's easier for a user to just chain multiple
update_control actions together, just it's not so performant. Then ideally we'd need to come up with some way of doing
parallel actions ideally. Relates to an idea I had about "batching" actions - let's discuss some time...
"""


# TODO NOW: let's get this working for graph first and then worry about AgGrid.
# When it comes to AgGrid, let's discuss how we could implement using selectedData.
@_experimental
class update_control(_AbstractAction):
    """...

    Args:
        ...
    """

    type: Literal["update_controls"] = "update_controls"
    target: ModelID = Field(
        description="...",  # Filter/parameter id, not selector id
    )
    """
    TODO NOW: work out a good argument name and syntax for this.

    For graphs we want to start from _trigger["points"][0] and then be able to navigate to:
    1. something at root level like x or y - so lookup="x"
    2. something inside customdata. How should user specify this? Could use glom or other lookup syntax like
    lookup=customdata.0. It looks a bit weird but I don't think there's any better alternative?
      - I don't think we want to look at the function call to see if customdata was provided and then lookup based on
        that function call (we do this now). BUT maybe if it improves user experience then it's ok.
      - For filter we could lookup target column name automatically but that's not possible for parameter.
      - We could suggest users do custom data in a dictionary like {"species": "species"} rathern than indexing by
      number (suggested by ChatGPT, I didn't realise it was possible before actually. It seems to work not very
      officially documented) and then lookup="species" would work straight away without the "customdata."
      - should customdata.0 be the default value for graphs? Then the user wouldn't need to provide that much - only
      in cases where they need customdata.1 which is much less common.
    Overall my feeling is we should use something like glom or another lookup syntax that works for lookup="x" and
    lookup="customdata.0" (or "customdata[0]"), which would probably be the default.

    Don't worry about being able to navigate to anything outside _trigger["points"][0].

    """
    lookup: str  # Joe said "The name “lookup” could indeed be improved. In VizX we used something
    # like “source_field_name” to make it explicit

    @_log_call
    def pre_build(self):
        # if target is on same page as trigger:
        #     self._same_page = True
        # else:
        #     self._same_page = False
        #     if not self.target.show_in_url:
        #         raise ValueError
        # Also need to check if target is found in dashboard at all and raise error if not
        # Check that target control selector is categorical.

        pass

    def function(self, _trigger):
        root = _trigger["points"][0]
        value = do_lookup(root, self.lookup)  # do this somehow
        # You suggested that the logic for doing the lookup lives in the Graph model itself, which sounds very sensible.
        # That way we can implement different logic for Graph vs. AgGrid. From memory the triggering Graph model should
        # be available in self._parent_model or something like that (hacky but ok for now).
        # Generally I like the idea of being able to hook in so that if we (or a user) adds a new ControlType or
        # ComponentType, it's easy to use the same update_control action rather than write a whole new action for it.
        # Then this would be something like parent_model._update_control_hook(root, self.lookup)
        # Should we just let self.lookup itself be a captured callable? Think of case of wanting to update a control
        # to a particular value from a Button - should it go through this same action or not? How could you just
        # specify a static value to send without needing to write a new method in vm.Button? Something like:
        # lookup = lambda: 3 or Literal[3] (but how to do from yaml?). How can lookup specify a lookup inside trigger
        # and also a static value? Actually this would work if we just ignore trigger in the update_control_hook in
        # Button and return lookup unaltered, so no need to function for that anyway.

        # Need to handle case that target selector is multi=False or multi=True. Or just only handle
        # multi=False case for now if that's easier (raise error in pre-build for multi=True).
        # value = [value] if self.target.multi else value
        if self._same_page:
            return value
        else:
            # TODO NOW: Double check this is the right encoding scheme and matches the JS one.
            # Don't make this public yet.
            def encode_to_base64(value):
                json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
                b64_bytes = base64.urlsafe_b64encode(json_bytes)
                return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"

            # lookup page path of self.target in dash registry, not model_manager, since homepage path needs to be "/"
            page_path = ...
            # ideally this shouldn't overwrite all the URL params but just append to existing ones.
            # What's the best way to do that? If it does override then that's ok - we can fix the bug later.
            # TODO NOW: alternative approach is maybe don't send directly to vizro_url but instead to some proxy
            #  object and then update vizro_url with cs callback that does encoding.
            # This is nice idea so then b64 logic not needed in Python (yet anyway).
            # And same page vs. different looks more similar.
            # Then do change page as another action in the chain? Would be an extra callback but work with chain. Not sure
            # if good idea.
            # Currently not sure whether this should actually change page or not in case that target is on another page.
            # Probably it should change page by default anyway.
            # Need to make url safe the target id (though not base64).
            url_query_params = f"?{self.target}={encode_to_base64(value)}"
            return get_relative_path(page_path), url_query_params

    @property
    def outputs(self):  # type: ignore[override]
        if self._same_page:
            return self.target  # Should target underlying selector.value.
        else:
            return ["vizro_url.pathname", "vizro_url.search"]
