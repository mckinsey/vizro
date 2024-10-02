# Vizro-AI

Vizro-AI uses generative AI to extend [Vizro](https://vizro.readthedocs.io) so you can use instructions in English, or other languages, to effortlessly create interactive charts and dashboards.

By using Vizro's themes, you can incorporate design best practices by default. If you're new to coding, Vizro-AI simplifies both the creation of charts with [Plotly](https://plotly.com/python/) and their layout upon an interactive and easily-distributed dashboard.

Even if you are an experienced data practitioner, Vizro-AI optimizes how you create visually appealing layouts to present detailed insights about your data.

<img src=".//assets/readme/readme_animation.gif" alt="Gif to demonstrate vizro-ai">

Below is a table of the Vizro components currently supported by Vizro-AI. This list is not exhaustive, and we are actively working on adding more features to Vizro-AI.

| Feature type         | Feature                                                                                                                | Availability |
|----------------------|------------------------------------------------------------------------------------------------------------------------|--------------|
| **Components**       | [Graph](https://vizro.readthedocs.io/en/stable/pages/user-guides/graph/)                                               | ✔            |
|                      | [AG Grid](https://vizro.readthedocs.io/en/stable/pages/user-guides/table/#ag-grid)                                     | ✔            |
|                      | [Card](https://vizro.readthedocs.io/en/stable/pages/user-guides/card-button/)                                          | ✔            |
|                      | [Button](https://vizro.readthedocs.io/en/stable/pages/user-guides/card-button/)                                        | ✖            |
|                      | [Tabs](https://vizro.readthedocs.io/en/stable/pages/user-guides/tabs/)                                                 | ✖            |
|                      | [Containers](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/)                                      | ✖            |
| **Controls**         | [Filter](https://vizro.readthedocs.io/en/stable/pages/user-guides/filters/)                                            | ✔            |
|                      | [Parameter](https://vizro.readthedocs.io/en/stable/pages/user-guides/parameters/)                                      | ✖            |
| **Navigation**       | [Default navigation](https://vizro.readthedocs.io/en/stable/pages/user-guides/navigation/#use-the-default-navigation)  | ✔            |
|                      | [Custom navigation](https://vizro.readthedocs.io/en/stable/pages/user-guides/navigation/#customize-the-navigation-bar) | ✖            |
| **Layout**           | [Layout](https://vizro.readthedocs.io/en/stable/pages/user-guides/layouts/)                                            | ✔            |
| **Dashboard header** | [Dashboard title](https://vizro.readthedocs.io/en/stable/pages/user-guides/dashboard/)                                 | ✔            |
|                      | [Logo](https://vizro.readthedocs.io/en/stable/pages/user-guides/dashboard/)                                            | ✖            |

If a feature you need for your dashboard isn't currently supported by Vizro-AI you can [retrieve the dashboard code](https://vizro.readthedocs.io/projects/vizro-ai/en/vizro-ai-0.2.3/pages/user-guides/retrieve-dashboard-code/) and add the missing components before running the dashboard.

<div class="grid cards" markdown>

-   :fontawesome-solid-forward-fast:{ .lg .middle } __New to Vizro-AI?__

    ---

    [:octicons-arrow-right-24: Install Vizro-AI](pages/user-guides/install.md) </br>
    [:octicons-arrow-right-24: Quickstart chart generation](pages/tutorials/quickstart.md) </br>
    [:octicons-arrow-right-24: Quickstart dashboard generation](pages/tutorials/quickstart-dashboard.md) </br>

- :fontawesome-solid-keyboard:{ .lg .middle } __Get hands-on__

    ---

    [:octicons-arrow-right-24: How to run Vizro-AI](pages/user-guides/run-vizro-ai.md)</br>
    [:octicons-arrow-right-24: Model usage](pages/user-guides/customize-vizro-ai.md)</br>
    [:octicons-arrow-right-24: Create advanced charts](pages/user-guides/create-advanced-charts.md)</br>
    [:octicons-arrow-right-24: Add charts to a dashboard](pages/user-guides/add-generated-chart-usecase.md)</br>
    [:octicons-arrow-right-24: Generate a complex dashboard](pages/user-guides/create-complex-dashboard.md)</br>
    [:octicons-arrow-right-24: Retrieve code for a generated dashboard](pages/user-guides/retrieve-dashboard-code.md)

- :material-format-font:{ .lg .middle } __Find out more__

    ---

    [:octicons-arrow-right-24: FAQs](pages/explanation/faq.md) </br>
    [:octicons-arrow-right-24: Safeguard dynamic code execution](pages/explanation/safeguard.md) </br>
    [:octicons-arrow-right-24: Guidelines for use of LLMs](pages/explanation/safety-in-vizro-ai.md)

- :fontawesome-solid-chart-column:{ .lg .middle } __Vizro__

    ---

    [:octicons-arrow-right-24: Vizro documentation](https://vizro.readthedocs.io/)


</div>

!!! notice "Notice"

    Review the [disclaimer](pages/explanation/disclaimer.md)
    before using the `vizro-ai` package.

    Users must connect to large language models (LLMs) to use Vizro-AI.
    Please review our [guidelines on the use of LLMs](pages/explanation/safety-in-vizro-ai.md)
    and the required [safeguarding for dynamic code evaluation](pages/explanation/safeguard.md).
