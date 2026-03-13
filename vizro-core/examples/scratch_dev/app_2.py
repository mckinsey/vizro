"""Claim cases dashboard - KPI cards targetable by filters, with navigation to detail pages."""

import dash_bootstrap_components as dbc
import pandas as pd
import vizro.models as vm
from dash import dcc, get_relative_path, html
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.models.types import capture
from vizro.tables import dash_ag_grid


@capture("figure")
def claim_kpi_card(data_frame: pd.DataFrame, row_index: int = 0):
    """Renders one KPI-style card for the row at row_index.
    Claim ID in header, description + last update + recommendation in body.
    """
    if data_frame.empty or row_index >= len(data_frame):
        return html.Div("—", className="p-3")
    row = data_frame.iloc[row_index]
    claim_id = row["claim_id"]
    last_update_val = row["last_update"]
    last_update_str = (
        last_update_val.strftime("%d/%m/%Y") if hasattr(last_update_val, "strftime") else str(last_update_val)[:10]
    )
    header = dbc.CardHeader(html.H4(f"Claim ID: #{claim_id}", className="card-kpi-title"))
    body_text = dcc.Markdown(
        f"""
        {row["description"]} \n
        Last update: {last_update_str} \n
        Recommendation: {row["recommendation"]}
    """
    )
    body = dbc.CardBody(body_text)
    card = dbc.Card([header, body])
    href = get_relative_path(f"/claim-{claim_id}")
    return dbc.NavLink(
        children=card,
        href=href,
        target="_top",
    )


# --- Fake claim cases dataset ---
claim_cases_df = pd.DataFrame(
    [
        {
            "claim_id": 486986,
            "description": "Fire damage in a hotel belonging to a large hotel chain",
            "last_update": pd.Timestamp("2025-07-12"),
            "recommendation": "Band B",
            "date_of_loss": pd.Timestamp("2025-07-05"),
            "routing_recommendations": "Band B",
            "current_adjuster": "Jenny Smith",
            "ai_flags": "All",
            "last_transaction": "All",
        },
        {
            "claim_id": 901061,
            "description": "Flood damage in a warehouse owned by a retail chain",
            "last_update": pd.Timestamp("2025-07-05"),
            "recommendation": "Band A",
            "date_of_loss": pd.Timestamp("2025-07-10"),
            "routing_recommendations": "Band A",
            "current_adjuster": "Jenny Smith",
            "ai_flags": "All",
            "last_transaction": "All",
        },
        {
            "claim_id": 996616,
            "description": "Water damage in a restaurant caused by a burst pipe",
            "last_update": pd.Timestamp("2025-07-15"),
            "recommendation": "STP",
            "date_of_loss": pd.Timestamp("2025-07-01"),
            "routing_recommendations": "STP",
            "current_adjuster": "Jenny Smith",
            "ai_flags": "All",
            "last_transaction": "All",
        },
    ]
)

claim_cases_container = vm.Container(
    title="",
    controls=[
        vm.Filter(
            column="date_of_loss",
            selector=vm.DatePicker(
                title="Date of loss",
                range=True,
            ),
        ),
        vm.Filter(column="routing_recommendations", selector=vm.Dropdown(title="Routing recommendations")),
        vm.Filter(column="current_adjuster", selector=vm.Dropdown(title="Current adjuster")),
        vm.Filter(column="ai_flags", selector=vm.Dropdown(title="AI flags")),
        vm.Filter(column="last_transaction", selector=vm.Dropdown(title="Last transaction")),
    ],
    components=[
        vm.Figure(
            id="claim_kpi_card_0",
            figure=claim_kpi_card(data_frame=claim_cases_df, row_index=0),
        ),
        vm.Figure(
            id="claim_kpi_card_1",
            figure=claim_kpi_card(data_frame=claim_cases_df, row_index=1),
        ),
        vm.Figure(
            id="claim_kpi_card_2",
            figure=claim_kpi_card(data_frame=claim_cases_df, row_index=2),
        ),
    ],
    layout=vm.Grid(grid=[[0, 1, 2]]),
)

claim_cases_page = vm.Page(title="Claim cases", components=[claim_cases_container])

# --- Fake data for Claim #486986 detail page ---
claim_486986_building_df = pd.DataFrame(
    [
        {
            "Source": "Policy documentation",
            "Age of the building": 5,
            "Owner": "Hotel chain",
            "Building occupancy, sq m": 3800,
            "Building purpose": "Hotel",
            "Jurisdiction": "Austin County, TX",
        },
        {
            "Source": "Loss adjuster report",
            "Age of the building": 50,
            "Owner": "Hotel chain",
            "Building occupancy, sq m": 4000,
            "Building purpose": "Hotel",
            "Jurisdiction": "Austin County, TX",
        },
    ]
)

