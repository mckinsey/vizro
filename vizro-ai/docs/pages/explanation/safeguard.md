# Safeguard dynamic code execution in Vizro-AI

Vizro-AI uses the `exec()` statement in Python to run generated code from large language models (LLMs) for self-debugging and automatic visual rendering in methods such as `.get_fig_object()` and `VizroAI.plot()`. One of the primary concerns is the potential for malicious code to access or change critical system resources or data.

## Understand `exec()`

The `exec()` function enables the dynamic execution of Python programs which can either be a string or object code. While it offers great flexibility, it also poses a significant security risk, especially when executing untrusted code.

## Safeguarding code execution

While we have made considerable efforts to safeguard its usage by limiting the usage to specific modules and functions and by restricting certain built-in operations, these measures cannot guarantee absolute security. It is imperative for users to take extra precautions.

### Our effort on safeguarding code execution in Vizro-AI

To help to mitigate these risks, we limit the execution of certain modules and functions. One approach is to use Python's built-in `sys` module to restrict access to unsafe modules or functions. By defining a whitelist of safe modules and packages and restricting certain built-in functions.

!!! Warning

    While some measures have been put in place to help safeguard against known vulnerabilities, it is important to run such systems in an isolated environment and avoid providing malicious inputs, since such **safeguards can never be 100% effective**. Always ensure the security infrastructure when implementing and using such systems.

    The white lists indicate allowed packages and built-in functions.

    The red lists represent potentially unsafe methods or operations that are restricted.

The lists below are a reflection of the security and functionality we have implemented with Vizro-AI:

<!--vale off-->

??? success "Whitelisted Packages"

    - `pandas`
    - `numpy`
    - `vizro`
    - `plotly`
    - `datetime`
    - `matplotlib`
    - `dash`
    - `scipy`
    - `sklearn`

??? success "Whitelisted Builtins"

    - abs
    - len
    - max
    - min
    - print
    - sum
    - None
    - False
    - True
    - dict
    - enumerate
    - float
    - int
    - list
    - map
    - str
    - tuple

??? failure "Redlisted Class Methods"

    - subclasses
    - builtins

??? failure "Redlisted Data Handling Methods and Formats"

    - Various data file formats (such as .csv, .tsv, .xlsx, .json, and so on)
    - Specific methods related to data input/output operations (such as .to_csv, .read_excel, .loadtxt)

<!--vale on-->

### Safeguard for user environment and input

- **Isolated environment**: Always run code in an isolated or contained environment, such as a virtual environment, virtual machine or container, to minimize potential harm to the primary system.

- **Avoid malicious input**: Never feed untrusted or malicious input. Regardless of safeguards, there's always a risk associated with executing dynamic code. It remains the user's responsibility to ensure the safety and appropriateness of executing any generated code, particularly in sensitive or critical contexts.

- **Accessible to trusted users**: Only trusted users should be given access to the system to run Vizro-AI.
