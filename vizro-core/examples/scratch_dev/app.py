"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro


page_1 = vm.Page(title="Page 1", components=[vm.Text(text="Page 1 content")])
page_2 = vm.Page(title="Page 2", components=[vm.Text(text="Page 2 content")])
page_3 = vm.Page(title="Page 3", components=[vm.Text(text="Page 3 content")])
page_4 = vm.Page(title="Page 4", components=[vm.Text(text="Page 4 content")])
page_5 = vm.Page(title="Page 5", components=[vm.Text(text="Page 5 content")])
page_6 = vm.Page(title="Page 6", components=[vm.Text(text="Page 6 content")])

# Accordion only (no navbar): grouped pages with icons per group
dashboard = vm.Dashboard(
    pages=[page_1, page_2, page_3, page_4, page_5, page_6],
    navigation=vm.Navigation(
        nav_selector=vm.Accordion(
            pages={
                "Group A": ["Page 1", "Page 4"],
                "Group B": ["Page 2", "Page 5"],
                "Group C": ["Page 3", "Page 6"],
            },
            icons={
                "Group A": "article",
                "Group B": "dashboard",
                "Group C": "info",
            },
        ),
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
