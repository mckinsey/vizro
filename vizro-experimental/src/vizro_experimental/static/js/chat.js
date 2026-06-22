/**
 * Vizro Chat Component - Clientside Callbacks
 *
 * This file contains JavaScript functions used by the chat component's
 * clientside callbacks for SSE streaming, markdown rendering, and UI interactions.
 */

// Register as a dash_clientside namespace so Dash ClientsideFunction can reference these directly.
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.vizroChatComponent =
  window.dash_clientside.vizroChatComponent || {};

// ==================== Constants ====================

// CSS class names (must match chat.css)
const CSS_MESSAGE_BUBBLE = "chat-message-bubble";
const CSS_USER_MESSAGE = "chat-user-message";
const CSS_ASSISTANT_MESSAGE = "chat-assistant-message";
const CSS_MESSAGE_WRAPPER = "chat-message-wrapper";
const CSS_USER_TEXT = "chat-user-text";
const CSS_LOADING_MESSAGE = "chat-loading-message";

// ==================== SSE Streaming Decoder ====================

/**
 * Decodes and accumulates SSE streaming chunks for chat responses.
 * Used by StreamingChatAction to process real-time streaming data.
 *
 * @param {string} animatedText - The accumulated animated text from SSE
 * @param {Array} existingChildren - Current message children in hidden-messages
 * @param {Array} storeData - Current conversation store data
 * @returns {Array} [updatedChildren, updatedStoreData]
 */
window.dash_clientside.vizroChatComponent.processStreamingChunk = (
  animatedText,
  existingChildren,
  storeData,
) => {
  const CHUNK_DELIMITER = "|END|";
  const STREAM_DONE_SIGNAL = "[DONE]";

  // Helper: Decode base64 chunk to UTF-8 text
  function decodeChunk(chunk) {
    try {
      const binaryString = atob(chunk);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      return new TextDecoder("utf-8").decode(bytes);
    } catch (e) {
      console.warn("Failed to decode chunk:", e);
      return "";
    }
  }

  // Helper: Get message content from simple structure [role, content]
  function getMessageContent(msg) {
    if (
      msg?.props?.children &&
      Array.isArray(msg.props.children) &&
      msg.props.children.length >= 2
    ) {
      return msg.props.children[1]?.props?.children || "";
    }
    return "";
  }

  // Helper: Set message content in simple structure [role, content]
  function setMessageContent(msg, content) {
    if (
      msg?.props?.children &&
      Array.isArray(msg.props.children) &&
      msg.props.children.length >= 2
    ) {
      msg.props.children[1].props.children = content;
    }
  }

  // Handle stream completion
  if (!animatedText || animatedText === STREAM_DONE_SIGNAL) {
    window.lastProcessedChunkCount = 0;
    return [existingChildren, window.dash_clientside.no_update];
  }

  const newChildren = [...(existingChildren || [])];
  const newData = [...(storeData || [])];

  // Swap the send-click loading placeholder for an empty assistant bubble so
  // chunks accumulate into a real message instead of the spinner element.
  const last = newChildren[newChildren.length - 1];
  const isLoadingPlaceholder =
    last?.props?.children?.props?.className?.includes(CSS_LOADING_MESSAGE);
  if (isLoadingPlaceholder) {
    newChildren[newChildren.length - 1] = {
      type: "Div",
      namespace: "dash_html_components",
      props: {
        children: [
          {
            type: "Div",
            namespace: "dash_html_components",
            props: { children: "assistant", style: { display: "none" } },
          },
          {
            type: "Div",
            namespace: "dash_html_components",
            props: { children: "" },
          },
        ],
      },
    };
  }

  const lastMsg = newChildren[newChildren.length - 1];
  const currentContent = getMessageContent(lastMsg);

  // Reset counter for new messages
  if (!window.lastProcessedChunkCount || currentContent === "") {
    window.lastProcessedChunkCount = 0;
  }

  // Process new chunks only
  const chunks = animatedText.split(CHUNK_DELIMITER).slice(0, -1);
  const newText = chunks
    .slice(window.lastProcessedChunkCount)
    .filter(Boolean)
    .map(decodeChunk)
    .join("");

  window.lastProcessedChunkCount = chunks.length;

  // Update message content if new text received
  if (newText) {
    setMessageContent(lastMsg, currentContent + newText);

    // Update store data for assistant messages
    const lastStoreMsg = newData[newData.length - 1];
    if (lastStoreMsg?.role === "assistant") {
      // During streaming, accumulate in content_json as serialized string
      const existingContent = JSON.parse(lastStoreMsg.content_json || '""');
      lastStoreMsg.content_json = JSON.stringify(existingContent + newText);
    }
  }

  return [newChildren, newData];
};

// ==================== Markdown Parser & Code Block Renderer ====================

/**
 * Parses hidden message children and renders them with markdown formatting
 * and syntax-highlighted code blocks.
 *
 * @param {Array} children - Hidden message children to process
 * @returns {Array} Rendered message components
 */
