# vizro-experimental

**Status: experimental.** This package is the incubation home for large Vizro
features that aren't ready for [`vizro-core`](../vizro-core) yet. APIs may
change or be removed between releases.

## Install

```bash
pip install vizro-experimental              # core Chat component
pip install "vizro-experimental[agent]"     # + floating chat popup with auto-agent
```

## Chat component

```python
import vizro.models as vm
from vizro import Vizro
from vizro_experimental.chat import Chat, ChatAction, Message

class EchoAction(ChatAction):
    def generate_response(self, messages: list[Message]) -> str:
        return f"You said: {messages[-1]['content']}"

vm.Page.add_type("components", Chat)

dashboard = vm.Dashboard(
    pages=[vm.Page(title="Chat", components=[Chat(actions=[EchoAction()])])]
)
Vizro().build(dashboard).run()
```

## Floating chat popup

```python
from vizro import Vizro
from vizro_experimental.chat.popup import add_chat_popup

app = Vizro().build(dashboard)
add_chat_popup(app)   # auto-discovers dashboard data; requires OPENAI_API_KEY
app.run()
```

## Documentation

See [vizro.readthedocs.io/projects/vizro-experimental](https://vizro.readthedocs.io/projects/vizro-experimental).

## License

Apache 2.0. See [LICENSE.txt](LICENSE.txt).
