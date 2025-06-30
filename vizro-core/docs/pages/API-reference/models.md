# Models

<!-- vale off -->
API reference for all [`pydantic`](https://docs.pydantic.dev/latest/) models used.

::: vizro.models._dashboard.ExampleModel

::: vizro.models.Dashboard
    options:
          filters: ["!^_","!build","!model_post_init"] # Don't show underscore methods, build method, and model_post_init
::: vizro.models.Page
    options:
          filters: ["!^_","!build","!model_post_init"] # Don't show underscore methods, build method, and model_post_init
<!-- 
::: vizro.models
    options:
      filters: ["!^_","!build","!model_post_init"] # Don't show underscore methods, build method, and model_post_init
-->
::: vizro.models.types
    options:
      filters: ["!^_"]  # Don't show dunder methods as well as single underscore ones
      merge_init_into_class: false

<!-- vale on -->
