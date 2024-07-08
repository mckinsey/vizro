"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro

page_1 = vm.Page(title="Page 1", components=[vm.Card(text="Placeholder")])
page_2 = vm.Page(title="Page 2", components=[vm.Card(text="Placeholder")])
page_3 = vm.Page(title="Page 3", components=[vm.Card(text="Placeholder")])
page_4 = vm.Page(title="Page 4", components=[vm.Card(text="Placeholder")])
page_5 = vm.Page(title="Page 5", components=[vm.Card(text="Placeholder")])
page_6 = vm.Page(title="Page 6", components=[vm.Card(text="Placeholder")])
page_7 = vm.Page(title="Page 7", components=[vm.Card(text="Placeholder")])
page_8 = vm.Page(title="Page 8", components=[vm.Card(text="Placeholder")])
page_9 = vm.Page(title="Page 9", components=[vm.Card(text="Placeholder")])
page_10 = vm.Page(title="Page 10", components=[vm.Card(text="Placeholder")])

dashboard = vm.Dashboard(
    pages=[page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8, page_9, page_10],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Page 1", pages=["Page 1"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 2"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 3"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 4"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 5"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 6"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 7"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 8"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 9"], icon="Home"),
                vm.NavLink(label="Page 1", pages=["Page 10"], icon="Home"),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
