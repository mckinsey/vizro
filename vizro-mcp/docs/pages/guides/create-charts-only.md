# Create standalone charts without a Vizro dashboard

If you don't want to create an entire Vizro dashboard, you can still use Vizro-MCP to create the code for a single chart. If you're not sure what kind of chart you want, check out the [Vizro Visual Vocabulary](https://huggingface.co/spaces/vizro/demo-visual-vocabulary) for ideas.

In Claude Desktop or Cursor, the **easiest** way to create a Vizro chart is to choose the [`create_vizro_chart` template](./use-prompt-templates.md) and just send the prompt. This will create a simple chart that you can alter. Take it from there!

Alternatively, you can just ask Vizro-MCP through a prompt. For example:

> _Create a scatter plot based on the iris dataset._

> _Create a bar chart based on `<insert absolute file path or public URL>` data._
