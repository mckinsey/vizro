import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
import dash_mantine_components as dmc
from typing import Literal
from pydantic import Field
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class MantineCard(VizroBaseModel):
    """Custom Mantine Card component with image, text, and button.

    Args:
        type (Literal["mantine_card"]): Defaults to "mantine_card".
        title (str): Card title text. Defaults to "Card Title".
        badge_text (str): Badge text to display. Defaults to "".
        badge_color (str): Badge color. Defaults to "pink".
        description (str): Card description text. Defaults to "".
        button_text (str): Button text. Defaults to "Learn More".
        image_url (str): URL for the card image. Defaults to Mantine demo image.
        width (int): Card width in pixels. Defaults to 350.
    """

    type: Literal["mantine_card"] = "mantine_card"
    title: str = Field(default="Card Title", description="Card title text")
    badge_text: str = Field(default="", description="Badge text to display")
    badge_color: str = Field(default="pink", description="Badge color")
    description: str = Field(default="", description="Card description text")
    button_text: str = Field(default="Learn More", description="Button text")
    image_url: str = Field(
        default="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-8.png",
        description="URL for the card image",
    )
    width: int = Field(default=350, description="Card width in pixels")

    @_log_call
    def build(self):
        """Builds the Mantine card component."""
        card_children = [
            dmc.CardSection(
                dmc.Image(
                    src=self.image_url,
                    h=160,
                    alt=self.title,
                )
            ),
        ]

        # Add title and badge if provided
        group_children = [dmc.Text(self.title, fw=500)]
        if self.badge_text:
            group_children.append(dmc.Badge(self.badge_text, color=self.badge_color))

        card_children.append(
            dmc.Group(
                group_children,
                justify="space-between",
                mt="md",
                mb="xs",
            )
        )

        # Add description if provided
        if self.description:
            card_children.append(
                dmc.Text(
                    self.description,
                    size="sm",
                )
            )

        # Add button
        card_children.append(
            dmc.Button(
                self.button_text,
                fullWidth=True,
                mt="md",
            )
        )

        return dmc.Card(
            id=self.id,
            children=card_children,
            withBorder=True,
            w=self.width,
        )


# Register the custom component type with Page
vm.Page.add_type("components", MantineCard)

page_1 = vm.Page(
    title="Custom Mantine Card Demo",
    layout=vm.Flex(direction="row", wrap=True),
    components=[
        MantineCard(
            title="Norway Fjord Adventures",
            badge_text="On Sale",
            badge_color="pink",
            description="With Fjord Tours you can explore more of the magical fjord landscapes with tours and "
            "activities on and around the fjords of Norway",
            button_text="Book classic tour now",
        ),
        vm.Card(text="## Regular Vizro Card\n\nThis is a standard Vizro card component for comparison."),
        vm.Button(text="Click me", variant="filled"),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
