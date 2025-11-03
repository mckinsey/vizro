# Create Vizro Dashboards with Gen AI

This tutorial shows how to build and share a Vizro dashboard using generative AI.


Ensure VS Code setup to use Vizro-MCP

### Create a workspace
In VS Code, select **File > Open Folder…**, create a new folder (e.g., `lighting`), then click **Open**.  
**VIDEO**

### Open chat view
Open the Chat view.  
Use **Agent mode** with Claude Sonnet 4.  
**VIDEO**

---

## Create a blank dashboard

Submit this prompt in chat:
> “Let’s use Vizro-MCP to generate a blank dashboard with one page and three tabs. Generate the code and save it to app.py in the workspace. Don’t open in PyCafe.”

When complete, `app.py` appears in the Explorer.  
**VIDEO**

## Run the dashboard
Prompt:
> “Use a single command to open a terminal, navigate to the lighting directory, activate a uv virtual environment (Python 3.13), install vizro and pandas, and run app.py.”

Or run manually:
```bash
cd lighting
uv venv training --python 3.13
source training/bin/activate
uv pip install vizro pandas
python app.py
```
Open the dashboard URL shown in the terminal.  
**VIDEO**

Optional: Try the same prompt without Vizro-MCP to compare results.  
**VIDEO**

---

## Add charts with prompts

### Add a choropleth map
Prompt:
> “Use data from https://ourworldindata.org/grapher/share-of-the-population-with-access-to-electricity?overlay=download-data.  
> Add a choropleth map to tab 1 showing access to electricity in 2023 by country, with a colour gradient legend and light theme.”

**VIDEO**

If Vizro-MCP fails, type “Clear context” and retry.  
You can add example code for reference.

#### Add a year slider
Prompt:
> “Add a slider to select year 1990–2023 and update the map as it moves.”

If marks are too dense, add to `app.py`:
```python
marks={year: str(year) for year in range(1990, 2024, 5)},
```

**VIDEO**

#### Add animation and projection selector
Prompt:
> “Add animation by year and a projection selector to switch between flat and 3D globe views.”  
**VIDEO**

---

### Add a line chart

Prompt:
> “On tab 2, draw a line chart for seven countries (US, China, Brazil, India, Afghanistan, Rwanda, Haiti).  
> X = Year, Y = Access to electricity (% of population).  
> Use different colours and labels per country.  
> Add a checklist to add/remove countries.”

**VIDEO**

If scrolling through the checklist is awkward, replace it with a dropdown:
```python
vm.Filter(
  column="Entity",
  targets=["electricity_trends", "electricity_histogram"],
  selector=vm.Dropdown(
    multi=True,
    value=["United States", "China", "Brazil", "India", "Afghanistan", "Rwanda", "Haiti"],
    title="Select countries to display",
    extra={"optionHeight": 35},
  ),
),
```

**VIDEO**

**Current state summary**

| Tab | Content |
|:-|:|
| 1 | Choropleth map (1990–2023) + year slider + interactive filter |
| 2 | Line chart of electricity access + multi-select dropdown |
| 3 | Placeholder |

**IMAGE**

---

### Add an animated bar chart

Prompt:
> “Add a third tab with an animated horizontal bar chart showing electricity access by country.  
> Share the country filter with tab 2.  
> Remove legend.  
> Include all countries in every animation frame using interpolated data.”

Iterate if needed (e.g. “Make chart fit viewport”).  
**VIDEO**

---

## Share your dashboard

### Using PyCafe
1. Create a free account at [PyCafe](https://py.cafe).  
2. Create a new Vizro project.  
3. Replace default code with your `app.py`.  
4. Push project to share and get a link.

Use only public data for PyCafe (public site).  

**VIDEO**

You can also iterate your code directly in PyCafe instead of VS Code.  

Example prompt:
> “Open and run the Vizro code in PyCafe and display the results.”  
**VIDEO**

---

## 10. Conclusion and next steps
You now have a three-tab Vizro dashboard built with Vizro-MCP and shared via PyCafe.

Bug reports and feature requests: [public GitHub repo](https://github.com/mckinsey/vizro).  

**IMAGE**

---

## Tutorial summary
- Install and configure Vizro-MCP.  
- Generate a dashboard and charts using prompts.  
- Iterate visualizations and filters.  
- Share via PyCafe.  

Feedback and suggestions welcome GitHub.
