import pandas as pd
import vizro.plotly.express as px
from vizro.models.types import capture

years = [1952, 1962, 1972, 1982, 1992, 2002, 2007]
# Annual population rank (1 = most populous) for each country.
ranks = {
    "China": [5, 4, 3, 2, 2, 1, 1],
    "Germany": [2, 1, 1, 4, 3, 4, 5],
    "India": [4, 5, 5, 1, 1, 2, 3],
    "Japan": [3, 3, 2, 3, 4, 3, 2],
    "USA": [1, 2, 4, 5, 5, 5, 4],
}
rank_data = pd.DataFrame(
    [
        {"year": year, "country": country, "rank": country_ranks[i]}
        for country, country_ranks in ranks.items()
        for i, year in enumerate(years)
    ]
)


@capture("graph")
def bump(data_frame: pd.DataFrame):
    fig = px.line(data_frame, x="year", y="rank", color="country", markers=True)
    fig.update_traces(line_width=3)
    fig.update_yaxes(autorange="reversed", title="Rank")
    fig.update_xaxes(title="Year")
    return fig


fig = bump(rank_data)