claim_486986_kpi_lead = pd.DataFrame([{"value": "Lead"}])
claim_486986_kpi_share = pd.DataFrame([{"value": 10}])
claim_486986_kpi_deductible = pd.DataFrame([{"value": 100_000}])
claim_486986_kpi_insured = pd.DataFrame([{"value": 2_500_000}])
claim_486986_kpi_reserve = pd.DataFrame([{"value": 1_650_000}])
claim_486986_kpi_limit = pd.DataFrame([{"value": 2_000_000}])

# --- Fake data for Claim #901061 detail page (flood / warehouse / retail) ---
claim_901061_building_df = pd.DataFrame(
    [
        {
            "Source": "Policy documentation",
            "Age of the building": 12,
            "Owner": "Retail chain",
            "Building occupancy, sq m": 12000,
            "Building purpose": "Warehouse",
            "Jurisdiction": "Harris County, TX",
        },
        {
            "Source": "Loss adjuster report",
            "Age of the building": 12,
            "Owner": "Retail chain",
            "Building occupancy, sq m": 12500,
            "Building purpose": "Warehouse",
            "Jurisdiction": "Harris County, TX",
        },
    ]
)
claim_901061_kpi_lead = pd.DataFrame([{"value": "Follow"}])
claim_901061_kpi_share = pd.DataFrame([{"value": 25}])
claim_901061_kpi_deductible = pd.DataFrame([{"value": 250_000}])
claim_901061_kpi_insured = pd.DataFrame([{"value": 3_200_000}])
claim_901061_kpi_reserve = pd.DataFrame([{"value": 2_800_000}])
claim_901061_kpi_limit = pd.DataFrame([{"value": 4_000_000}])

# --- Fake data for Claim #996616 detail page (water / restaurant) ---
claim_996616_building_df = pd.DataFrame(
    [
        {
            "Source": "Policy documentation",
            "Age of the building": 8,
            "Owner": "Restaurant group",
            "Building occupancy, sq m": 450,
            "Building purpose": "Restaurant",
            "Jurisdiction": "Dallas County, TX",
        },
        {
            "Source": "Loss adjuster report",
            "Age of the building": 8,
            "Owner": "Restaurant group",
            "Building occupancy, sq m": 450,
            "Building purpose": "Restaurant",
            "Jurisdiction": "Dallas County, TX",
        },
    ]
)
claim_996616_kpi_lead = pd.DataFrame([{"value": "Lead"}])
claim_996616_kpi_share = pd.DataFrame([{"value": 5}])
claim_996616_kpi_deductible = pd.DataFrame([{"value": 50_000}])
claim_996616_kpi_insured = pd.DataFrame([{"value": 480_000}])
claim_996616_kpi_reserve = pd.DataFrame([{"value": 420_000}])
claim_996616_kpi_limit = pd.DataFrame([{"value": 500_000}])


def _policy_coverage_container_486986():
    """Policy coverage check section for claim 486986 (fire / hotel)."""
    return vm.Container(
        title="Policy coverage check",
        layout=vm.Grid(grid=[[0, 1, 2]]),
        components=[
            vm.Container(
                title="",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Text(text="**Results**"),
                    vm.Text(
                        text="6/6 checks passed – the reported loss is likely covered.",
                        extra={"style": {"color": "var(--bs-success)"}},
                    ),
                    vm.Container(
                        title="",
                        components=[
                            vm.Button(text="Download report", variant="outlined", icon="download"),
                            vm.Button(text="Validate check", icon="check_circle"),
                        ],
                        layout=vm.Flex(direction="row"),
                    ),
                    vm.Text(text="**Policy coverage flags**"),
                    vm.Card(
                        text="Cause of loss is covered",
                        extra={"style": {"borderLeft": "4px solid var(--bs-primary)", "padding": "0.5rem"}},
                    ),
                    vm.Container(
                        title="Remaining flags",
                        collapsed=True,
                        components=[
                            vm.Card(
                                text="Property Insured matches schedule", extra={"style": {"padding": "0.25rem 0.5rem"}}
                            ),
                            vm.Card(text="No wear and tear exclusion", extra={"style": {"padding": "0.25rem 0.5rem"}}),
                            vm.Card(
                                text="Fire/explosion peril confirmed", extra={"style": {"padding": "0.25rem 0.5rem"}}
                            ),
                            vm.Card(text="Indemnity basis verified", extra={"style": {"padding": "0.25rem 0.5rem"}}),
                        ],
                        layout=vm.Flex(direction="column"),
                    ),
                ],
            ),
            vm.Container(
                title="Reasoning",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Text(
                        text="According to the Policy wording Company agrees to indemnify the Insured in respect of "
                        "physical loss or destruction of or damage to the Property Insured described in the Schedule, "
                        "caused by **fire**, lightning, or explosion. "
                        "Damage arising from wear and tear, gradual deterioration, mechanical or electrical breakdown "
                        "not resulting in fire is excluded. The reported cause (electrical fire in kitchen) falls "
                        "within cover; exclusions do not apply."
                    ),
                ],
            ),
            vm.Container(
                title="Sources & Evidence",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Button(text="", icon="download", variant="outlined"),
                    vm.Text(text="Page 6 / 18 · Zoom 100%"),
                    vm.Card(
                        text="*Document viewer placeholder – policy schedule and loss adjuster report.*",
                        extra={
                            "style": {
                                "minHeight": "200px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                            }
                        },
                    ),
                ],
            ),
        ],
    )


