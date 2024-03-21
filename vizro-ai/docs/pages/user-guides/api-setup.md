# How to set up and use a large language model with Vizro-AI
Use of Vizro-AI requires the use of a large language model. At present, we only support [OpenAI](https://openai.com/).

## Set up OpenAI
To use OpenAI with Vizro-AI you need an API key, which you can get by [creating an OpenAI account if you don't already have one](https://platform.openai.com/account/api-keys).

!!! note

    We recommend that you consult the [third-party API key section of the disclaimer documentation](../explanation/disclaimer.md) documentation.

### Set up the API key
There are two common ways to set up the API key in a development environment.

#### Method 1: Set an environment variable for a single project

To make the API key available for a single project, you can create a locacl `.env`
file to store it. Then, you can load the API key from that `.env` file in your development environment.

!!! example "The `.env` file should look as follows (containing your key rather than `abc123`)"
    === ".env"
        ```text
        OPENAI_API_KEY=abc123
        ```

By default, `vizro-ai` automatically loads the `.env` file, by searching the current directory and, if it does not find `.env`, the search continues upwards through the directory hierarchy.

If you would like to customize the `.env` file location and name, you can manually customize the search.
The default import of the `.env` file can be overridden by specifying the path and name.
Here's how you can do it:

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


#### Method 2: Set an environment variable for all projects

To make the OpenAI API key available for all projects, you can set it as a system environment
variable. Please refer to the section ["Set up your API key for all projects"](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key?context=python)
in the OpenAI documentation. (It is under the dropdown of "Step 2: Set up your API key").

The documentation provides step-by-step instructions for setting up the API key as an environment
variable, on operating systems including Windows and MacOS.


### Setup the base URL (optional)
You might need to provide the base URL if you are using a custom OpenAI resource endpoint.

The API base URL used for the OpenAI connector is set to `https://api.openai.com/v1` by default.
If you are using a custom API endpoint, for example, if your organization has a designated API gateway,
you can change the base URL by setting it as an environment variable.


Follow the approach above in Method 2 to [add the environment variable `OPENAI_API_BASE` for use by all projects](#method-2-set-an-environment-variable-for-all-projects).
