---
hide:
  - navigation
  - toc
---

# Vizro-Experimental

Vizro-Experimental is the **incubation home** for large Vizro features that aren't ready
for [`vizro-core`](https://vizro.readthedocs.io) yet. APIs in this package may change
or be removed between releases. Once a feature stabilises, it graduates to `vizro-core`.

## Get started

<div class="grid cards" markdown>

- :fontawesome-solid-comments:{ .lg .middle } __Chat component__

    Add a Chat to a page and back it with an action. Subclass `ChatAction` (sync) or
    `StreamingChatAction` (SSE) for any LLM, file upload, or rich response pattern.

    [:octicons-arrow-right-24: Get started](pages/chat/chat-component.md)

- :fontawesome-solid-window-restore:{ .lg .middle } __Chat popup__

    Drop a floating chatbot onto any dashboard with one line. Auto-discovers data
    from `data_manager` and answers questions about it via a built-in LangChain agent.

    [:octicons-arrow-right-24: Add a chat popup](pages/chat/chat-popup.md)

</div>
