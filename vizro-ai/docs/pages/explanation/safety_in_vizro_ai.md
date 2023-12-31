## Warning and Safety usage for Generative AI Models

Generative AI models, especially Large Language Models (LLMs) represent significant advancements in the AI field.
Vizro-AI also leverages LLMs, however, as with any powerful tool, there are potential risks associated.

Users must connect to a generative AI model, specifically LLMs to use Vizro-AI.
We recommend users research and understand the selected model before using `vizro_ai` package.

Users are encouraged to treat AI-generated content as supplementary, **always apply human judgment**,
approach with caution, review the relevant [disclaimer](disclaimer.md) page, and consider the following:

### 1. Hallucination and Misrepresentation

Generative models can potentially generate information while appearing factual, being entirely fictitious or misleading.
The vendor models might lack real-time knowledge or events beyond its last updates.
`vizro_ai` output may vary and please always verify critical information.
It is the user's responsibility to discern the accuracy, consistent, and reliability of the generated content.

### 2. Unintended and Sensitive output

The outputs from these models can be unexpected, inappropriate, or even harmful.
Users as human in the loop is an essential part. Users must check and interpret the final output.
It is necessary to approach the generated content with caution, especially when shared or applied in various contexts.

### 3. Data Privacy

Your data is sent to model vendors if you connect to LLMs via their APIs.
For example, if you connect to the model "gpt-3.5-turbo-0613" from Open AI, your data will be sent to OpenAI via their API.
Users should be cautious about sharing or inputting any personal or sensitive information.

### 4. Bias and Fairness

Generative AI can exhibit biases present in their training data.
Users need to be aware of and navigate potential biases in generated outputs and be cautious when interpreting the generated content.

### 5. Malicious Use

These models can be exploited for various malicious activities. Users should be cautious about how and where they deploy and access such models.

It's crucial for users to remain informed, cautious, and ethical in their applications.

## Dependencies, Code Scanners and Infosec

It may occur that dependencies of `vizro_ai` get flagged by code scanners and other infosec tools. As a consequence it may happen that
`vizro_ai` also get flagged.

While we aim to resolve any flagged issues as soon as possible, there may not always be an immediate available fix, especially in a very dynamic environment such as generative AI. We encourage users to investigate if any flagged infosec issues are actually related
to any functionality used in our code base or if they only concern functionality outside the scope of `vizro_ai`.

In case those issues are related to code execution, note that `vizro_ai` has its own process of executing dynamic code (see [Safeguard Execution of Dynamic Code](safeguard.md)), and does not rely on its dependencies to do so.

## Execution of Dynamic Code in Vizro-AI

The `exec()` statement is used in `vizro_ai`. It allows for dynamic execution of Python programs which can be powerful, but can also pose security risk
if used without caution. When paired with outputs from generative models, there is potential for unintended or malicious code execution.

Users must exercise caution when executing code generated by or influenced by AI models. It's essential to:

- Never input prompts designed to generate harmful or malicious code.
- Always consider using controlled environments, such as virtual machines or containers, to execute uncertain code
- Always be aware of potential risks when executing dynamically generated code in environments with access to sensitive data or systems
- Always be aware that malicious code execution cannot be mitigated with 100% certainty
- Always review and understand the selected model before connecting with `vizro_ai`

If you would like to learn more about our efforts in safeguarding code execution, please refer to [Safeguard Execution of Dynamic Code](safeguard.md) for more information.
