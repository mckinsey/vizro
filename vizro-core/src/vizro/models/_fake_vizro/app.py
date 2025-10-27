"""Example app.py to play with the fake vizro models."""

from typing import Union

from vizro.models._fake_vizro.models import Card, Dashboard, Graph, Page, VizroBaseModel


class CustomPage(Page):
    # Allow int
    title: int


class CustomPageBase(VizroBaseModel):
    title: int
    components: list[Union[Graph, Card]]


class CustomGraph(Graph):
    figure: int


class CustomGraphBase(VizroBaseModel):
    figure: int


# If the above custom components subclass VizroBaseModel instead of Page/Graph then behaviour should be the same (
# unlike it is now).
graph_1 = Graph(figure="a")
custom_graph_1 = CustomGraph(figure=2)

graph_2 = Graph(figure="a")
custom_graph_2 = CustomGraph(figure=2)

page = Page(title="Title", components=[graph_1, custom_graph_1])
custom_page = CustomPage(title=2, components=[graph_2, custom_graph_2])

# No add_type needed anywhere!!

dashboard = Dashboard(pages=[page, custom_page])
dashboard = Dashboard.model_validate(dashboard)

assert type(dashboard.pages[0]) is Page
assert type(dashboard.pages[1]) is CustomPage
assert type(dashboard.pages[0].components[0]) is Graph
assert type(dashboard.pages[0].components[1]) is CustomGraph
assert type(dashboard.pages[1].components[0]) is Graph
assert type(dashboard.pages[1].components[1]) is CustomGraph

###
# YAML configuration
# Must have type specified since it's a real discriminated union:
graph_dict = dict(figure="a", type="graph")  # , type="graph"
# Can't specify type since it's not a real discriminated union. There's no way of doing a custom component like this
# (this is currently possible thanks to add_type but in docs we say it's not possible so it's ok to break).
# Comment MS: I think "don't have to" is a better term than "can't"?? I think it works if one specifies the type!
page = dict(title="Title", components=[graph_dict])

dashboard = Dashboard(pages=[page])
dashboard = Dashboard.model_validate(dashboard)

assert type(dashboard.pages[0]) is Page
assert type(dashboard.pages[0].components[0]) is Graph


"""
Normal cases (2 sub-cases):
- Python 
- yaml (or json)

Custom components cases (subclassing VizroBaseModel and specific model) (4+1 sub-cases):
- Add to normal field
- Add to discriminated union field

- YAML should just not work

Wrong cases (should raise validation error) (2 sub-cases):
- Python wrong
- YAML (or JSON) wrong
"""


## TEST CASES (9 total: 2 normal + 4 custom + 1 YAML custom + 2 wrong) ###

GREEN_TICK = "\u2705"
RED_CROSS = "\u274c"

print("\n" + "=" * 70)
print("NORMAL CASES (2)")
print("=" * 70)

print("\n=== TEST 1: Normal Python instantiation ===")
try:
    graph = Graph(figure="test_figure")
    page = Page(title="Test Page", components=[graph])
    dashboard = Dashboard(pages=[page])
    dashboard = Dashboard.model_validate(dashboard)
    assert type(dashboard.pages[0]) is Page
    assert type(dashboard.pages[0].components[0]) is Graph
    print(f"{GREEN_TICK} PASS")
except Exception as e:
    print(f"{RED_CROSS} FAIL: {e}")


print("\n=== TEST 2: Normal YAML/dict instantiation ===")
try:
    graph_dict = {"figure": "test_figure", "type": "graph"}
    page_dict = {"title": "Test Page", "components": [graph_dict]}
    dashboard_dict = {"pages": [page_dict]}
    dashboard = Dashboard.model_validate(dashboard_dict)
    assert type(dashboard.pages[0]) is Page
    assert type(dashboard.pages[0].components[0]) is Graph
    print(f"{GREEN_TICK} PASS")
except Exception as e:
    print(f"{RED_CROSS} FAIL: {e}")


