"""SQL Agent processor for handling SQL queries through chat."""

import os
from pathlib import Path
from typing import Annotated, Any, Literal, Iterator

import requests
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableWithFallbacks
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import json

from vizro_chat.processors import ChatProcessor
from langsmith import traceable


class SQLAgentProcessor(ChatProcessor):
    """Processor for handling SQL queries through chat using LangChain and LangGraph."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """Initialize the SQL Agent processor.
        
        Args:
            model: The OpenAI model to use
            temperature: The temperature parameter for the model
        """
        self.model = model
        self.temperature = temperature
        self._setup_database()
        self._setup_tools()
        self._setup_workflow()

    def _setup_database(self):
        """Set up the SQLite database."""
        # Download the database if it doesn't exist
        db_path = Path("Chinook.db")
        if not db_path.exists():
            url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
            response = requests.get(url)
            if response.status_code == 200:
                db_path.write_bytes(response.content)
            else:
                raise RuntimeError(f"Failed to download database: {response.status_code}")

        self.db = SQLDatabase.from_uri("sqlite:///Chinook.db")

    def _setup_tools(self):
        """Set up the tools for the SQL agent."""
        # Create toolkit and get tools
        toolkit = SQLDatabaseToolkit(db=self.db, llm=ChatOpenAI(model=self.model))
        tools = toolkit.get_tools()
        
        self.list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
        self.get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

        # Define the query tool with query extraction
        @tool
        def db_query_tool(query: str) -> str:
            """Execute a SQL query against the database and get back the result."""

            result = self.db.run_no_throw(query)
            if not result:
                return "Error: Query failed. Please rewrite your query and try again."
            return result

        self.db_query_tool = db_query_tool

    def _create_tool_node_with_fallback(self, tools: list) -> RunnableWithFallbacks[Any, dict]:
        """Create a ToolNode with a fallback to handle errors."""
        return ToolNode(tools).with_fallbacks(
            [RunnableLambda(self._handle_tool_error)], exception_key="error"
        )

    def _handle_tool_error(self, state) -> dict:
        """Handle tool errors by returning an error message."""
        error = state.get("error")
        tool_calls = state["messages"][-1].tool_calls
        return {
            "messages": [
                ToolMessage(
                    content=f"Error: {repr(error)}\n please fix your mistakes.",
                    tool_call_id=tc["id"],
                )
                for tc in tool_calls
            ]
        }

    def _setup_workflow(self):
        """Set up the workflow for the SQL agent."""
        # Define the state with additional context fields
        class State(TypedDict):
            messages: Annotated[list[AnyMessage], add_messages]
            relevant_schemas: dict[str, str]  # Table name to schema mapping
            query: str | None  # Store the generated query
            query_result: str | None  # Store the query result

        workflow = StateGraph(State)

        # Add nodes for each step in the workflow
        workflow.add_node("select_relevant_schemas", self._select_schemas)
        workflow.add_node("generate_query", self._generate_query)
        workflow.add_node("execute_query", self._execute_query)
        workflow.add_node("generate_answer", self._generate_answer)

        # Add edges
        workflow.add_edge(START, "select_relevant_schemas")
        workflow.add_conditional_edges(
            "select_relevant_schemas",
            self._should_continue_schema_selection,
            {
                "generate_query": "generate_query",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "generate_query",
            self._should_continue_query_gen,
            {
                "execute_query": "execute_query",
                "select_relevant_schemas": "select_relevant_schemas",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "execute_query",
            self._should_continue_execution,
            {
                "generate_answer": "generate_answer",
                "generate_query": "generate_query",
                "end": END
            }
        )
        workflow.add_edge("generate_answer", END)

        self.graph = workflow.compile()

    def _select_schemas(self, state: dict) -> dict:
        """Select relevant schemas based on the user question."""
        system_prompt = """You are a SQL expert. Your task is to:
        1. Determine if the user's question can be answered using the database
        2. If yes, identify the relevant tables needed
        3. If no, explain why the question cannot be answered
        Only retrieve schemas for tables that are actually needed.
        Use the get_schema tool for each relevant table."""
        
        messages = state["messages"]
        question = messages[-1].content
        
        # First list all tables
        tables = self.list_tables_tool.invoke({})  # Empty dict for list_tables
        
        # Then get schemas for relevant tables
        model = ChatOpenAI(model=self.model, temperature=0).bind_tools(
            [self.list_tables_tool, self.get_schema_tool]
        )
        schema_result = model.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Available tables: {tables}\nQuestion: {question}"}
        ])
        
        # Extract table names and schemas from the tool calls
        schemas = {}
        if hasattr(schema_result, "additional_kwargs"):
            tool_calls = schema_result.additional_kwargs.get("tool_calls", [])
            for call in tool_calls:
                if call["function"]["name"] == "sql_db_schema":
                    # Parse the JSON string in arguments
                    try:
                        args = json.loads(call["function"]["arguments"])
                        table_names = args.get("table_names")
                        if table_names:
                            schema = self.get_schema_tool.invoke(table_names)
                            # Split schema result for individual tables
                            table_list = [t.strip() for t in table_names.split(",")]
                            for table in table_list:
                                schemas[table] = schema
                    except json.JSONDecodeError:
                        continue  # Skip if JSON parsing fails
        
        if not schemas:
            # Fallback: get all table schemas
            schema = self.get_schema_tool.invoke(tables)
            table_list = [t.strip() for t in tables.split(",")]
            for table in table_list:
                schemas[table] = schema
        
        return {
            "messages": [schema_result],
            "relevant_schemas": schemas,
            "query": None,
            "query_result": None
        }

    def _generate_query(self, state: dict) -> dict:
        """Generate and validate SQL query."""
        system_prompt = """You are a SQL expert. Generate a SQLite query to answer the question.
        Rules:
        1. Only use tables mentioned in the schema
        2. Limit results to 5 rows unless specified otherwise
        3. Only query relevant columns
        4. Never use DML statements (INSERT, UPDATE, DELETE)
        5. Validate the query for common SQL mistakes"""
        
        messages = state["messages"]
        schemas = state["relevant_schemas"]
        
        # Format schemas for the prompt
        schema_text = "\n".join(f"Table {table}:\n{schema}" for table, schema in schemas.items())
        
        query_gen = ChatOpenAI(model=self.model, temperature=0)
        result = query_gen.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Schemas:\n{schema_text}\n\nQuestion: {messages[-2].content}"}
        ])
        
        # Extract the SQL query from the response
        query = result.content.strip()
        
        # Extract query from markdown code block if present
        if "```" in query:
            import re
            # Look for SQL block with optional 'sql' language identifier
            sql_block_match = re.search(r"```(?:sql)?\s*(.+?)\s*```", query, re.DOTALL)
            if sql_block_match:
                query = sql_block_match.group(1).strip()
        
        # Remove any remaining markdown formatting or comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)  # Remove SQL comments
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)  # Remove multi-line SQL comments
        query = query.strip()
        
        return {
            "messages": [result],
            "relevant_schemas": state["relevant_schemas"],
            "query": query,
            "query_result": None
        }

    def _execute_query(self, state: dict) -> dict:
        """Execute the SQL query and handle errors."""
        query = state["query"]
        result = self.db_query_tool.invoke(query)
        
        return {
            "messages": [AIMessage(content=result)],
            "relevant_schemas": state["relevant_schemas"],
            "query": query,
            "query_result": result
        }

    def _generate_answer(self, state: dict) -> dict:
        """Generate a natural language answer from the query results."""
        system_prompt = """Generate a clear, concise answer based on the query results.
        1. Format numbers and dates appropriately
        2. Provide context when needed
        3. Be direct and to the point"""
        
        class SubmitFinalAnswer(BaseModel):
            """Submit the final answer to the user."""
            final_answer: str = Field(..., description="The final answer to the user")

        query = state["query"]
        query_result = state["query_result"]
        schemas = state["relevant_schemas"]
        
        # Format context for answer generation
        context = f"""
        Query executed: {query}
        Result: {query_result}
        Tables used: {', '.join(schemas.keys())}
        """
        
        answer_gen = ChatOpenAI(model=self.model, temperature=0).bind_tools([SubmitFinalAnswer])
        result = answer_gen.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ])
        
        return {
            "messages": [result],
            "relevant_schemas": state["relevant_schemas"],
            "query": query,
            "query_result": query_result
        }

    def _should_continue_schema_selection(self, state: dict) -> Literal["generate_query", "end"]:
        """Decide whether to proceed with query generation or end."""
        last_message = state["messages"][-1]
        if "cannot be answered" in last_message.content.lower():
            return "end"
        return "generate_query"

    def _should_continue_query_gen(self, state: dict) -> Literal["execute_query", "select_relevant_schemas", "end"]:
        """Decide whether to execute query, reselect schemas, or end."""
        if not hasattr(self, '_query_retry_count'):
            self._query_retry_count = 0
            
        last_message = state["messages"][-1]
        if "Error:" in last_message.content:
            if self._query_retry_count < 2:
                self._query_retry_count += 1
                return "select_relevant_schemas"
            self._query_retry_count = 0
            return "end"
        return "execute_query"

    def _should_continue_execution(self, state: dict) -> Literal["generate_answer", "generate_query", "end"]:
        """Decide whether to generate answer, retry query, or end."""
        if not hasattr(self, '_execution_retry_count'):
            self._execution_retry_count = 0
            
        last_message = state["messages"][-1]
        if "Error:" in last_message.content:
            if self._execution_retry_count < 2:
                self._execution_retry_count += 1
                return "generate_query"
            self._execution_retry_count = 0
            return "end"
        return "generate_answer"

    @traceable
    def get_response(self, messages: list[dict[str, str]], user_prompt: str) -> Iterator[str]:
        """Generate response for the user's SQL query."""
        try:
            from langchain_core.messages import HumanMessage
            
            # Initialize state with empty context
            initial_state = {
                "messages": [HumanMessage(content=user_prompt)],
                "relevant_schemas": {},
                "query": None,
                "query_result": None
            }
            
            # Stream chunks and ensure we're yielding strings
            for message_chunk, metadata in self.graph.stream(initial_state, stream_mode="messages"):
                yield str(message_chunk.content)
                    
        except Exception as e:
            yield f"Error in SQL processing: {str(e)}"
