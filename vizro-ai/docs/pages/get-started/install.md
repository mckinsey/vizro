# Install Vizro-AI

In this guide you'll learn how to set up the prerequisites needed for Vizro-AI, and how to install it. You'll also find out how to verify the Vizro-AI installation succeeded, find the version of Vizro-AI, and learn how to update it.

## Prerequisites

### Python
Vizro-AI supports macOS, Linux, and Windows. It works with Python 3.9 and later. You can specify the version of Python to use with Vizro-AI when you set up a virtual environment.


### Set up a virtual environment
You should create a virtual environment for each Vizro-AI project you work on to isolate its Python dependencies from those of other projects. See the following references to learn more about [Python virtual environments](https://realpython.com/python-virtual-environments-a-primer/), [Conda virtual environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda) or [watch an explainer video about them](https://youtu.be/YKfAwIItO7M).

??? information "How to create a virtual environment for your Vizro-AI project"

    The simplest way to create a virtual environment in Python is `venv`, which is included in the Python standard library. Create a directory for your project and navigate to it. For example:

    ```bash
    mkdir vizroai-project
    cd vizroai-project
    ```

    Next, create and activate a new virtual environment in this directory with `venv`:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

    Alternatively, you might like to use [`conda` as your virtual environment manager](https://docs.conda.io/projects/conda/en/latest/user-guide/install/). Once installed, you can create and activate a virtual environment from the terminal as follows:

    ```bash
    conda create --name vizroai-environment
    conda activate vizroai-environment
    ```

### Set up access to a large language model

Use of Vizro-AI requires the use of a large language model. At present, we only support [OpenAI](https://openai.com/).

To use OpenAI with Vizro-AI you need an API key, which you can get by [creating an OpenAI account if you don't already have one](https://platform.openai.com/account/api-keys).

!!! note

    We recommend that you consult the [third-party API key section of the disclaimer documentation](../explanation/disclaimer.md) documentation.

There are two common ways to set up the API key in a development environment.

__Method 1: Set an environment variable for a single project__

To make the API key available for a single project, you can create a local `.env`
file to store it. Then, you can load the API key from that `.env` file in your development environment.

The `.env` file should look as follows (containing your key rather than `abc123`):

```text
OPENAI_API_KEY=abc123
```

By default, `vizro-ai` automatically loads the `.env` file, by searching the current directory and, if it does not find `.env`, the search continues upwards through the directory hierarchy.

If you would like to customize the `.env` file location and name, you can manually customize the search to override the default and specify the path and name of a custom `.env` file.

??? example "How to override the default location of the .`env` file:"

    ```py
    from dotenv import load_dotenv, find_dotenv
    from pathlib import Path

    # Specify the exact path to your .env file
    env_file = Path.cwd() / ".env"  # Adjust the path as needed

    # Alternatively, specify a different .env file name
    env_file = find_dotenv(".env.dev")  # Replace ".env.dev" with your file name

    # Load the specified .env file
    load_dotenv(env_file)
    ```
    Refer to [python-dotenv documentation](https://saurabh-kumar.com/python-dotenv/reference/) for further information.

!!! warning "Don't share your secret API key!"

    You should avoid committing the `.env` file to version control. You can do this for Git by adding `.env` to your `.gitignore` file.


__Method 2: Set an environment variable for all projects__

To make the OpenAI API key available for all projects, you can set it as a system environment
variable. Refer to the section ["Set up your API key for all projects"](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key?context=python)
in the OpenAI documentation. (It is under the dropdown of "Step 2: Set up your API key").

The documentation provides step-by-step instructions for setting up the API key as an environment
variable, on operating systems including Windows and MacOS.

__Set the base URL (optional)__

You might need to give the base URL if you are using a custom OpenAI resource endpoint.

The API base URL used for the OpenAI connector is set to `https://api.openai.com/v1` by default.
If you are using a custom API endpoint, for example, if your organization has a designated API gateway,
you can change the base URL by setting it as an environment variable.


Follow the approach above in Method 2 to add the environment variable `OPENAI_API_BASE` for use by all projects.


## Install Vizro

To install Vizro-AI, use [`pip`](https://pip.pypa.io/en/stable/) in your terminal window:

```bash
pip install vizro_ai
```

## Confirm a successful installation

To confirm the installation was successful, and verify the version of Vizro-AI installed, call the following. You can do this from within a Jupyter Notebook cell, or run the following as a Python script:

```py
import vizro_ai

print(vizro_ai.__version__)
```

You should see a return output of the form `x.y.z`.

## Upgrade

To change the version of Vizro-AI installed:

```bash
pip install -U vizro_ai
```

!!! tip Check the Vizro-AI release notes

    To upgrade safely, check the [release notes](https://github.com/mckinsey/vizro/blob/main/vizro-ai/CHANGELOG.md) for any notable breaking changes before migrating an existing project.