print("\n" + "=" * 70)
print("CUSTOM COMPONENT CASES (4)")
print("=" * 70)

print("\n=== TEST 3: Custom (subclass Page) in normal field (pages) ===")
try:
    custom_page = CustomPage(title=456, components=[Graph(figure="test_figure")])
    dashboard = Dashboard(pages=[custom_page])
    dashboard = Dashboard.model_validate(dashboard)
    assert type(dashboard.pages[0]) is CustomPage
    print(f"{GREEN_TICK} PASS")
except Exception as e:
    print(f"{RED_CROSS} FAIL: {e}")


print("\n=== TEST 4: Custom (subclass Graph) in discriminated union field (components) ===")
try:
    custom_graph = CustomGraph(figure=123)
    page = Page(title="Test Page", components=[custom_graph])
    dashboard = Dashboard(pages=[page])
    dashboard = Dashboard.model_validate(dashboard)
    assert type(dashboard.pages[0].components[0]) is CustomGraph
    print(f"{GREEN_TICK} PASS")
except Exception as e:
    print(f"{RED_CROSS} FAIL: {e}")


print("\n=== TEST 5: Custom (subclass VizroBaseModel) in normal field (pages) ===")
try:
    custom_page_base = CustomPageBase(title=789, components=[Graph(figure="test_figure")])
    dashboard = Dashboard(pages=[custom_page_base])
    dashboard = Dashboard.model_validate(dashboard)
    assert type(dashboard.pages[0]) is CustomPageBase
    print(f"{GREEN_TICK} PASS")
except Exception as e:
    print(f"{RED_CROSS} FAIL: {e}")


print("\n=== TEST 6: Custom (subclass VizroBaseModel) in discriminated union field (components) ===")
try:
    custom_graph_base = CustomGraphBase(figure=999)
    page = Page(title="Test Page", components=[custom_graph_base])
    dashboard = Dashboard(pages=[page])
    dashboard = Dashboard.model_validate(dashboard)
    assert type(dashboard.pages[0].components[0]) is CustomGraphBase
    print(f"{GREEN_TICK} PASS")
except Exception as e:
    print(f"{RED_CROSS} FAIL: {e}")


print("\n" + "=" * 70)
print("YAML WITH CUSTOM COMPONENT - SHOULD NOT WORK (1)")
print("=" * 70)

print("\n=== TEST 7: YAML with custom component - should NOT work ===")
try:
    custom_graph_dict = {"figure": 123, "type": "custom_graph"}
    page_dict = {"title": "Test Page", "components": [custom_graph_dict]}
    dashboard_dict = {"pages": [page_dict]}
    dashboard = Dashboard.model_validate(dashboard_dict)
    print(
        f"{RED_CROSS} UNEXPECTED: Validation passed when it shouldn't (got type: {type(dashboard.pages[0].components[0])})"
    )
except Exception as e:
    print(f"{GREEN_TICK} PASS (correctly rejected): {type(e).__name__}")


print("\n" + "=" * 70)
print("WRONG CASES - SHOULD RAISE VALIDATION ERROR (2)")
print("=" * 70)

print("\n=== TEST 8: Python wrong - wrong model in pages field ===")
try:
    graph = Graph(figure="a")
    dashboard = Dashboard(pages=[graph])  # Graph is not a Page; should raise validation error
    dashboard = Dashboard.model_validate(dashboard)
    print(f"{RED_CROSS} FAIL: Should have raised validation error")
except Exception as e:
    print(f"{GREEN_TICK} PASS (correctly rejected): {type(e).__name__}")


print("\n=== TEST 9: YAML wrong - wrong model in pages field ===")
try:
    graph_dict = {"figure": "a", "type": "graph"}  # Graph is not a Page
    dashboard_dict = {"pages": [graph_dict]}
    dashboard = Dashboard.model_validate(dashboard_dict)
    print(f"{RED_CROSS} FAIL: Should have raised validation error")
except Exception as e:
    print(f"{GREEN_TICK} PASS (correctly rejected): {type(e).__name__}")
