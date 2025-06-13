# VizroChatComponent Architecture Documentation

## Overview

VizroChatComponent is a chat interface built for Vizro dashboards that provides smooth streaming responses with rich markdown support. It features a plugin-based architecture that separates data processing from UI rendering, enabling easy integration with different AI services.

## 🏗️ Architecture Design

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐
│   Data Source   │ -> │   ChatProcessor  │ -> │ VizroChatComponent│
│  (LLM/AI API)   │    │   (Plugin API)   │    │   (UI Component)  │
└─────────────────┘    └──────────────────┘    └───────────────────┘
```

### 1. **ChatProcessor Layer** (Data Processing)
- **Responsibility**: Convert various data sources into standardized `ChatMessage` objects
- **Interface**: Abstract base class with `get_response()` method
- **Output**: Stream of typed `ChatMessage` objects
- **Flexibility**: Easy to implement custom processors for different AI services

### 2. **VizroChatComponent Layer** (UI & Experience)
- **Responsibility**: Handle all UI concerns, animations, user interactions
- **Features**: Smooth streaming, markdown rendering, clipboard functionality
- **Performance**: Client-side buffering and animation for optimal UX

### 3. **Communication Layer** (SSE Streaming)
- **Technology**: Server-Sent Events (SSE) for real-time streaming
- **Format**: JSON-serialized `ChatMessage` objects
- **Benefits**: Low latency, automatic reconnection, browser-native support

## 📊 Data Flow Architecture

### Complete Data Flow Pipeline

```
[LLM Token Stream] 
        ↓
[ChatProcessor.get_response()]
        ↓ 
[ChatMessage Objects]
        ↓
[JSON Serialization]
        ↓
[SSE Stream]
        ↓
[VizroChatComponent Callbacks]
        ↓
[Client-side Buffer]
        ↓
[Smooth Animation]
        ↓
[Rendered UI]
```

### Step-by-Step Flow

1. **Data Source** → Raw tokens/chunks from LLM or AI service
2. **Processor** → Parses and structures data into `ChatMessage` objects
3. **Serialization** → Converts to JSON for network transmission
4. **SSE Streaming** → Real-time streaming to browser
5. **Component Callbacks** → Server-side Dash callbacks receive data
6. **Buffer Management** → Accumulates content in client-side buffer
7. **Animation Engine** → Smooth character-by-character rendering
8. **UI Rendering** → Final display with markdown, syntax highlighting, clipboard

## 🔧 Special Design Features

### 1. Streaming Buffer System

**Purpose**: Provide smooth, consistent animation regardless of irregular token arrival from LLMs.

**How It Works**:
```python
# Server-side: Accumulate all received content
stream_buffer = ""
for message in sse_stream:
    stream_buffer += message.content

# Client-side: Smooth character-by-character rendering
render_position = 0
timer_interval = 33ms  # ~30fps

def animate_frame():
    if render_position < len(stream_buffer):
        chars_to_add = min(4, len(stream_buffer) - render_position)
        render_position += chars_to_add
        display_content = stream_buffer[:render_position]
        update_ui(display_content)
```

**Benefits**:
- Consistent typing speed regardless of network irregularities
- Smooth visual experience similar to ChatGPT/Claude
- Decouples data arrival from visual presentation

### 2. Server-Sent Events (SSE) Integration

**Why SSE**: 
- Browser-native streaming support
- Automatic reconnection handling
- Lower overhead than WebSockets for one-way communication
- Works through proxies and firewalls

**Implementation**:
```python
# Server-side streaming endpoint
@app.route("/streaming-{component_id}", methods=["POST"])
def streaming_chat():
    def response_stream():
        for chat_message in processor.get_response(messages, prompt):
            yield sse_message(chat_message.to_json())
        yield sse_message()  # Signal completion
    
    return Response(response_stream(), mimetype="text/event-stream")

# Client-side SSE consumption
<SSE id="sse-component" url="/streaming-endpoint" />
```

### 3. Client-Side Animation Engine

**Smooth Rendering Algorithm**:
```javascript
function animate_stream(n_intervals, stream_buffer, render_position) {
    if (render_position < stream_buffer.length) {
        // Adaptive speed: faster for longer content
        const charsToAdd = Math.min(
            Math.max(2, Math.floor(stream_buffer.length / 100)), 
            4
        );
        const newPosition = Math.min(
            render_position + charsToAdd, 
            stream_buffer.length
        );
        
        return [newPosition, stream_buffer.slice(0, newPosition)];
    }
    
    // Animation complete
    return [no_update, no_update];
}
```

**Timer Management**:
- **Start**: When new content arrives
- **Stop**: When rendering is complete
- **Performance**: Uses `no_update` to prevent unnecessary re-renders

### 4. Safe Markdown Parsing During Streaming

**Challenge**: Incomplete markdown blocks can break rendering during streaming.

**Solution**: Parse incrementally with rollback capability:

```python
def parse_markdown_stream(token_stream):
    buffer = ""
    in_code_block = False
    
    for token in token_stream:
        buffer += token
        
        # Check for complete code block delimiters
        while "```" in buffer:
            before, delimiter, after = buffer.partition("```")
            
            if in_code_block:
                # Complete code block - safe to render
                yield ChatMessage(
                    type=MessageType.CODE,
                    content=before,
                    metadata={"language": code_language}
                )
                in_code_block = False
            else:
                # Starting code block
                if before.strip():
                    yield ChatMessage(type=MessageType.TEXT, content=before)
                in_code_block = True
