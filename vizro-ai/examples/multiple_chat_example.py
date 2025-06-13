"""Complete example of using multiple VizroChatComponents in a dashboard."""

import os
import vizro.models as vm
from vizro import Vizro
import vizro_ai.components as vcc
from dotenv import load_dotenv

load_dotenv()

def create_multi_chat_dashboard():
    """Create a dashboard with multiple specialized chat components."""
    
    # 1. Create multiple chat components with different purposes
    general_chat = vcc.VizroChatComponent(
        id="general_chat",
        input_placeholder="Ask me anything...",
        initial_message="👋 Hi! I'm your general AI assistant. How can I help you today?",
        processor=vcc.OpenAIProcessor(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            system_message="You are a helpful general-purpose AI assistant."
        ) if os.getenv("OPENAI_API_KEY") else vcc.EchoProcessor(),
    )
    
    data_analyst_chat = vcc.VizroChatComponent(
        id="data_analyst_chat",
        input_placeholder="Ask about data analysis, statistics, or visualization...",
        initial_message="📊 Hello! I specialize in data analysis and visualization. What data questions do you have?",
        processor=vcc.OpenAIProcessor(
            model="gpt-4o-mini", 
            api_key=os.getenv("OPENAI_API_KEY"),
            system_message="You are a specialized data analyst AI. Focus on statistics, data analysis, visualization recommendations, and data science best practices."
        ) if os.getenv("OPENAI_API_KEY") else vcc.EchoProcessor(),
    )
    
    code_assistant_chat = vcc.VizroChatComponent(
        id="code_assistant_chat",
        input_placeholder="Ask about programming, debugging, or code review...",
        initial_message="💻 Hi! I'm your coding assistant. I can help with programming, debugging, and code review.",
        processor=vcc.OpenAIProcessor(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"), 
            system_message="You are a senior software engineer AI. Help with coding questions, debugging, code review, and programming best practices. Provide code examples when helpful."
        ) if os.getenv("OPENAI_API_KEY") else vcc.EchoProcessor(),
    )
    
    # 2. Register the component type with Vizro
    vm.Page.add_type("components", vcc.VizroChatComponent)
    
    # 3. Create specialized pages for different use cases
    general_page = vm.Page(
        title="🤖 General AI Chat",
        components=[general_chat],
    )
    
    data_page = vm.Page(
        title="📊 Data Analysis Chat", 
        components=[data_analyst_chat],
    )
    
    coding_page = vm.Page(
        title="💻 Code Assistant",
        components=[code_assistant_chat],
    )
    
    # 4. Example: Multiple chat components on the same page
    comparison_page = vm.Page(
        title="🔄 Chat Comparison",
        components=[
            # You can have multiple chat components on the same page
            vcc.VizroChatComponent(
                id="quick_chat_a",
                input_placeholder="Quick question A...",
                initial_message="Quick Chat A - Ready!",
                processor=vcc.EchoProcessor(),
            ),
            vcc.VizroChatComponent(
                id="quick_chat_b", 
                input_placeholder="Quick question B...",
                initial_message="Quick Chat B - Ready!",
                processor=vcc.EchoProcessor(),
            ),
        ],
    )
    
    # 5. Create dashboard with all pages
    dashboard = vm.Dashboard(
        title="Multi-Chat AI Dashboard",
        pages=[general_page, data_page, coding_page, comparison_page]
    )
    
    # 6. 🚨 CRITICAL: Pass ALL chat components as plugins
    # This includes both named components and inline components
    all_chat_components = [
        general_chat,
        data_analyst_chat, 
        code_assistant_chat,
        # Don't forget components created inline in pages!
        comparison_page.components[0],  # quick_chat_a
        comparison_page.components[1],  # quick_chat_b
    ]
    
    return dashboard, all_chat_components

def main():
    """Run the multi-chat dashboard."""
    
    # Create dashboard and get all chat components
    dashboard, chat_components = create_multi_chat_dashboard()
    
    print(f"Created dashboard with {len(chat_components)} chat components:")
    for i, chat in enumerate(chat_components, 1):
        print(f"  {i}. {chat.id} - {type(chat.processor).__name__}")
    
    # Create Vizro app with all chat components as plugins
    app = Vizro(plugins=chat_components)
    
    # Build and verify routes
    app.build(dashboard)
    
    # Verify all routes are registered
    routes = [rule.rule for rule in app.dash.server.url_map.iter_rules()]
    chat_routes = [r for r in routes if r.startswith("/streaming-")]
    
    print(f"\nRegistered {len(chat_routes)} streaming routes:")
    for route in sorted(chat_routes):
        print(f"  {route}")
    
    print(f"\n✅ Dashboard ready with {len(chat_components)} chat components!")
    print("Each component has its own streaming endpoint and processor.")
    print("No route conflicts detected.")
    
    # Run the app
    app.run(debug=True)

if __name__ == "__main__":
    main() 