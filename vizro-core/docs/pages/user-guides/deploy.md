# How to deploy your dashboard to production

Typically when you create a dashboard, there are two distinct stages:

1. Development. This is when you build your app. You make frequent changes to your code and want a simple way to see how the dashboard looks after each change. At this point, you may, or may not, want to make it possible for other people to access your dashboard.
1. Production. When you complete development of your app, you _deploy_ it to production. The dashboard should be accessible to other people.

This page describes methods to run your dashboard _in production_. If your dashboard is still in development then you should read our [guide to development](run.md).

Vizro is built on top of [Dash](https://dash.plotly.com/), which itself uses [Flask](https://flask.palletsprojects.com/). Most of our guidance on how to run a Vizro app in development or production is very similar to guidance on Dash and Flask.

??? note
    There are many possible workflows depending on your requirements. The above describes a simple workflow that applies to many people but is not suitable for everyone. For example:

    - If you are the only user of your app then the process is often simpler since you might never want to deploy to production.
    - If there are multiple people involved with development then you will need some way to coordinate code changes, such as a [GitHub repository](https://github.com/) or [Hugging Face Space](https://huggingface.co/spaces).
    - You might want to use _authentication_ to restrict access to your app.
    - You might want to update your dashboard after it has been put into production. There is then a cycle of repeated development and deployment.
    - There might be additional stages or _environments_ for Quality Assurance (QA) to test that the app works correctly before it is deployed.

## Overview

When developing your dashboard you typically run it _locally_ (on your own computer) using the Flask development server. When you deploy to production, this is no longer suitable. Instead, you need a solution that can handle multiple users in a stable, secure and efficient way.

Vizro is a production-ready framework, which means that the dashboard created during development is immediately suitable for deployment to production with minimal changes. Under the hood, Vizro uses [Dash's stateless architecture](https://dash.plotly.com/sharing-data-between-callbacks#dash-is-stateless), designed for scaling to thousands of concurrent users.

In general, there is only one code change that is required. The last of your `app.py` file should look like `Vizro().build(dashboard).run()`. This should be replaced with:

```python
app = Vizro().build(dashboard)  # (1)!

if __name__ == "__main__":  # (2)!
    app.run()
```

1. The Vizro `app` object needs to be exposed so that the app can be started in production.
1. This code is only executed when you run `python app.py` and does not run in production. It's there to enable you to [run the same app in development](run.md#development-server) using the Flask development server.

That's it! Your app is now suitable for deployment to production.

!!! warning "Extra step if you use dynamic data cache"
    If your dashboard uses [dynamic data](data.md#dynamic-data) that can be refreshed while the dashboard is running then you should [configure your data manager cache](data.md#configure-cache) to use a backend that supports multiple processes.

Now that your `app.py` file is ready, you need to choose a _hosting provider_. There are many services out there with different offerings, but for most users we recommend two in particular: [Hugging Face](https://huggingface.co/) and [Ploomber Cloud](https://docs.cloud.ploomber.io/). These both have a free tier with the possibility of paying more for extras, and they are both quick and easy to get started with. We give step-by-step instructions on how to use each:

- [Deploy a Vizro dashboard to Hugging Face](#hugging-face)
- [Deploy a Vizro dashboard to Ploomber Cloud](#ploomber-cloud)

Enterprise users should look at our guidance for [deploying Vizro dashboards on Dash Enterprise](#dash-enterprise). We also discuss the [general principles for deploying a Vizro app](#general-principles) that apply to all hosting providers.

## Hugging Face

[Hugging Face](https://huggingface.co/) is a platform for machine learning models, datasets and demos. Within Hugging Face, the [Spaces feature](https://huggingface.co/spaces/launch) offers a one click experience to deploy a Vizro dashboard for free. This is the easiest way to deploy a Vizro app if you do not mind your app's code being public or shared within your [Hugging Face organization](https://huggingface.co/organizations). Paid plans include features such as authentication, developer mode for debugging, user analytics and more powerful computing resources.

The best way to get started with Vizro on Hugging Face is to copy an existing Vizro dashboard and then modify it to add your own app. Vizro maintains an [official gallery of example dashboards](https://huggingface.co/collections/vizro/vizro-official-gallery-66697d414646eeac61eae6de) and a [gallery of example dashboards made by the community](https://huggingface.co/collections/vizro/community-demos-666987c8e9f56afc7bc1d0fc). Any of these example dashboards can be used as a template for your app. In Hugging Face terminology, a Vizro dashboard lives in a _Space_, and you can copy a dashboard by [duplicating the Space](https://huggingface.co/docs/hub/en/spaces-overview#duplicating-a-space).

If this is your first Vizro deployment then we recommend using our ["first dashboard" example](https://huggingface.co/spaces/vizro/demo-first-dashboard). This is a minimal example that is designed to make it as simple as possible to get started on Hugging Face. You can create your own Vizro deployment based on this template as follows:

1. [Sign up for a Hugging Face account](https://huggingface.co/join).
1. Copy our example Hugging Face dashboard by duplicating our ["first dashboard" example Space](https://huggingface.co/spaces/vizro/demo-first-dashboard). To do so, click the following button: [![Duplicate this Space](https://huggingface.co/datasets/huggingface/badges/resolve/main/duplicate-this-space-md.svg)](https://huggingface.co/spaces/vizro/demo-first-dashboard?duplicate=true). This should open a window with the following form: ![Form to duplicate Space](../../assets/user_guides/deploy/hugging_face_duplicate_this_space.png)
1. You do not need to alter any of the default options but the [Hugging Face documentation](https://huggingface.co/docs/hub/en/spaces-overview#duplicating-a-space) gives an explanation of each.
1. Click "Duplicate Space" to start building your Hugging Face Space. This takes around 10 seconds, and when complete you should see the following dashboard running. ![Running dashboard](../../assets/user_guides/deploy/hugging_face_space.png)

To turn the example app into your own, you will need to edit the code in the `app.py` file. Click on the Files tab at the top of your app and select `app.py`. Click the Edit button highlighted in the below screenshot to enter an editor view of the file. ![Edit app.py](../../assets/user_guides/deploy/hugging_face_edit_app.png)

You can now copy and paste your app code into the editor. When you've finished editing, click "Commit changes to `main`". This immediately triggers a rebuild of your Space. As with the initial build this takes around 10 seconds, and when complete you should be able to view your own app deployed on Hugging Face!

!!! note
    Remember that a deployed `app.py` file must contain a line that [exposes the Vizro `app` object](#overview) as `app = Vizro().build(dashboard)`.

Under the hood, your Space is a Git repository. Instead of editing files through your browser, you can use [`git` from the command line and the Hugging Face CLI](https://huggingface.co/docs/hub/en/repositories-getting-started). Every time you make a commit to your repository, your app is automatically rebuilt and restarted.

In addition to `app.py`, your Space contains a few other files:

- `.gitattributes` is used by [Git Large File Storage (LFS)](https://git-lfs.com/) and is only relevant if you have files larger than 10MB. See the [Hugging Face documentation](https://huggingface.co/docs/hub/en/repositories-getting-started) for more information.
- `Dockerfile` gives instructions to configure your app's environment and start the app. See our [section on Dockerfiles](#dockerfile) for more information.
- `README.md` configures your Space, for example its title, description and licence. See the [Hugging Face documentation](https://huggingface.co/docs/hub/en/spaces-config-reference) for more information.
- `requirements.txt` gives your Python package dependencies. See our [section on dependencies](#dependencies) for more information.

!!! tip
    If you'd like to show your Vizro app off to the community then you can add it to our [Vizro dashboard community gallery](https://huggingface.co/collections/vizro/community-demos-666987c8e9f56afc7bc1d0fc).

On Hugging Face, Vizro apps are hosted on Docker Spaces. Hugging Face has thorough documentation on [Spaces in general](https://huggingface.co/docs/hub/en/spaces-overview) and specifically on [Docker Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-docker-first-demo). There are many features that go beyond simply hosting a Vizro app. For example, you can [make a collection](https://huggingface.co/docs/hub/en/collections) of multiple Spaces, collaborate on your code using [pull requests and discussions](https://huggingface.co/docs/hub/en/repositories-pull-requests-discussions), or create an [organization](https://huggingface.co/docs/hub/en/organizations) to group accounts and Spaces together.

## Ploomber Cloud

[Ploomber Cloud](https://ploomber.io/) is a platform specifically built to deploy data visualization apps built using frameworks such as Vizro. Its free tier offers an easy deployment by drag and drop, the [Ploomber Cloud CLI](https://docs.cloud.ploomber.io/en/latest/user-guide/cli.html), or `git push`. Paid plans include features such as a custom domain, enterprise-grade authentication, user analytics and more powerful computing resources.

The [Ploomber Cloud documentation](https://docs.cloud.ploomber.io/en/latest/apps/vizro.html) contains detailed instructions on how to deploy Vizro on Ploomber Cloud. In short, the process is as follows:

1. [Sign up for a Ploomber Cloud account](https://platform.ploomber.io/register).
1. Modify the last line of your `app.py` to [expose the Vizro `app` object](#overview) as `app = Vizro().build(dashboard)`.
1. Create a `requirements.txt` file to give your Python package dependencies. This should include `vizro` and `gunicorn`. See our [section on dependencies](#dependencies) for more information.
1. Create a `Dockerfile` by copying the [example given in the Ploomber Cloud documentation](https://docs.cloud.ploomber.io/en/latest/apps/vizro.html#application-setup). See our [section on Dockerfiles](#dockerfile) for more information.
1. Compress your `app.py`, `requirements.txt` and `Dockerfile` into a single zip file.
1. Upload the zip file to Ploomber Cloud.

## Dash Enterprise

Since a Vizro app is a Dash app under the hood, they can be deployed to [Dash Enterprise](https://plotly.com/dash/) and accessed in the same way as other Dash apps.

Dash Enterprise helps to deploy and scale production-grade data apps and integrate them with IT infrastructure such as authentication and VPC services. Vizro users may find it suitable for deployment, rapid development environments, and authentication.

Vizro is compatible with the following functionality within Dash Enterprise:

- [App Portal](https://dash.plotly.com/dash-enterprise/portal?de-version=5.5)
- [App Manager](https://plotly.com/dash/app-manager/)
- [Dash App Workspaces](https://plotly.com/dash/workspaces/)
- [App logs and viewer statistics](https://dash.plotly.com/dash-enterprise/logs)
- [Centralized data app management](https://plotly.com/dash/centralized-data-app-management/)
- [CI/CD](https://plotly.com/dash/continuous-integration/)
- [Redis](https://plotly.com/dash/big-data-for-python/)
- [Dash Enterprise Authentication](https://plotly.com/dash/authentication/)

Vizro is not currently compatible with the [Dashboard Engine](https://plotly.com/dash/dashboard-engine/) or [Dash Design Kit](https://plotly.com/dash/design-kit/), and cannot produce static reports accessed via the [Snapshot Engine](https://plotly.com/dash/snapshot-engine/).

## General principles

There are many other hosting providers, such as [Render](https://render.com/), [Heroku](https://www.heroku.com/), and [Fly](https://fly.io/). Some of these, such as Render, offer a free tier.

Although these services work in slightly different ways, there are some general principles that usually apply across all hosting providers. In general, the procedure is:

1. Modify the last line of your `app.py` to [expose the Vizro `app` object](#overview) as `app = Vizro().build(dashboard)`.
1. Create a `requirements.txt` file to give your Python package dependencies. This should include `vizro` and `gunicorn`. See the [section on dependencies](#dependencies) for more information.
1. Upload your `app.py` and `requirements.txt` files, for example by drag and drop, your hosting provider's CLI, or `git push`.
1. Specify on your hosting provider how to handle your app:
    - Before the app is started, the environment needs to be built. Python dependencies should be installed with `pip install -r requirements.txt`.
    - To start the app, you should use the command `gunicorn app:app --workers 4`. See the [section on Gunicorn](#gunicorn) for more information.
    - Optional: set [advanced configuration](#advanced-configuration), for example to serve assets using a Content Delivery Network (CDN).
1. Optional: configure further settings on your hosting provider, for example to make your dashboard private or to configure computing resources.

The method for providing instructions on how to handle your app varies between hosting providers. For example, on Render there are [build and deploy commands](https://render.com/docs/deploys); on Heroku and Dash Enterprise there is a [Procfile](https://devcenter.heroku.com/articles/procfile). One common cross-platform way to configure an environment is using a Dockerfile. This is used by both Hugging Face and Ploomber Cloud among others. See the [section on Dockerfile](#dockerfile) for more information.

### Dependencies

The `requirements.txt` file [specifies your app's Python dependencies](https://pip.pypa.io/en/stable/reference/requirements-file-format/). At a minimum, the file must include `vizro` (used to run the app in development and production) and `gunicorn` (used only in production). Our simple dashboard demo has exactly this [minimal example `requirements.txt`](https://huggingface.co/spaces/vizro/demo-first-dashboard/blob/main/requirements.txt). These dependencies should then be installed on your host server using [`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/) with the command `pip install -r requirements.txt` (or the [`uv` equivalent](https://docs.astral.sh/uv/pip/packages/#installing-a-package) `uv pip install -r requirements.txt`).

Although this process for handling dependencies is sufficient to get started with deployment, it is best practice to _pin_ your dependencies to exact versions. This ensures that your app does not break when your dependencies are updated. Ideally, pinned versions should include both your _direct_ dependencies and their dependencies (your _transitive_ dependencies). There are two alternative methods we recommend for this:

- Run [`pip freeze`](https://pip.pypa.io/en/stable/cli/pip_freeze/) in your development environment to create the `requirements.txt` file with `pip freeze > requirements.txt`. On your host server, these dependencies are installed with `pip install -r requirements.txt`.
- Create a new file `requirements.in` for your unpinned requirements and run [`uv pip compile`](https://docs.astral.sh/uv/pip/compile/) to generate the `requirements.txt` file from this with `uv pip compile requirements.in -o requirements.txt`. On the host server, these dependencies should be installed with `uv pip sync requirements.txt`. This is the method followed in our [KPI dashboard demo](https://huggingface.co/spaces/vizro/demo-kpi/tree/main).

### Gunicorn

[Gunicorn](https://gunicorn.org/) is a production-ready Python server for deploying an app over multiple worker processes. The standard way to write a Vizro app is to have a file called `app.py` that contains the Vizro app in a variable called `app`. Given this setup, the command to start Gunicorn with four worker processes is:

```bash
gunicorn app:app --workers 4
```

The Gunicorn documentation gives [commonly used arguments](https://docs.gunicorn.org/en/stable/run.html#commands) and advice for setting them. Other than `workers`, the most common argument to specify is `bind`, which makes your app accessible. This is often set as `--bind 0.0.0.0:<port>`. Your hosting provider needs to tell you what the correct port to use is. For example, on Hugging Face it is 7860 and on Ploomber Cloud it is 80.

### Dockerfile

A [Dockerfile](https://docs.docker.com/build/concepts/dockerfile/) contains instructions to build a [container image](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/). You can think of it as a way to give in a single file all the instructions that your hosting provider needs to deploy your app. This includes both the [installation of dependencies](#dependencies) and [starting the app with Gunicorn](#gunicorn). A Dockerfile is used by many hosting providers, including Hugging Face and Ploomber Cloud.

Here is an annotated [example Dockerfile](https://huggingface.co/spaces/vizro/demo-first-dashboard/blob/main/Dockerfile) that we use in our simple Hugging Face demo. It demonstrates the key Dockerfile instructions needed to deploy Vizro and should serve as a good starting point for your own Dockerfile.

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim  # (1)!

WORKDIR /app

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt
COPY . .
# (2)!

ENTRYPOINT ["gunicorn", "app:app", "--workers", "4", "--bind", "0.0.0.0:7860"]
# (3)!
```

1. Use a Docker image that [includes `uv` pre-installed](https://docs.astral.sh/uv/guides/integration/docker/).
1. Install the [Python dependencies](#dependencies) as [described in the `uv` documentation](https://docs.astral.sh/uv/guides/integration/docker/#installing-requirements). The app files are copied into the container after installing dependencies to optimise Docker's [build cache](https://docs.docker.com/build/cache/).
1. Run the Vizro app using [Gunicorn](#gunicorn).

### Advanced configuration

Vizro is built on top of [Dash](https://dash.plotly.com/), which itself uses [Flask](https://flask.palletsprojects.com/). Deployment of Vizro is essentially the same as deployment of the underlying frameworks, and more guidance can be found in [Flask's deployment documentation](https://flask.palletsprojects.com/en/2.0.x/deploying/) and [Dash's deployment documentation](https://dash.plotly.com/deployment).

[`Vizro`][vizro.Vizro] accepts `**kwargs` that are passed through to `Dash`. This enables you to configure the underlying Dash app using the same [arguments that are available](https://dash.plotly.com/reference#dash.dash) in `Dash`. For example, in a deployment context, these arguments may be useful:

- `url_base_pathname`: serve your Vizro app at a specific path rather than at the domain root. For example, if you host your dashboard at `http://www.example.com/my_dashboard/` then you would set `url_base_pathname="/my_dashboard/"` or an environment variable `DASH_URL_BASE_PATHNAME="/my_dashboard/"`.
- `serve_locally`: set to `False` to [serve Dash component libraries from a Content Delivery Network (CDN)](https://dash.plotly.com/external-resources#serving-dash's-component-libraries-locally-or-from-a-cdn), which reduces load on the server and can improve performance. Vizro uses [jsDeliver](https://www.jsdelivr.com/) as a CDN for CSS and JavaScript sources.
- `assets_external_path`: when `serve_locally=False`, you can also set `assets_external_path` or an environment variable `DASH_ASSETS_EXTERNAL_PATH` to [serve your own assets from a CDN](https://dash.plotly.com/external-resources#load-assets-from-a-folder-hosted-on-a-cdn).

In fact, the only difference between deploying a Vizro app and deploying a Dash app is that Vizro implements a small simplification that makes it unnecessary for you to add a line like `server = app.server`, as you would do with Dash. Internally, `app = Vizro()` contains a Flask app in `app.dash.server`. As a convenience, the Vizro `app` itself implements the [WSGI application interface](https://werkzeug.palletsprojects.com/en/3.0.x/terms/#wsgi) as a shortcut to the underlying Flask app. This means that the Vizro `app` object can be directly supplied to the WSGI server in the command `gunicorn app:app`.