def _policy_coverage_container_901061():
    """Policy coverage check section for claim 901061 (flood / warehouse)."""
    return vm.Container(
        title="Policy coverage check",
        layout=vm.Grid(grid=[[0, 1, 2]]),
        components=[
            vm.Container(
                title="",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Text(text="**Results**"),
                    vm.Text(
                        text="5/6 checks passed – flood endorsement and limits confirmed.",
                        extra={"style": {"color": "var(--bs-success)"}},
                    ),
                    vm.Container(
                        title="",
                        components=[
                            vm.Button(text="Download report", variant="outlined", icon="download"),
                            vm.Button(text="Validate check", icon="check_circle"),
                        ],
                        layout=vm.Flex(direction="row"),
                    ),
                    vm.Text(text="**Policy coverage flags**"),
                    vm.Card(
                        text="Flood zone coverage verified",
                        extra={"style": {"borderLeft": "4px solid var(--bs-primary)", "padding": "0.5rem"}},
                    ),
                    vm.Container(
                        title="Remaining flags",
                        collapsed=True,
                        components=[
                            vm.Card(
                                text="Building purpose (warehouse) covered",
                                extra={"style": {"padding": "0.25rem 0.5rem"}},
                            ),
                            vm.Card(text="Subrogation clause noted", extra={"style": {"padding": "0.25rem 0.5rem"}}),
                            vm.Card(
                                text="Business interruption within limits",
                                extra={"style": {"padding": "0.25rem 0.5rem"}},
                            ),
                        ],
                        layout=vm.Flex(direction="column"),
                    ),
                ],
            ),
            vm.Container(
                title="Reasoning",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Text(
                        text="The policy includes a **flood endorsement** for the insured premises. Loss caused by "
                        "flood following storm is covered subject to the flood sub-limit. Exclusions for gradual "
                        "water ingress and lack of maintenance do not apply to this sudden storm event. "
                        "Reserve recommendation is within the policy limit and co-insurance is satisfied."
                    ),
                ],
            ),
            vm.Container(
                title="Sources & Evidence",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Button(text="", icon="download", variant="outlined"),
                    vm.Text(text="Page 4 / 12 · Zoom 100%"),
                    vm.Card(
                        text="*Document viewer placeholder – flood endorsement and loss report.*",
                        extra={
                            "style": {
                                "minHeight": "200px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                            }
                        },
                    ),
                ],
            ),
        ],
    )