window.dash_clientside.vizroChatComponent.renderMessages = (
  children,
  linkTarget,
) => {
  const CODE_BLOCK_REGEX = /```(\w+)?\n([\s\S]*?)```/g;

  // Component factory helpers
  const createComponent = (type, namespace, props) => ({
    type,
    namespace,
    props,
  });

  const createMarkdown = (text) =>
    createComponent("Markdown", "dash_core_components", {
      children: text,
      dangerously_allow_html: false,
      link_target: linkTarget || "_blank",
      className: "assistant-markdown",
    });

  const createCodeHighlight = (code, language) =>
    createComponent("CodeHighlight", "dash_mantine_components", {
      code: code.trim(),
      language: language || "text",
      withLineNumbers: false,
    });

  const createDivWithClass = (children, className) =>
    createComponent("Div", "dash_html_components", { children, className });

  // Parse content into markdown and code blocks
  function parseContent(content) {
    const parts = [];
    let lastIndex = 0;
    CODE_BLOCK_REGEX.lastIndex = 0; // Reset regex state

    let match = CODE_BLOCK_REGEX.exec(content);
    while (match !== null) {
      const [, language, code] = match;

      // Add preceding text as markdown
      if (match.index > lastIndex) {
        const text = content.slice(lastIndex, match.index).trim();
        if (text) parts.push(createMarkdown(text));
      }

      // Add code block
      parts.push(createCodeHighlight(code, language));
      lastIndex = CODE_BLOCK_REGEX.lastIndex;

      match = CODE_BLOCK_REGEX.exec(content);
    }

    // Add trailing text
    const trailing = content.slice(lastIndex).trim();
    if (trailing) parts.push(createMarkdown(trailing));

    return parts;
  }

  // Main processing
  if (!children?.length) return [];

  return children.map((msg) => {
    // Skip if no props
    if (!msg?.props?.children) return msg;

    // Handle simple structure: [role, content]
    if (Array.isArray(msg.props.children) && msg.props.children.length >= 2) {
      const [roleDiv, contentDiv] = msg.props.children;
      const role = roleDiv?.props?.children;
      const content = contentDiv?.props?.children;

      // Only wrap messages with the placeholder shape that processStreamingChunk
      // emits for incoming text: [hidden role-marker div, raw-text div]. Pre-styled
      // messages from _message_to_html (e.g. wrapper > [attachments, bubble]) must
      // pass through untouched — re-wrapping them would strip the attachments div.
      if (role !== "user" && role !== "assistant") return msg;
      if (typeof content !== "string") return msg;

      // Apply styling based on role
      if (role === "user") {
        // User message: styled div with text using CSS classes
        return createDivWithClass(
          createDivWithClass(
            createDivWithClass(content, CSS_USER_TEXT),
            `${CSS_MESSAGE_BUBBLE} ${CSS_USER_MESSAGE}`,
          ),
          CSS_MESSAGE_WRAPPER,
        );
      } else {
        // Assistant message: parse for code blocks
        if (/```/g.test(content)) {
          // Has code blocks - parse and use CodeHighlight
          const parts = parseContent(content);
          if (parts.length > 0) {
            return createDivWithClass(
              createDivWithClass(
                createDivWithClass(parts, null),
                `${CSS_MESSAGE_BUBBLE} ${CSS_ASSISTANT_MESSAGE}`,
              ),
              CSS_MESSAGE_WRAPPER,
            );
          }
        }
        // No code blocks - use regular Markdown
        return createDivWithClass(
          createDivWithClass(
            createMarkdown(content),
            `${CSS_MESSAGE_BUBBLE} ${CSS_ASSISTANT_MESSAGE}`,
          ),
          CSS_MESSAGE_WRAPPER,
        );
      }
    }

    // Return unchanged if structure doesn't match
    return msg;
  });
};

// ==================== Enter Key Handler ====================

/**
 * Sets up Enter key handler for a chat input.
 * Submits on Enter, allows Shift+Enter for new lines.
 */
window.dash_clientside.vizroChatComponent.setupEnterKeyHandler = (
  value,
  inputId,
) => {
  const chatInput = document.getElementById(inputId);
  if (!chatInput || chatInput.dataset.listenerAdded) {
    return window.dash_clientside.no_update;
  }

  const componentId = inputId.substring(0, inputId.lastIndexOf("-chat-input"));
  chatInput.dataset.listenerAdded = "true";
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const sendButton = document.getElementById(`${componentId}-send-button`);
      if (sendButton && chatInput.value.trim()) {
        sendButton.click();
      }
    }
  });
  return window.dash_clientside.no_update;
};

// ==================== Popup Helpers ====================

/**
 * Renders messages with link_target="_self" for popup navigation.
 */
window.dash_clientside.vizroChatComponent.renderMessagesInPopup = (
  children,
) => {
  return window.dash_clientside.vizroChatComponent.renderMessages(
    children,
    "_self",
  );
};

/**
 * Toggles the popup panel open/closed.
 */
window.dash_clientside.vizroChatComponent.togglePanel = (n, currentClass) => {
  const isOpen = currentClass?.includes("chat-popup-panel-open");
  return isOpen ? "chat-popup-panel" : "chat-popup-panel chat-popup-panel-open";
};

/**
 * Closes the popup panel.
 */
window.dash_clientside.vizroChatComponent.closePanel = () => "chat-popup-panel";

/**
 * Clears the chat history.
 */
window.dash_clientside.vizroChatComponent.clearChat = () => [[], []];
