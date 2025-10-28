# How to use local or remote data

You can ask the LLM to create specific dashboards based on local or remote data if you already have an idea of what you want.

## Local data

When you are prompting to generate the dashboard code, most MCP hosts will allow you to upload your data into the prompt. Otherwise, you can tell the LLM the filepath of the data it is working with.

### How to set up PyCafe to run the generated dashboard code

PyCafe can only run the dashboard code if it can access the data it requires. The MCP host will not open your code in PyCafe if your data is stored locally. However, if you like using PyCafe to review the work in progress, you can prompt the MCP host to open your code in PyCafe. It will open PyCafe with the code, but the dashboard will not display correctly, as shown below. 

You can then share the data to the PyCafe project by upload as shown. This is the most straightforward way to run a project, but **do not share private data!**.

![Install Vizro-MCP with uv](../../assets/images/looping-data-upload.gif)

### How to run generated code within a Python virtual environment

If your data is private or you prefer not to upload it to PyCafe, you can run the code that Vizro-MCP generates for you locally. Often, the MCP host will guide you in how to do this. 

1. Save the generated code to a file named, for example `app.py`, ideally in the same folder as the data you are using, as this simplifies the path in the code that accesses the data.
2. Modify the path to the data in the code to point from `app.py` to the correct location of the data.
3. Within your terminal, open a Python virtual environment that has [Vizro installed into it](https://vizro.readthedocs.io/en/stable/pages/user-guides/install/#verifying-the-installation).
4. Navigate to the same folder in the terminal that you have stored `app.py`.
5. Type `python app.py` to run the code. 

This sounds like a complex process but if you use an MCP host like Cursor or Microsoft VS Code, it will guide you. You can even prompt the host with the steps above and ask it to run through them for you.

## Remote data

Example prompts for using remote data could be:

> _Create a Vizro dashboard with one page, a scatter chart, and a filter based on `<insert absolute file path or public URL>` data._

> _Create a simple two page Vizro dashboard, with first page being a correlation analysis of `<insert absolute file path or public URL>` data, and the second page being a map plot of `<insert absolute file path or public URL>` data_

You can find a set of sample CSVs to try out in the [Plotly repository](https://github.com/plotly/datasets/tree/master).

You can even ask for dashboard code without providing data:

> _Create a Vizro dashboard with one page, a scatter chart, and a filter._

In general, it helps to specify Vizro in the prompt and to keep it as precise (and simple) as possible.