def _policy_coverage_container_996616():
    """Policy coverage check section for claim 996616 (water / restaurant)."""
    return vm.Container(
        title="Policy coverage check",
        layout=vm.Grid(grid=[[0, 1, 2]]),
        components=[
            vm.Container(
                title="",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Text(text="**Results**"),
                    vm.Text(
                        text="6/6 checks passed – water damage and burst pipe covered.",
                        extra={"style": {"color": "var(--bs-success)"}},
                    ),
                    vm.Container(
                        title="",
                        components=[
                            vm.Button(text="Download report", variant="outlined", icon="download"),
                            vm.Button(text="Validate check", icon="check_circle"),
                        ],
                        layout=vm.Flex(direction="row"),
                    ),
                    vm.Text(text="**Policy coverage flags**"),
                    vm.Card(
                        text="Cause of loss (burst pipe) is covered",
                        extra={"style": {"borderLeft": "4px solid var(--bs-primary)", "padding": "0.5rem"}},
                    ),
                    vm.Container(
                        title="Remaining flags",
                        collapsed=True,
                        components=[
                            vm.Card(
                                text="Sudden and accidental damage", extra={"style": {"padding": "0.25rem 0.5rem"}}
                            ),
                            vm.Card(text="No gradual damage exclusion", extra={"style": {"padding": "0.25rem 0.5rem"}}),
                            vm.Card(text="Property Insured matches", extra={"style": {"padding": "0.25rem 0.5rem"}}),
                            vm.Card(text="STP eligible", extra={"style": {"padding": "0.25rem 0.5rem"}}),
                        ],
                        layout=vm.Flex(direction="column"),
                    ),
                ],
            ),
            vm.Container(
                title="Reasoning",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Text(
                        text="Policy covers **physical damage** to the Property Insured caused by accidental discharge "
                        "or leakage of water. Burst pipe due to corrosion is a sudden event; gradual deterioration "
                        "exclusion does not apply. Cause and scope are clearly documented; no liability dispute. "
                        "Claim meets criteria for straight-through processing."
                    ),
                ],
            ),
            vm.Container(
                title="Sources & Evidence",
                layout=vm.Flex(direction="column"),
                components=[
                    vm.Button(text="", icon="download", variant="outlined"),
                    vm.Text(text="Page 2 / 8 · Zoom 100%"),
                    vm.Card(
                        text="*Document viewer placeholder – policy wording and repair invoice.*",
                        extra={
                            "style": {
                                "minHeight": "200px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                            }
                        },
                    ),
                ],
            ),
        ],
    )


claim_detail_486986_page = vm.Page(
    title="Claim #486986",
    path="/claim-486986",
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [2, 3, 4, 5, 6, 7],
            [8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8],
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
        ],
        row_min_height="150px",
    ),
    components=[
        vm.Container(
            title="",
            components=[
                vm.Text(
                    text="**Claim ID: #486986** Fire damage in a hotel belonging to a large hotel chain",
                ),
                vm.Container(
                    title="",
                    components=[
                        vm.Card(
                            text="Risky jurisdiction",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Advance payment request",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Information inconsistencies",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Fraud potential",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Subrogation",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="**Status:** Ongoing",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="**Recommendation:** Band B",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                    ],
                    layout=vm.Flex(direction="row"),
                ),
            ],
            layout=vm.Flex(direction="column"),
        ),
        vm.AgGrid(figure=dash_ag_grid(data_frame=claim_486986_building_df)),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_486986_kpi_lead,
                value_column="value",
                title="Lead or follow?",
                icon="description",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_486986_kpi_share,
                value_column="value",
                title="Company share",
                value_format="{value}%",
                icon="percent",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_486986_kpi_deductible,
                value_column="value",
                title="Any other peril deductible",
                value_format="$ {value:,.0f}",
                icon="payments",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_486986_kpi_insured,
                value_column="value",
                title="Insured request",
                value_format="$ {value:,.0f}",
                icon="payments",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_486986_kpi_reserve,
                value_column="value",
                title="Reserve recommendation from loss adjuster report",
                value_format="$ {value:,.0f}",
                icon="search",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_486986_kpi_limit,
                value_column="value",
                title="Policy limit",
                value_format="$ {value:,.0f}",
                icon="schedule",
            )
        ),
        vm.Card(
            text="""
            **Cause of Loss:** Electrical fire in the kitchen due to deep fryer fault

            **Scope and Extent of Damage:** Severe damage to the kitchen, restaurant,
            banquet fall; smoke/water damage to 15 guest rooms(out of 80)

            **Coverage and Liability Analysis:** Loss falls within policy coverage; no exclusions apply
            """
        ),
        _policy_coverage_container_486986(),
    ],
)