```

**Benefits**:
- No broken markdown rendering during streaming
- Smooth transitions between text and code blocks
- Maintains syntax highlighting throughout the stream

### 5. Dynamic Clipboard System

**Architecture**: 
```javascript
// Detect new code blocks as they render
const codeBlocks = document.querySelectorAll('pre');

codeBlocks.forEach(pre => {
    // Create clipboard button with SVG icon
    const clipboardBtn = document.createElement('button');
    clipboardBtn.innerHTML = `<svg>...</svg>`;
    
    // Position in top-right corner
    clipboardBtn.style.position = 'absolute';
    clipboardBtn.style.top = '5px';
    clipboardBtn.style.right = '5px';
    
    // Copy functionality
    clipboardBtn.onclick = () => {
        navigator.clipboard.writeText(pre.textContent);
        showSuccessFeedback();
    };
    
    pre.appendChild(clipboardBtn);
});
```

**Features**:
- **Auto-detection**: Dynamically adds buttons to new code blocks
- **Visual feedback**: Icon changes to checkmark on successful copy
- **Claude-style UX**: Hidden until hover, smooth transitions

## 🔌 Plugin Architecture

### Creating Custom Processors

```python
from vizro_ai.components import ChatProcessor, ChatMessage, MessageType

class CustomProcessor(ChatProcessor):
    def get_response(self, messages, prompt):
        # Connect to your AI service
        response = my_ai_service.generate(prompt)
        
        # Stream character by character
        for char in response:
            yield ChatMessage(
                type=MessageType.TEXT,
                content=char
            )
        
        # Or yield complete blocks
        yield ChatMessage(
            type=MessageType.CODE,
            content="print('hello')",
            metadata={"language": "python"}
        )

# Use with VizroChatComponent
chat = VizroChatComponent(
    id="my-chat",
    processor=CustomProcessor()
)
```

### Supported Message Types

```python
class MessageType(str, Enum):
    TEXT = "text"      # Regular text content
    CODE = "code"      # Code blocks with syntax highlighting
    ERROR = "error"    # Error messages with special styling
```

### Message Schema

```python
class ChatMessage(BaseModel):
    type: MessageType = MessageType.TEXT
    content: str                              # The actual content
    metadata: Dict[str, Any] = {}            # Additional data (e.g., language for code)
    
    def to_json(self) -> str:
        return self.model_dump_json()
```

## 🎯 Performance Optimizations

### 1. **Efficient Re-rendering Prevention**
- Uses `dash.no_update` to prevent unnecessary component updates
- Separates buffer updates from visual rendering
- Client-side animation reduces server round-trips

### 2. **Memory Management**
- Streaming buffer is cleared between messages
- Clipboard buttons are cleaned up and recreated to prevent memory leaks
- Timer is properly disabled when animation completes

### 3. **Network Efficiency**
- SSE provides persistent connection for streaming
- JSON serialization minimizes payload size
- Graceful error handling prevents connection drops

## 🔧 Configuration Options

### Component Configuration

```python
VizroChatComponent(
    id="chat-component",
    input_placeholder="Ask me anything...",
    input_height="80px",
    button_text="Send",
    initial_message="Hello! How can I help?",
    processor=YourCustomProcessor()
)
```

### Styling Customization

The component uses CSS variables for theming:
- `--surfaces-bg-card`: Background colors
- `--text-primary`: Primary text color
- `--border-subtleAlpha01`: Border colors

### Animation Tuning

```javascript
// In client-side callback
const interval = 33;        // ~30fps animation
const charsPerFrame = 2-4;  // Adaptive speed
const maxIntervals = content_length / charsPerFrame;
```

## 🚀 Getting Started

### Basic Usage

```python
from vizro_ai.components import VizroChatComponent, OpenAIProcessor

# Create with OpenAI processor
chat = VizroChatComponent(
    id="ai-chat",
    processor=OpenAIProcessor(
        model="gpt-4o-mini",
        api_key="your-api-key"
    )
)

# Add to your Vizro page
page = vm.Page(
    title="AI Chat",
    components=[chat]
)
```

### Advanced Usage

```python
# Custom processor with agent framework
class AgentProcessor(ChatProcessor):
    def __init__(self, agent_config):
        self.agent = create_agent(agent_config)
    
    def get_response(self, messages, prompt):
        for step in self.agent.run_stream(prompt):
            if step.type == "thought":
                yield ChatMessage(
                    type=MessageType.TEXT,
                    content=f"💭 {step.content}",
                    metadata={"step_type": "reasoning"}
                )
            elif step.type == "code":
                yield ChatMessage(
                    type=MessageType.CODE,
                    content=step.content,
                    metadata={"language": step.language}
                )

# Use with custom processor
chat = VizroChatComponent(
    id="agent-chat",
    processor=AgentProcessor(agent_config)
)
```

## 🔍 Debugging & Development

### Console Debugging

The component logs useful information to browser console:
```javascript
// Check for clipboard functionality
console.log('Found code blocks:', codeBlocks.length);
console.log('Processing code block:', pre);

// Monitor animation state  
console.log('Animation position:', render_position);
console.log('Buffer length:', stream_buffer.length);
```

### Common Issues

1. **No streaming animation**: Check that timer is enabled and `supports_streaming=True`
2. **Clipboard not working**: Ensure HTTPS or localhost for clipboard API
3. **Markdown not rendering**: Verify CSS classes and selectors
4. **Memory leaks**: Check that timers are properly disabled

This architecture provides a robust, extensible foundation for building AI-powered chat interfaces in Vizro applications. 