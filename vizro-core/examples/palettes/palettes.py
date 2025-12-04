QUALITATIVE_PALETTE = [
    "#00B4FF",
    "#FF9222",
    "#3949AB",
    "#FF5267",
    "#08BDBA",
    "#FDC935",
    "#689F38",
    "#976FD1",
    "#F781BF",
    "#52733E",
]
SEQUENTIAL_PALETTE = [
    "#AFE7F9",
    "#8BD0F6",
    "#6CBAEC",
    "#52A3DD",
    "#3B8DCB",
    "#2777B7",
    "#1661A2",
    "#074C8C",
    "#003875",
]
DIVERGING_PALETTE = [
    "#7D000F",
    "#981822",
    "#B22F36",
    "#C9474C",
    "#DD6065",
    "#ED7B7F",
    "#F89B9B",
    "#FCB6BA",
    "#F8D6DA",
    "#F5F6F6",
    "#AFE7F9",
    "#8BD0F6",
    "#6CBAEC",
    "#52A3DD",
    "#3B8DCB",
    "#2777B7",
    "#1661A2",
    "#074C8C",
    "#003875",
]
SEQUENTIALMINUS_PALETTE = [
    "#7D000F",
    "#981822",
    "#B22F36",
    "#C9474C",
    "#DD6065",
    "#ED7B7F",
    "#F89B9B",
    "#FCB6BA",
    "#F8D6DA",
]

"""

# Plotly Express Charts with Vizro Palettes

link to app

How to use the app: just edit `palettes.py` and the whole dashboard will update. These are currently set to the Vizro template defaults.

Read the introduction text in the app for more guidance.

## Plotly Express and trace types

Plotly Express (`px`) is the high-level wrapper for underlying Plotly Graph Objects (`go`). Everything we say here ignores `px.imshow` and deprecated `mapbox` functions, which leaves us with 35 `px` functions. These are all shown in the app.

Each `px` function has  corresponding `go` trace type, e.g. `px.Pie` corresponds to `go.Pie`. In general there's a 1:1 mapping between `px` functions and `go` trace types, but some `px` functions have the same underlying trace type (e.g. `px.area`, `px.ecdf`, `px.line`, `px.scatter` all have the same `go.Scatter` trace type).

There's another 15-20 `go` trace types that exist but are not used by any `px` functions and therefore don't appear in the app. Most of these are pretty niche and we don't see in Vizro.

## Which are the most common chart types?

These are all shown in the app apart from the `go.Sankey` and `go.Waterfall` trace types, which you can see in the visual vocabulary.

I would roughly estimate the following groups for usage in a Vizro dashboard:
* Common: `px.bar`, `px.scatter`, `px.line`, `px.area` (that's all the basic charts), `px.histogram`, `px.box`, `px.pie`
* Sometimes: `px.density_heatmap`, `px.violin`, `px.strip`, `px.scatter_geo`, `px.choropleth`, `px.scatter_map`, `px.choropleth_map`, `go.Sankey`, `go.Waterfall`
* Rare: `px.sunburst`, `px.treemap`, `px.icicle`, `px.funnel`, `px.funnel_area`, `px.density_contour`, `px.scatter_matrix`, `px.ecdf`, `px.timeline`, `px.parallel_coordinates`, `px.parallel_categories`
* Very rare: everything else

## How much control over the palettes do we have?

Our template can have the following global palettes, all defined in the pycafe app `palettes.py`. After plotly PR has been released, all of these will be used automaticallyL

* qualitative: any discrete plot. Defined in `template.layout.colorway`.
* sequential: continuous plot with all positive values. Defined in `template.layout.colorscale.sequential`.
* diverging: continuous plot with both positive and negative values. Defined in `template.layout.colorscale.diverging`. 
* sequentialminus: continuous plot with all negative values. Defined in `template.layout.colorscale.sequentialminus`.

If we want more fine-grained control then it's also possible:
* after plotly PR has been released, you can specify a qualitative palette to use in a `px` function for each trace type in `template.data.<trace_type>`. Since this is done by trace type, it constrains different `px` functions that have the same underlying trace-type (e.g. `px.line`, `px.scatter`) to have the same colours. If this is a problem then probably we can add something to plotly to distinguish these though.
* `go` trace types that don't appear in `px` (e.g. `go.Sankey`, `go.Waterfall`) can also have their own qualitative palettes already specified in `template.data`.
* weirdly you can already specify different palettes for pie, funnelarea, sunburst, icicle, treemap trace types in in `template.layout.<trace_type>colorway`.

I haven't looked into setting different continuous palettes for different trace types, but I imagine it would be possible with some modifications to plotly if it is something we want to pursue.

Remember!
* In a dashboard context we must have exactly the same palettes in dark and light themes or theme-switching will break.
* If we want to have more palettes e.g. different options for the qualitative palette, there's space in Vizro to put them, and they could be used for any plots. They would just not be used automatically but instead be manually chosen by a dashboard developer.


"""
