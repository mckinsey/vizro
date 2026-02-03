"""Dev app to try things out - Security Dashboard inspired."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.figures import kpi_card, kpi_card_reference
import pandas as pd

# Sample data for security metrics
security_issues = pd.DataFrame({
    "Severity": ["Critical", "High", "Medium", "Low"],
    "Count": [2, 263, 1994, 641],
    "Trend": ["-25%", "-40%", "+33%", "-11%"]
})

top_issues = pd.DataFrame({
    "Rule": [
        "OpenAI Service public network access",
        "Admin principals inactive over 90 days",
        "SF - Endpoint Protection - Microsoft Defender ATP",
        "SF - Kubernetes Cluster - Wiz Sensor is missing",
        "AI Service public network access should be restricted",
        "Storage account should use customer-managed key",
        "Kubernetes API server should be private",
        "SQL databases should have vulnerability assessment",
        "Virtual machines should encrypt temp disks",
        "Network security groups should restrict inbound traffic",
    ],
    "Issues": [40, 32, 31, 14, 13, 12, 11, 10, 9, 8]
})

secrets_data = pd.DataFrame({
    "Type": ["Username/Password", "Okta Token", "JSON Web Token", "RSA Private Key", "Bearer Token"],
    "Count": [85, 65, 45, 35, 25]
})

# KPI data for secrets detection
kpi_data = pd.DataFrame({
    "Metric": ["Critical Incidents", "High Incidents", "Publicly Leaked", "Valid Secrets"],
    "Value": [45, 155, 10, 30],
    "Reference": [60, 200, 20, 50]
})

sast_data = pd.DataFrame({
    "Category": ["Security Issues", "Security Hotspots", "Security Vulnerabilities", "Dependency Risks"],
    "Critical": [4, 2, 8, 7],
    "High": [21, 18, 12, 15],
    "Medium": [40, 40, 30, 22]
})

composition_data = pd.DataFrame({
    "Severity": ["Critical", "High", "Medium"],
    "Count": [25, 75, 150]
})

lifecycle_data = pd.DataFrame({
    "Status": ["Archived/Offline", "Operate/Support", "Design/Dev/Integrate", "Ideate", "Exit/Sunset"],
    "Count": [7, 2, 5, 3, 3]
})

# Create figures

def create_bar_chart(data_frame, x, y, color_seq=None):
    return px.bar(data_frame, x=x, y=y,
                  color_discrete_sequence=color_seq or ["#1f77b4"], height=400)

def create_donut_chart(data_frame, values, names, color_seq=None):
    return px.pie(data_frame, values=values, names=names, hole=0.5,
                  color_discrete_sequence=color_seq or px.colors.qualitative.Set2, height=400)

# Page with flex layout
page = vm.Page(
    title="Security Dashboard",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        # Left column - Cloud Security
        vm.Container(
            layout=vm.Flex(),
            description="This is a description of the Cloud Security container.",
            variant="filled",
            title="Cloud Security",
            components=[
                vm.Text(
                    text="""
                    ####
                    
                    **Critical**: 2 (↓ 25%)
                    
                    **High**: 263 (↓ 40%)
                    
                    **Medium**: 1,994 (↑ 33%)
                    
                    **Low**: 641 (↓ 11%)
                    """,
                ),
                vm.AgGrid(
                    title="Top Issues (289 rules)",
                    figure=dash_ag_grid(top_issues)
                ),
            ],
        ),
        
        # Right column container
        vm.Container(
            variant="filled",
            description="This is a description of the Detection & Analysis container.",
            title="Detection & Analysis",
            layout=vm.Flex(),
            components=[
                # Secrets Detection KPIs
                vm.Container(
                    layout=vm.Flex(direction="row", wrap=True, gap="30px"),
                    components=[
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_data[kpi_data["Metric"] == "Critical Incidents"],
                                value_column="Value",
                                reference_column="Reference",
                                title="Critical Incidents",
                                icon="Warning"
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_data[kpi_data["Metric"] == "High Incidents"],
                                value_column="Value",
                                reference_column="Reference",
                                title="High Incidents",
                                icon="Error"
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_data[kpi_data["Metric"] == "Publicly Leaked"],
                                value_column="Value",
                                reference_column="Reference",
                                title="Publicly Leaked",
                                icon="Public"
                            )
                        ),
                    ],
                ),
                vm.Graph(
                    figure=create_bar_chart(secrets_data, "Type", "Count", ["#00b4d8"]),
                                           title="Top Detectors"
                ),
                
                vm.Graph(
                    figure=create_donut_chart(composition_data, "Count", "Severity",
                                          
                                             ["#ef476f", "#ffd166", "#06ffa5"]),
                                             title="Software Composition Analysis (SCA)"
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page], title="Security Dashboard")

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