claim_detail_901061_page = vm.Page(
    title="Claim #901061",
    path="/claim-901061",
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [2, 3, 4, 5, 6, 7],
            [8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8],
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
        ],
        row_min_height="150px",
    ),
    components=[
        vm.Container(
            title="",
            components=[
                vm.Text(
                    text="**Claim ID: #901061** Flood damage in a warehouse owned by a retail chain",
                ),
                vm.Container(
                    title="",
                    components=[
                        vm.Card(
                            text="High-value claim",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Multiple locations",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Business interruption",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Subrogation",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="**Status:** Under review",
                            extra={"style": {"backgroundColor": "#cfe2ff", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="**Recommendation:** Band A",
                            extra={"style": {"backgroundColor": "#e9ecef", "padding": "0.25rem 0.5rem"}},
                        ),
                    ],
                    layout=vm.Flex(direction="row"),
                ),
            ],
            layout=vm.Flex(direction="column"),
        ),
        vm.AgGrid(figure=dash_ag_grid(data_frame=claim_901061_building_df)),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_901061_kpi_lead,
                value_column="value",
                title="Lead or follow?",
                icon="description",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_901061_kpi_share,
                value_column="value",
                title="Company share",
                value_format="{value}%",
                icon="percent",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_901061_kpi_deductible,
                value_column="value",
                title="Any other peril deductible",
                value_format="$ {value:,.0f}",
                icon="payments",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_901061_kpi_insured,
                value_column="value",
                title="Insured request",
                value_format="$ {value:,.0f}",
                icon="payments",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_901061_kpi_reserve,
                value_column="value",
                title="Reserve recommendation from loss adjuster report",
                value_format="$ {value:,.0f}",
                icon="search",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_901061_kpi_limit,
                value_column="value",
                title="Policy limit",
                value_format="$ {value:,.0f}",
                icon="schedule",
            )
        ),
        vm.Card(
            text="""
            **Cause of Loss:** Flood following severe storm; warehouse located in designated flood zone.

            **Scope and Extent of Damage:** Significant water damage to inventory and equipment;
            structural damage to loading bay; business interruption estimated at 6 weeks.

            **Coverage and Liability Analysis:** Flood coverage under separate endorsement;
            subrogation potential against local authority regarding drainage.
            """
        ),
        _policy_coverage_container_901061(),
    ],
)

# --- Claim #996616 detail page (same structure as #486986, different data) ---
claim_detail_996616_page = vm.Page(
    title="Claim #996616",
    path="/claim-996616",
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [2, 3, 4, 5, 6, 7],
            [8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8],
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
        ],
        row_min_height="150px",
    ),
    components=[
        vm.Container(
            title="",
            components=[
                vm.Text(
                    text="**Claim ID: #996616** Water damage in a restaurant caused by a burst pipe",
                ),
                vm.Container(
                    title="",
                    components=[
                        vm.Card(
                            text="Quick settlement",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="Single location",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="No subrogation",
                            extra={"style": {"backgroundColor": "#fff3cd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="**Status:** Closed",
                            extra={"style": {"backgroundColor": "#d1e7dd", "padding": "0.25rem 0.5rem"}},
                        ),
                        vm.Card(
                            text="**Recommendation:** STP",
                            extra={"style": {"backgroundColor": "#e9ecef", "padding": "0.25rem 0.5rem"}},
                        ),
                    ],
                    layout=vm.Flex(direction="row"),
                ),
            ],
            layout=vm.Flex(direction="column"),
        ),
        vm.AgGrid(figure=dash_ag_grid(data_frame=claim_996616_building_df)),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_996616_kpi_lead,
                value_column="value",
                title="Lead or follow?",
                icon="description",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_996616_kpi_share,
                value_column="value",
                title="Company share",
                value_format="{value}%",
                icon="percent",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_996616_kpi_deductible,
                value_column="value",
                title="Any other peril deductible",
                value_format="$ {value:,.0f}",
                icon="payments",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_996616_kpi_insured,
                value_column="value",
                title="Insured request",
                value_format="$ {value:,.0f}",
                icon="payments",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_996616_kpi_reserve,
                value_column="value",
                title="Reserve recommendation from loss adjuster report",
                value_format="$ {value:,.0f}",
                icon="search",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=claim_996616_kpi_limit,
                value_column="value",
                title="Policy limit",
                value_format="$ {value:,.0f}",
                icon="schedule",
            )
        ),
        vm.Card(
            text="""
            **Cause of Loss:** Burst pipe in ceiling void above kitchen; pipe corrosion and age-related failure.

            **Scope and Extent of Damage:** Water damage to kitchen and dining area; ceiling collapse;
                equipment damage. Restaurant closed for 2 weeks.

            **Coverage and Liability Analysis:** Covered under standard water damage provisions;
                no liability dispute; STP (straight-through processing) recommended.
            """
        ),
        _policy_coverage_container_996616(),
    ],
)

# --- Navigation ---
navigation = vm.Navigation(
    nav_selector=vm.NavBar(
        items=[
            vm.NavLink(pages=["Claim cases"], label="Claim cases"),
            vm.NavLink(pages=["Claim #486986"], label="Claim #486986"),
            vm.NavLink(pages=["Claim #901061"], label="Claim #901061"),
            vm.NavLink(pages=["Claim #996616"], label="Claim #996616"),
        ],
        position="top",
    ),
)

dashboard = vm.Dashboard(
    pages=[
        claim_cases_page,
        claim_detail_486986_page,
        claim_detail_901061_page,
        claim_detail_996616_page,
    ],
    navigation=navigation,
    title="Claim cases",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
