"""Example of creating a dashboard using VizroAI."""

import vizro.plotly.express as px
from dotenv import load_dotenv
from vizro import Vizro
from vizro_ai import VizroAI

load_dotenv()

vizro_ai = VizroAI(model="gpt-4o")
# vizro_ai = VizroAI()

gapminder_data = px.data.gapminder()
tips_data = px.data.tips()

dfs = [gapminder_data, tips_data]
input_text = """
Create a dashboard that displays the Gapminder dataset and the tips dataset.
page1 displays the Gapminder dataset. create a bar chart for average GDP per capita of each continent.
add a filter to filter by continent.
Use a card to explain what Gapminder dataset is about.
The card should only take 1/6 of the whole page.
The rest of the page should be the graph or table. Don't create empty space.
page2 displays the tips dataset. use two different charts to help me understand the data
distributions. one chart should be a bar chart and the other should be a scatter plot.
first chart is on the left and the second chart is on the right.
add a filter to filter data in the scatter plot by smoker.
"""

dashboard = vizro_ai.dashboard(dfs=dfs, user_input=input_text)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
