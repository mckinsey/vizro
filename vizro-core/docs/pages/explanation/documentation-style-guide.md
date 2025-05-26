# Vizro documentation style guide

<!-- vale off -->

This is the style guide we apply to the [Vizro documentation](https://vizro.readthedocs.io/en/stable/).

We ask anyone kind enough to contribute documentation changes to follow this style for consistency and simplicity.

What follows is a set of lightweight guidelines rather than rules. There are always edge cases and exceptions, and if it's not obvious what the style should be, consult the [Microsoft style guide](https://docs.microsoft.com/en-gb/style-guide/welcome/) for an example of good practice. We also [ensure inclusive terminology](https://developers.google.com/style/inclusive-documentation) with the Google developer documentation style guide.

## Vizro lexicon

The names of our products and sites are:

- **[Vizro](https://github.com/mckinsey/vizro)**
- **[Vizro-AI](https://github.com/mckinsey/vizro/tree/main/vizro-ai)**
- **[Vizro-MCP](https://github.com/mckinsey/vizro/tree/main/vizro-mcp)**
- **[Vizro visual vocabulary dashboard](https://huggingface.co/spaces/vizro/demo-visual-vocabulary)**
- **[Vizro examples gallery](https://vizro.mckinsey.com/)**

We refer to other products using their preferred capitalization. For example:

- Dash and Pydantic are always capitalized, except where given as Python package names `dash` and `pydantic`.
- pandas DataFrame has a lowercase "p" and camelcase "DataFrame".

Vizro components are named using lower case:

> Here is a guide to using containers...

Use code font when referring to the component as a class or object:

> To add a `Container` to your page...

Avoid referring to data using terms like "dataset" or "connector". Prefer to use just "data" or, where that does not feel natural, "data source".

## Bullets

- Capitalize the first word, and end the bullet with a period.
- Don't use numbered bullets except for a sequence of instructions, or where you have to refer back to one of them in the text (or a diagram).

## Call out boxes

Keep the amount of text, and the number and variety of callouts used, to a minimum. There is a [broad set available](https://squidfunk.github.io/mkdocs-material/reference/admonitions/#supported-types) for use in the Vizro docs, but we limit usage to notes, warnings, details and examples:

!!! note "note"

    For notable information.

!!! warning "warning"

    To indicate a potential gotcha.

??? details "See more details"

    A side note (used sparingly)

!!! example "example"

    For example code.

Callout boxes can be made collapsible: if you use them, add them to the page so they are initially collapsed.

???+ note "Limit the use of collapsible callouts to secondary information only"

    Don't use expanded-on-load collapsibles like this one. If the callout contains important information and needs to be shown as expanded on page load, it should simply be non-collapsible.

## Capitalization

- Only capitalize proper nouns such as the names of technology products, other tools and services.
- Don't capitalize cloud, internet, machine learning, or advanced analytics. Take a look at the [Microsoft style guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/term-collections/accessibility-terms) if you're unsure.
- Follow sentence case, which capitalizes only the first word of a title/subtitle. We prefer "An introduction to data visualization" to "An Introduction to Data Visualization".

## Code formatting

- Mark code blocks with the appropriate language to enable syntax highlighting.
- We use a `bash` lexer for all codeblocks that represent the terminal, and we don't include the prompt.
- Use the code format for Python package names such as `pandas` or `pydantic`.

## Headings and subheadings

Choosing a heading is sometimes the hardest part of the writing process. Take your time!

Aim to avoid use of gerunds (verb+ing) where you can. So your page should be "Get started" rather than "Getting started" and "Customize a layout" rather than "Customizing a layout". Keep the title short and descriptive, ideally think about a reader who may be using a search engine to find an answer -- structure your title to give them the best chance of understanding what the page tells them.

In Vizro, when you are working on a how-to guide, there are a few more guidelines to follow for consistency:

- Don't use "how to" in the file name: keep that as short as possible.
- The title (H1 header) should start with "How to".
- Don't use "how to" in the subsections that follow (H2 - H5) unless you consider the alternative to be confusing.
- Don't use gerund form in the subsections either.

Example: In a page called "Filters" you would have the following:

- H1: "How to use filters"
- H2 subsection: "Use a custom filter" and not "How to use a custom filter" nor "Using a custom filter".

## Instructions

Prefer to use imperatives to make instructions. For example:

> Complete the configuration steps

You don't need to use the word "please" -- readers want less to read and don't think it's rude if you omit it.

You can also use second person:

> You should complete the configuration steps.

Don't use the passive tense:

> The configuration steps should be completed.

!!! note "What is passive tense?"

    If you can add "by zombies" to the end of any sentence, it is passive.

    - For example: "The configuration steps should be completed." can also be read as: "The configuration should be completed BY ZOMBIES".
    - Instead, you'd write this: "You should complete the configuration steps" or better still, "Complete the configuration steps".

## Language

- Use US English.

## Links

- Make hyperlink descriptions as descriptive as you can. This is a good description:

> Learn how to [contribute to Vizro](https://vizro.readthedocs.io/en/stable/pages/development/contributing/).

This is less helpful:

> [Learn how to](https://vizro.readthedocs.io/en/stable/pages/development/contributing/) contribute to Vizro.

Don't write this:

> To learn how to contribute to Vizro, see [here](https://vizro.readthedocs.io/en/stable/pages/development/contributing/).

### Internal cross-referencing

We use internal cross-references as follows:

- For each documentation page, if it helps the reader, we link to narrative documentation (non-API documentation) about each Vizro topic where it is first introduced.
- On any single page, we limit the repetition of links: do not re-link to the same page again unless there is good reason to do so (for example, linking to a specific sub-section to illustrate a point).
- Add links to relevant API documentation where it is useful for the reader, and consider how they will navigate from where they land in the API documentation back to the narrative content. Consider adding a link in the relevant docstring back to your page.

## Oxford commas

Use these in lists to avoid confusion. This is confusing:

> The ice cream comes in a range of flavors including banana and strawberry, mango and raspberry and blueberry.

This is clearer:

> The ice cream comes in a range of flavors including banana and strawberry, mango and raspberry, and blueberry.

## Style

Keep your sentences short and easy to read. Your tone of voice should be simple, friendly and functional.

### Simple

Simple is clear, concise and direct:

> We build new skills in your team.

Simple is not vague, verbose or full of jargon:

> We leverage your existing organizational resources to synthesize novel competencies.

### Friendly

Friendly is approachable and open, and it makes discussions flow:

> Vizro: Let’s make cool visualizations happen. Together.

Friendly is not secretive, negative, vague or non-inclusive:

> Vizro is utilized to build tier one visualizations for your organization.

### Functional

Functional is compelling, positive, inspiring:

> 200+ successful projects and counting.

Functional is not try-hard, cliched or hyperbolic:

> We’re ultra-sucessful business-builders.

## Things to avoid

- **Gerunds in headings**. What are these? They are the "-ing" forms of verbs. If you find yourself writing "Getting started" in a heading, then consider "Get started" or "How to get started" instead. In fact, in general, it's better to avoid gerund-forms of verbs where you can.
- **Plagiarism**. Link to their text and credit them.
- **Colloquialisms**. Avoid them "like the plague" because they may not translate to other regions/languages.
- **Technical terminology**. This applies particularly to acronyms that do not pass the "Google test". If it is not possible to find their meaning from a simple Google search, don't use them, or explain them with a link or some text.
- **Business speak**. You can explain simply without using words like "leverage", "utilize" or "facilitate" and still sound clever.

<!-- vale on -->
