"""Rough example used by developers."""

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Dashboard Title",
    pages=[
        vm.Page(
            title="Tabs with nested containers",
            components=[
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Tab Label 1",
                            components=[vm.Container(title="Visible Title", components=[vm.Button()])],
                        ),
                        vm.Container(title="Tab Label 2", components=[vm.Button()]),
                    ],
                ),
                vm.Container(
                    title="Visible Title",
                    components=[vm.Button()],
                ),
            ],
        )
    ],
)

Vizro().build(dashboard).run()

if __name__ == "__main__":
    Vizro().build(dashboard).run()
