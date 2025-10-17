from __future__ import annotations

from typing import Union, Annotated, Literal

from pydantic import ConfigDict, BaseModel, Field

from vizro.models import VizroBaseModel


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

# Without the problematic custom_page_without_subclassing:
dashboard = OldDashboard(pages=[page, custom_page])

# Types are as expected.
assert type(dashboard.pages[0]) is OldPage
assert type(dashboard.pages[1]) is CustomOldPage


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
# Even though CustomNewPage is a subclass of NewPage, it gets turned back into NewPage by validate_instances="always"!
# This is shown more clearly below and maybe surprising.
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


###
# Here's the crux of what happens above. Even though CustomNewPageX is completely compatible with NewPageX and directly
# subclasses it, it gets converted back into the parent NewPageX when revalidate_instances="true".
# X added to names of each of these to avoid very confusing name conflicts.
class NewDashboardX(NewVizroBaseModel):
    pages: list[NewPageX]


# Defined in Vizro framework
class NewPageX(NewVizroBaseModel):
    title: str

    def build(self):
        return "new_page"


# User defined
class CustomNewPageX(NewPageX):
    def build(self):
        return "custom_new_page"


page = NewPageX(title="Title")
custom_page = CustomNewPageX(title="a")
dashboard = NewDashboardX(pages=[page, custom_page])

# Types are NOT as expected!
assert type(dashboard.pages[0]) is NewPageX

try:
    assert type(dashboard.pages[1]) is CustomNewPageX, f"{type(dashboard.pages[1])=}"
except Exception as e:
    # It's been turned into NewPageX, not CustomNewPageX
    print(e)
    print(dashboard.pages[1].build())


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
examples of it. The OldCustomPageWithoutSubclassing already doesn't work so we don't need to worry about that.

Regardless of what it currently may or may not break what are the options?
1. set validate_instances="always" and change our current assumed workflow so that you need to explicitly make custom
models all the way up the tree. Seems like horrible UX for someone just wanting to do OldCustomPage.
2. set validate_instances="always" and make some mechanism (like recursive add_type or some other sort of schema
modification) that would make these schema modifications for you. This means that, unlike now, you'd need to use
add_type (or whatever it would be) for all custom models, not just discriminated unions. It becomes more complex
because you're potentially changing non-union fields into unions, need to figure out how to handle nested things like 
list[Page], etc.
3. set validate_instances="always" and say that no one does this kind of custom model and we don't care about
supporting it. The only kind of custom model we support then is adding something to a field that's already a
discriminated union. UPDATE: we think you need to be able to customise e.g. Page model that's not in discriminated 
union so this isn't a valid option.
4. *don't set* validate_instances="always" - we said today that we didn't like this idea, but now I'm not so sure. 
validate_instances="always" makes it much harder for anyone to use a custom model even in a simple (non discriminated 
union) case. If we think that people being able to easily use a custom model anywhere is important then we could drop
this. But then it also means figuring out some way to do the whole model manager registration thing without 
validate_instances="always" :| IMPORTANT UPDATE: now that I realise how validate_instances="always" coerces back to a 
parent class, it makes me rethink whether validate_instances="always" is even the right thing to do out of principle.
I don't even understand why anyone would want that behaviour? Note validate_instances="subclass-instances" is also an
option but still does the subclass coercion so doesn't help us in any way.
5. set validate_instances="always" and make all our fields that use VizroBaseModel into discriminated unions. May be 
able to do this without add_type.
 
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
- UPDATE: given revelation that revalidate_instances="always" coerces to parent class, I'm now rethinking whether 
it's a good option at all which would mean Option 4 is the only possibility.

Next steps:
- understand what revalidate_instances="always" is actually for and why anyone would want it
- come up with alternatives for how to do the model manager without revalidate_instances="always" e.g. maybe we have
proxy models where that's true just to generate the model tree and then modify that tree to reflect the real one (
that has revalidate_instances="never"

