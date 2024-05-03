# Explore VizroAI

In this tutorial, we walk through the process of creating some of the more complex plotly charts. The examples use data from the [plotly express data package](https://plotly.com/python-api-reference/generated/plotly.express.data.html). 

## Create Polar Bar Chart with VizroAI

Polar Bar Charts are mostly used to visualize wind speed and direction at a given location, and with VizroAI you can create one with few simple lines of code. 

!!! example "Polar Bar Chart"

    === "Code for the cell"
        ```py
        import vizro_ai
        from vizro_ai import VizroAI
        import plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()
        
        df = px.data.wind()

        vizro_ai = VizroAI(model="gpt-4-0613")
        vizro_ai.plot(df, 
                      """Describe wind frequency and direction using bar_polar chart. 
                         Increase the width and height of the figure. 
                         Improve layout by placing title to the left. Show legend""", explain=True) 

        ```
    === "Result chart"
        [![VizroAIChart]][VizroAIChart]

    [VizroAIChart]: ../../assets/tutorials/chart/polar_bar_chart.png

