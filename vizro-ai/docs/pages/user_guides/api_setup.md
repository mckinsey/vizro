# How to setup the API
This guide shows how to set up the API key and other environment variables (e.g.,
base URL) so that you can seamlessly communicate with the Large Language Model (LLM).

Users are recommended to review the third party API key section of the [disclaimer](../explanation/disclaimer.md) documentation.

## OpenAI
To communicate with the OpenAI API, you need to provide the API key. Additionally, you
might need to provide the base URL if you are using a custom OpenAI resource endpoint.

### Setup the API key
There are two common ways to set up the API key in a development environment.

__Method 1 (recommended): Set up the API key for a single project__

To make the API key available for a specific project, you can set it in a `.env`
file. Then, you can load the API key from the `.env` file in your development environment.
Avoid committing the `.env` file if you are using a version control system such as Git.
You can add `.env` to your `.gitignore` file to avoid committing it.

!!! example "API key setup and usage"
    === ".env"
        ```text
        OPENAI_API_KEY=<your API key>
        ```
    === "Jupyter Notebook"
        ```python
        from dotenv import load_dotenv
        load_dotenv()
        ```

__Method 2: Set up the API key as an environment variable for all projects__

To make the API key available for all projects, you can set it as an environment
variable. Please refer to the section ["Setup your API key for all projects"](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key?context=python)
in the OpenAI documentation. (It is under the dropdown of Step 2: Setup your API key).

It provides step-by-step instructions for setting up the API key as an environment
variable, on operating systems including Windows and MacOS.


### Setup the Base URL (optional)
The API Base URL used for the OpenAI connector is set to `https://api.openai.com/v1` by default.
If you are using a custom API endpoint, you can set it as an environment variable.

This is usually for organizational users. For example, if your organization has designed API gateway,
you can change the API endpoint here.

You can follow the approach in the section "Setup your API key for all projects
(recommended)" to add the environment variable `OPENAI_API_BASE` to your environment.

!!! example "API Base setup and usage"
    === ".env"
        ```text
        OPENAI_API_BASE=<your API base>
        ```
