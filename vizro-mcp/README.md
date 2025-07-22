<!-- <a href="https://glama.ai/mcp/servers/@mckinsey/vizro">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@mckinsey/vizro/badge" />
</a> -->

# Vizro-MCP

Vizro-MCP is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server, which works alongside a LLM to help you create Vizro dashboards and charts.

<img src="docs/assets/images/vizro-mcp.gif" width="600" alt="Vizro-MCP Demo">

### Quick install

| Host                                      | Prerequisite                                                  | Link                                                                                                                                                                                                                                                                                                                                   | Notes                                                                   |
| ----------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [Cursor](https://www.cursor.com/)         | [uv](https://docs.astral.sh/uv/getting-started/installation/) | [![Install with UVX in Cursor](https://img.shields.io/badge/Cursor-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://cursor.com/install-mcp?name=vizro-mcp&config=eyJjb21tYW5kIjoidXZ4IHZpenJvLW1jcCJ9)                                                                                                 |                                                                         |
| [VS Code](https://code.visualstudio.com/) | [uv](https://docs.astral.sh/uv/guides/tools/)                 | [![Install with UVX in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=vizro-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22vizro-mcp%22%5D%7D)                                             |                                                                         |
| [Cursor](https://www.cursor.com/)         | [Docker](https://www.docker.com/get-started/)                 | [![Install with Docker in Cursor](https://img.shields.io/badge/Cursor-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://cursor.com/install-mcp?name=vizro-mcp&config=eyJjb21tYW5kIjoiZG9ja2VyIHJ1biAtaSAtLXJtIG1jcC92aXpybyJ9)                                                                          | For local data access, [mount your data directory](#setup-instructions) |
| [VS Code](https://code.visualstudio.com/) | [Docker](https://www.docker.com/get-started/)                 | [![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=vizro-mcp&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22mcp%2Fvizro%22%5D%7D) | For local data access, [mount your data directory](#setup-instructions) |

## Disclaimers

<details>
<summary><strong>Transparency and trust</strong></summary>


MCP servers are a relatively new concept, and it is important to be transparent about what the tools are capable of so you can make an informed choice as a user. Overall, the Vizro MCP server only reads data, and never writes, deletes or modifies any data on your machine.

In general the most critical part of the process is the `load_and_analyze_data` tool. This tool, running on your machine, will load local or remote data into a pandas DataFrame and provide a detailed analysis of its structure and content. It only uses `pd.read_xxx`, so in general there is no need to worry about privacy or data security. However, you should only run Vizro-MCP locally, not as a hosted server, because there is currently no authentication to manage access.

The second most critical part is the `validate_dashboard_config` tool. This tool will attempt to instantiate the Vizro model configuration and return the Python code and visualization link for valid configurations. If the configuration is valid, it will also return and attempt to open a link to a live preview of the dashboard, which will take you to PyCafe). If you don't want to open the link, you can tell the LLM to not do so.
</details>

<details>
<summary><strong>Third party API</strong></summary>

Users are responsible for anything done via their host LLM application.

Users are responsible for procuring any and all rights necessary to access any third-party generative AI tools and for complying with any applicable terms or conditions thereof.

Users are wholly responsible for the use and security of the third-party generative AI tools and of Vizro.

</details>

<details>
<summary><strong>User acknowledgments</strong></summary>

Users acknowledge and agree that:

Any results, options, data, recommendations, analyses, code, or other information (“Outputs”) generated by any third-party generative AI tools (“GenAI Tools”) may contain some inaccuracies, biases, illegitimate, potentially infringing, or otherwise inappropriate content that may be mistaken, discriminatory, or misleading.

McKinsey & Company:

(i) expressly disclaims the accuracy, adequacy, timeliness, reliability, merchantability, fitness for a particular purpose, non-infringement, safety or completeness of any Outputs,

(ii) shall not be liable for any errors, omissions, or other defects in, delays or interruptions in such Outputs, or for any actions taken in reliance thereon, and

(iii) shall not be liable for any alleged violation or infringement of any right of any third party resulting from the users’ use of the GenAI Tools and the Outputs.

The Outputs shall be verified and validated by the users and shall not be used without human oversight and as a sole basis for making decisions impacting individuals.

Users remain solely responsible for the use of the Output, in particular, the users will need to determine the level of human oversight needed to be given the context and use case, as well as for informing the users’ personnel and other affected users about the nature of the GenAI Output. Users are also fully responsible for their decisions, actions, use of Vizro and Vizro-MCP and compliance with applicable laws, rules, and regulations, including but not limited to confirming that the Outputs do not infringe any third-party rights.

</details>

<details>
<summary><strong>Warning and safety usage for generative AI models</strong></summary>

Vizro-MCP is used by generative AI models because large language models (LLMs) represent significant advancements in the AI field. However, as with any powerful tool, there are potential risks associated with connecting to a generative AI model.

We recommend users research and understand the selected model before using Vizro-MCP.

Users are encouraged to treat AI-generated content as supplementary, always apply human judgment, approach with caution, review the relevant disclaimer page, and consider the following:

<ol>
<li>Hallucination and misrepresentation</li>
Generative models can potentially generate information while appearing factual, being entirely fictitious or misleading.

The vendor models might lack real-time knowledge or events beyond its last updates. Vizro-MCP output may vary and you should always verify critical information. It is the user's responsibility to discern the accuracy, consistent, and reliability of the generated content.

<li>Unintended and sensitive output</li>
The outputs from these models can be unexpected, inappropriate, or even harmful. Users as human in the loop is an essential part. Users must check and interpret the final output. It is necessary to approach the generated content with caution, especially when shared or applied in various contexts.

<li>Data privacy</li>
Your data is sent to model vendors if you connect to LLMs via their APIs. For example, if you connect to the model from OpenAI, your data will be sent to OpenAI via their API. Users should be cautious about sharing or inputting any personal or sensitive information.

<li>Bias and fairness</li>
Generative AI can exhibit biases present in their training data. Users need to be aware of and navigate potential biases in generated outputs and be cautious when interpreting the generated content.

<li>Malicious use</li>
These models can be exploited for various malicious activities. Users should be cautious about how and where they deploy and access such models.
</ol>
It's crucial for users to remain informed, cautious, and ethical in their applications.

</details>