"""


########################################################################################################################
# Discriminated unions - check how add_type works.
class OldRealVizroBaseModel(VizroBaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Good for spotting user typos and being strict.
        validate_assignment=True,  # Run validators when a field is assigned after model instantiation.
    )


# Defined in Vizro framework
class OldRealDashboard(OldRealVizroBaseModel):
    pages: list[Annotated[Union[OldRealPage, OldRealPage2], Field(discriminator="type")]]


# Defined in Vizro framework
class OldRealPage(OldRealVizroBaseModel):
    type: Literal["old_real_page"] = "old_real_page"
    title: str


# Have to define this model too or you get a Union of just one thing and things don't work as expected.
class OldRealPage2(OldRealVizroBaseModel):
    type: Literal["old_real_page2"] = "old_real_page2"
    title: str


# User defined
class CustomOldRealPage(OldRealPage):
    type: Literal["custom_old_real_page"] = "custom_old_real_page"
    # title is now an int
    title: int


class CustomOldRealPageWithoutSubclassing(OldRealVizroBaseModel):
    type: Literal["custom_old_real_page_without_subclassing"] = "custom_old_real_page_without_subclassing"
    title: int


# add_type not relevant here because it's not a discriminated union.
# This all works fine.
page = OldRealPage(title="Title")
custom_page = CustomOldRealPage(title=1)
custom_page_without_subclassing = CustomOldRealPageWithoutSubclassing(title=1)

# Needed to resolve ForwardRefs to get add_type to work.
OldRealDashboard.model_rebuild()
OldRealDashboard.add_type("pages", CustomOldRealPage)
OldRealDashboard.add_type("pages", CustomOldRealPageWithoutSubclassing)

# This all works correctly.
dashboard = OldRealDashboard(pages=[page, custom_page, custom_page_without_subclassing])

# Types are as expected.
assert type(dashboard.pages[0]) is OldRealPage
assert type(dashboard.pages[1]) is CustomOldRealPage
assert type(dashboard.pages[2]) is CustomOldRealPageWithoutSubclassing


#####
class NewRealVizroBaseModel(VizroBaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Good for spotting user typos and being strict.
        validate_assignment=True,  # Run validators when a field is assigned after model instantiation.
        revalidate_instances="always",
    )


# Defined in Vizro framework
class NewRealDashboard(NewRealVizroBaseModel):
    pages: list[Annotated[Union[NewRealPage, NewRealPage2], Field(discriminator="type")]]


# Defined in Vizro framework
class NewRealPage(NewRealVizroBaseModel):
    type: Literal["new_real_page"] = "new_real_page"
    title: str


# Have to define this model too or you get a Union of just one thing and things don't work as expected.
class NewRealPage2(NewRealVizroBaseModel):
    type: Literal["new_real_page2"] = "new_real_page2"
    title: str


# User defined
class CustomNewRealPage(NewRealPage):
    type: Literal["custom_new_real_page"] = "custom_new_real_page"
    # title is now an int
    title: int


class CustomNewRealPageWithoutSubclassing(NewRealVizroBaseModel):
    type: Literal["custom_new_real_page_without_subclassing"] = "custom_new_real_page_without_subclassing"
    title: int


# add_type not relevant here because it's not a discriminated union.
# This all works fine.
page = NewRealPage(title="Title")
custom_page = CustomNewRealPage(title=1)
custom_page_without_subclassing = CustomNewRealPageWithoutSubclassing(title=1)

# Needed to resolve ForwardRefs to get add_type to work.
NewRealDashboard.model_rebuild()
NewRealDashboard.add_type("pages", CustomNewRealPage)
NewRealDashboard.add_type("pages", CustomNewRealPageWithoutSubclassing)

# This all works correctly.
dashboard = NewRealDashboard(pages=[page, custom_page, custom_page_without_subclassing])

# Types are as expected.
assert type(dashboard.pages[0]) is NewRealPage
assert type(dashboard.pages[1]) is CustomNewRealPage
assert type(dashboard.pages[2]) is CustomNewRealPageWithoutSubclassing

"""
Conclusion:
- for discriminated union, everything works as we want it to... Where exactly is the problem we're trying to solve 
here?
"""
