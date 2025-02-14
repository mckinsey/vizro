if (!window.dash_clientside) {
  window.dash_clientside = {};
}
if (!window.dash_clientside.clientside) {
  window.dash_clientside.clientside = {};
}

window.dash_clientside.clientside.streaming_GPT = async function (
  n_clicks,
  n_submit,
  user_input,
  messages_json,
) {
  // Check if either button was clicked or Enter was pressed
  if ((!n_clicks && !n_submit) || !user_input || !messages_json) {
    return messages_json;
  }

  try {
    const messages = JSON.parse(messages_json);
    const chatHistory = document.getElementById("cnx-assistant-history");

    // Add user message
    messages.push({ role: "user", content: user_input });

    // Create user message div first
    const userDiv = document.createElement("div");
    userDiv.textContent = user_input;
    // userDiv.style.backgroundColor = "#00b4ff";
    userDiv.style.backgroundColor = "var(--mantine-color-dark-light-hover)";
    userDiv.style.color = "var(--text-primary)";
    // userDiv.style.color = "white";
    userDiv.style.padding = "10px 15px";
    userDiv.style.maxWidth = "70%";
    userDiv.style.marginRight = "auto";
    userDiv.style.marginBottom = "15px";
    userDiv.style.whiteSpace = "pre-wrap";
    userDiv.style.wordBreak = "break-word";
    userDiv.style.width = "fit-content";
    userDiv.style.minWidth = "100px";
    userDiv.style.lineHeight = "1.25";
    userDiv.style.letterSpacing = "0.2px";
    userDiv.style.borderLeft = "2px solid #00b4ff";

    if (chatHistory) {
      chatHistory.appendChild(userDiv);
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Return immediately to update UI with user message
    setTimeout(() => {
      // Create streaming message div
      const streamingDiv = document.createElement("div");
      streamingDiv.style.backgroundColor =
        "var(--mantine-color-dark-light-hover)";
      streamingDiv.style.color = "var(--text-primary)";
      streamingDiv.style.padding = "10px 15px";
      streamingDiv.style.maxWidth = "70%";
      streamingDiv.style.marginRight = "auto";
      streamingDiv.style.marginBottom = "15px";
      streamingDiv.style.whiteSpace = "pre-wrap";
      streamingDiv.style.wordBreak = "break-word";
      streamingDiv.style.width = "fit-content";
      streamingDiv.style.minWidth = "100px";
      streamingDiv.style.lineHeight = "1.25";
      streamingDiv.style.letterSpacing = "0.2px";
      streamingDiv.style.borderLeft = "2px solid #aaa9ba";

      if (chatHistory) {
        chatHistory.appendChild(streamingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
      }

      // Start streaming
      fetch("/streaming-chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: user_input,
          chat_history: JSON.stringify(messages.slice(0, -1)),
        }),
      }).then((response) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let text = "";

        function readChunk() {
          reader.read().then(({ done, value }) => {
            if (done) {
              // Add assistant response to messages and update store
              messages.push({ role: "assistant", content: text.trim() });
              window.dash_clientside.callback_context = {
                triggered: { prop_id: "cnx-assistant-messages.data" },
              };
              return;
            }

            const chunk = decoder.decode(value);
            text += chunk;
            streamingDiv.textContent = text;

            if (chatHistory) {
              chatHistory.scrollTop = chatHistory.scrollHeight;
            }

            readChunk();
          });
        }

        readChunk();
      });
    }, 0);

    return JSON.stringify(messages);
  } catch (error) {
    console.error("Streaming error:", error);
    return messages_json;
  }
};
