from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict


##### Without revalidate_instances
# Defined in Vizro framework
class OldVizroBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Good for spotting user typos and being strict.
        validate_assignment=True,  # Run validators when a field is assigned after model instantiation.
    )


# Defined in Vizro framework
class OldDashboard(OldVizroBaseModel):
    pages: list[OldPage]


# Defined in Vizro framework
class OldPage(OldVizroBaseModel):
    title: str


# User defined
class CustomOldPage(OldPage):
    # title is now an int
    title: int


class CustomOldPageWithoutSubclassing(OldVizroBaseModel):
    title: int


# add_type not relevant here because it's not a discriminated union.
# This all works fine.
page = OldPage(title="Title")
custom_page = CustomOldPage(title=1)
custom_page_without_subclassing = CustomOldPageWithoutSubclassing(title=1)

# CustomOldPage passes validation because it subclasses OldPage but CustomOldPageWithoutSubclassing doesn't.
# This is maybe obvious now we look at it but it's inconsistent with discriminated unions where add_type
# would make both of these possible.
try:
    dashboard = OldDashboard(pages=[page, custom_page, custom_page_without_subclassing])
except Exception as e:
    print(e)


##### With revalidate_instances
# Defined in Vizro framework
class NewVizroBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Good for spotting user typos and being strict.
        validate_assignment=True,  # Run validators when a field is assigned after model instantiation.
        revalidate_instances="always",
    )


# Defined in Vizro framework
class NewDashboard(NewVizroBaseModel):
    pages: list[NewPage]


# Defined in Vizro framework
class NewPage(NewVizroBaseModel):
    title: str


# User defined
class CustomNewPage(NewPage):
    # Allow int as well as str
    title: int


class CustomNewPageWithoutSubclassing(NewVizroBaseModel):
    title: int


page = NewPage(title="Title")
custom_page = CustomNewPage(title=1)
custom_page_without_subclassing = CustomNewPageWithoutSubclassing(title=1)

# Now CustomNewPage also doesn't pass validation because NewDashboard revalidates it against NewPage rather than CustomPage.
try:
    dashboard = NewDashboard(pages=[page, custom_page, custom_page_without_subclassing])
except Exception as e:
    print(e)


# You would need to do this instead:
class CustomNewDashboard(NewDashboard):
    pages: list[Union[NewPage, CustomNewPage, CustomNewPageWithoutSubclassing]]


# No validation errors any more! But it's horrible for a user to do.
page = NewPage(title="Title")
custom_page = CustomNewPage(title=1)
custom_page_without_subclassing = CustomNewPageWithoutSubclassing(title=1)
custom_dashboard = CustomNewDashboard(pages=[page, custom_page, custom_page_without_subclassing])

"""
So current behaviour is:
- discriminated union: with add_type, you can use a custom model that subclasses a valid model OR one that subclasses
  BaseModel
- anything that's not discriminated union: you can use a custom model that subclasses a valid model.

When we set validate_instances="always" it affects more than just discriminated unions. Think about the non-discriminated
union case here. It becomes impossible to use a custom component at any point in the model tree without explicitly
redefining every model above that point in the hierarchy. This is something I always wanted to avoid with the original
design because otherwise making a minor tweak to a model at a lower level needs many new custom models to be defined
which is horrible UX.
So when I was originally working out how someone would make a custom model I found that everything worked great so
long as your subclass a valid model (as in the OldCustomPage example). But then I discovered it didn't work with a
discriminated union so had to come up with a solution there, which was add_type. This was a workaround
to make it possible to add subclasses of valid models to discriminated unions. It also allowed you to add a subclass
of BaseModel.

So if we set validate_instances="always" then we break anyone who is doing OldCustomPage. Is this currently a
legitimate/documented workflow or something that anyone does? It's not really clear - we don't have any explicit
examples of it. The OldCustomPageWithoutSubclassing already doesn't work.

Regardless of what it currently may or may not break what are the options?
1. set validate_instances="always" and change our current assumed workflow so that you need to explicitly make custom
models all the way up the tree. Seems like horrible UX for someone just wanting to do OldCustomPage.
2. set validate_instances="always" and make some mechanism (like recursive add_type or some other sort of schema
modification) that would make these schema modifications for you. This means that, unlike now, you'd need to use
add_type (or whatever it would be) for all custom models, not just discriminated unions. It becomes more complex
because you're potentially changing non-union.
fields into unions, need to figure out how to handle nested things like list[Page], etc.
3. set validate_instances="always" and say that no one does this kind of custom model and we don't care about
supporting it. The only kind of custom model we support then is adding something to a field that's already a
discriminated union.
4. *don't set* validate_instances="always" - we said today that we didn't like this idea, but now I'm not so sure.
validate_instances="always" makes it much harder for anyone to use a custom model even in a simple (non discriminated
union) case. If we think that people being able to easily use a custom model anywhere is important then we could drop
this. But then it also means figuring out some way to do the whole model manager registration thing without
validate_instances="always" :|

I don't like option 1 at all. All others seem feasible but bad...

Option 2: intention is that you can use custom model anywhere but user needs to manually add_type always (not just
discriminated unions).
- how do we actually do this? e.g. need to expand add_type to create Unions out of non-Unions :| Sounds very
complicated unless we can think of a much better way of modifying schema consistently - I remember making a
deliberate choice to *not* do this when I did add_type originally just for discriminated unions. Or all our type hints
just need to be VizroBaseModel (sounds very bad) or do something really weird/metaclass with pydantic (also sounds awful).
- breaking change if we assume people are doing this. Some new way for them to still achieve it.

Option 3: intention is that you can't use custom model anywhere, just in discriminated unions.
- breaking change if we assume people are doing it. No longer any way for people to achieve it.
- does it seem like a reasonable/principled restriction that you can only inject a custom model where there's a
discriminated union? In practice I'm sure this is by a long way the most common, because all the parts where you might
want to add a custom model we have a discriminated union already. But philosophically is this an improvement or not?
It means we are less extensible but have fewer, better defined, extension points. But what if e.g. you just want to
modify Page.build? That sounds pretty reasonable to me...
- we would in the same position we thought we were in earlier today where we only need to think about discriminated
unions. For those cases it's still open exactly whether/how you need to do add_type.

Option 4: intention is that you can use custom model anywhere.
- non-breaking change
- optionally we could also come up with a new mechanism for allowing arbitrary types in discriminated union without
add_type, e.g. inherit from Custom mixin that has type: custom (could even just be VizroBaseModel, means no need to
do type field for a custom field which would be nice improvement) and put that the discriminated union; or maybe do
what's currently in types.py.
- would also need to come up with some way to do model manager registration or selectively turn
validate_instances="always" on/off.

Conclusion:
- all options seem bad. Not sure what the ultimate solution should be here regardless of what it currently
breaks. Currently in some despair. How we can stay extensible but still benefit from pydantic validation. Do we
just need to become less tolerant of custom components?
- if we decide that Option 3 is not too restrictive then it's definitely my preferred one. Let's think about how
restrictive this would be.
- if it is too restrictive then Options 2 and 4 both on the table for me but I don't like either. It comes down to
the same question we thought of earlier: should user be trying to modify schema or just able to put in a custom model
easily wherever they want to? Probably my preference is for option 4 (and in future we come up with some better
system for being able to properly extend the schema). But then we're back to the model manager problem where
validate_instances="always" really felt like the right solution :|
- worst case scenario we do Option 1 but it just sounds horrible.

"""
