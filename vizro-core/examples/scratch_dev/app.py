"""Development playground exploring markdown variations using built-in Vizro models.

This script demonstrates a variety of ways to render markdown content with
components that internally rely on `vdc.Markdown` (the new built‑in
markdown component).  The goal is to exercise code blocks, math formulas,
links, headers and dynamic content without importing `vizro_dash_components`
explicitly.  We show both static pages (with `vm.Text` and `vm.Card`) and
custom figures which react to filters/parameters.
"""

import pandas as pd

import vizro.models as vm
from vizro import Vizro

# sample data with several kinds of markdown content

df = pd.DataFrame(
    {
        "topic": ["Python", "JavaScript", "SQL", "React"],
        "description": [
            "A versatile programming language",
            "The language of the web",
            "Database query language",
            "A JavaScript library for building UIs",
        ],
        "code_example": [
            '```python\ndef hello():\n    return "Hello, World!"\n```',
            '```javascript\nconst hello = () => "Hello, World!";\n```',
            "```sql\nSELECT * FROM users WHERE active = true;\n```",
            "```jsx\nconst App = () => <h1>Hello, World!</h1>;\n```",
        ],
        "formula": [
            r"$f(x) = x^2 + 2x + 1$",
            r"$y = mx + b$",
            r"$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$",
            r"$E = mc^2$",
        ],
    }
)

# tests previously used custom figure functions with capture decorators.
# since we only want to demonstrate vm.Text/vm.Card models we remove
# all @capture definitions and instead create simple pages directly.

# (helper data still available for manual consumption if desired)


# -----------------------------------------------------------------------------
# Pages built from the helper figures and static text/card examples
# -----------------------------------------------------------------------------

# create a page that showcases various markdown features using vm.Text
page_static = vm.Page(
    title="Markdown variations",
    components=[
        vm.Text(
            text="""# Header level 1

This is a paragraph with **bold**, *italic*, and a [link](https://example.com).

Here is some inline code: `print('hi')`.

And a fenced code block:
```python
for i in range(3):
    print(i)
```
""",
        ),
        vm.Text(
            text="""## Math and lists

To render math use `$E = mc^2$` inline or

This example uses the block delimiter:
$$
\\frac{1}{(\\sqrt{\\phi \\sqrt{5}}-\\phi) e^{\\frac25 \\pi}} =
1+\\frac{e^{-2\\pi}} {1+\\frac{e^{-4\\pi}} {1+\\frac{e^{-6\\pi}}
{1+\\frac{e^{-8\\pi}} {1+\\ldots} } } }
$$

This example uses the inline delimiter:
$E^2=m^2c^4+p^2c^2$


- bullet
- points
""",
            extra={"mathjax": True},
        ),
        vm.Card(
            header="Card header",
            text="""Cards can also contain markdown text with **formatting**.

```bash
$ echo hello
```""",
            footer="Footer text",
        ),
    ],
)

# a later page demonstrating layout flexibility and code snippets
page_snippet = vm.Page(
    title="Code snippet examples",
    components=[
        vm.Card(
            text="""

Block code snippet:
```python
print('hello world')
```

""",
        ),
        vm.Card(
            text="""
and inline code snippet: `print('hello world')`

and
```javascript
console.log('hello world');
const add = (a, b) => a + b;
```
""",
        ),
        vm.Text(
            text="""

Another snippet inside ``vm.Text``:
```python
# Kadane's Algorithm

class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        curr, summ = nums[0], nums[0]
        for n in nums[1:]:
            curr = max(n, curr + n)
            summ = max(summ, curr)
        return summ
```

test test tests
""",
        ),
    ],
)

# note: page_snippet already defined above, nothing else needed
# assemble dashboard

dashboard = vm.Dashboard(
    title="QB",
    pages=[page_static, page_snippet],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
