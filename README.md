# DeepAgent Gen UI Example

A demonstration of [LangGraph's Generative UI capabilities](https://docs.langchain.com/langsmith/generative-ui-react) with a DeepAgent that generates CSV and PDF reports. This example shows how to build an AI agent that not only processes data but also renders rich, interactive UI components dynamically.

> **📚 Based on:** [LangChain Generative UI React Documentation](https://docs.langchain.com/langsmith/generative-ui-react)

## ✨ Features

- 📊 **CSV Report Generation** with interactive table preview
- 📄 **PDF Report Generation** with inline preview
- 🎨 **Professional UI** with inline styles for consistent rendering
- 🔄 **Research Subagent** pattern - separates data fetching from UI generation
- ⚡ **GenUI Middleware** for automatic UI component rendering
- 🏗️ **DeepAgent Architecture** - supervisor agent coordinating specialized subagents

## 🎬 Demo

When you ask: *"Generate a CSV report on user analytics"*

The agent will:
1. Delegate to the research subagent to fetch data
2. Generate a CSV report with the data
3. Automatically render an interactive table in the UI with download button

The same flow works for PDF reports with inline preview!

## 🌟 What Makes This Example Special

This example demonstrates several advanced patterns:

1. **GenUI Middleware Pattern**: Automatically intercepts tool calls and pushes UI messages without cluttering your agent logic
2. **Subagent Delegation**: Main agent delegates data fetching to a specialized subagent, maintaining clean separation of concerns
3. **Tool Result Integration**: UI components read tool execution results via `useStreamContext()` metadata, not props
4. **Professional UI Components**: Self-contained React components with inline styles for consistent rendering across different frontends
5. **Base64 Data Transfer**: Handles binary data (PDFs) and text data (CSVs) seamlessly through base64 encoding

This pattern can be extended to any tool that generates visual outputs: charts, diagrams, forms, 3D visualizations, etc.

## 🏗️ Architecture

```
Main Agent (deepagent.py)
├── Tools: generate_csv_report, generate_pdf_report
├── Middleware: GenUIMiddleware
└── Subagents:
    └── Research Subagent (subagents.py)
        └── Tools: get_sales_data, get_user_analytics
```

**Key Pattern:** The main agent delegates data fetching to a research subagent, then uses the data to generate reports. The GenUI middleware automatically detects report generation tools and pushes UI messages to render React components in the frontend.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for UI dependencies)
- LangGraph CLI or LangGraph Studio
- An Anthropic or OpenAI API key

### 1. Install Python Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Install JavaScript Dependencies

```bash
yarn install
# or
npm install
```

### 3. Set up Environment Variables

Create a `.env` file with your API keys:

```bash
ANTHROPIC_API_KEY=your_key_here
# or
OPENAI_API_KEY=your_key_here
```

### 4. Or Run with LangGraph CLI

```bash
langgraph dev
```

Then connect with a frontend like [Deep Agents UI](https://github.com/langchain-ai/deep-agents-ui) or build your own using `@langchain/langgraph-sdk`.

## 💬 Example Queries

Try these prompts to see the GenUI in action:

- *"Generate a CSV report on user analytics"*
- *"Create a PDF report for sales data"*
- *"Show me user analytics for this month in a CSV"*
- *"Generate a sales report in PDF format"*

## 🖥️ Frontend Options

This example requires a frontend to visualize the GenUI components. You have a few options:

1. **[Deep Agents UI](https://github.com/langchain-ai/deep-agents-ui/tree/main)** - Pre-built chat interface
2. **Custom Frontend** - Build your own using `@langchain/langgraph-sdk` and `useStream()` hook

For custom frontends, see the [LangChain GenUI React docs](https://docs.langchain.com/langsmith/generative-ui-react).

## Project Structure

```
deepagent-gen-ui/
├── deepagent.py          # Main agent with UI generation tools
├── subagents.py          # Research subagent for data fetching
├── ui_middleware.py      # Middleware for GenUI integration
├── ui.tsx                # React components for CSV/PDF preview
├── langgraph.json        # LangGraph configuration
├── package.json          # JS dependencies (React, Tailwind)
├── pyproject.toml        # Python dependencies
└── README.md             # This file
```

## How It Works

### 1. User Request
User asks: "Generate a CSV on user analytics"

### 2. Main Agent Delegates
The main agent calls the `research-specialist` subagent to fetch data

### 3. Data Fetching
The subagent uses `get_user_analytics()` tool to retrieve mock data

### 4. Report Generation
The main agent receives the data and calls `generate_csv_report(data=...)`

### 5. Middleware Intercepts
`GenUIMiddleware` detects the tool call and pushes a UI message with empty props

### 6. React Component Renders
The `CSVPreview` component:
- Reads tool result from `useStreamContext()`
- Parses the base64 CSV data
- Displays an interactive table with download button

## Customization

### Adding New Report Types

1. **Create the tool** in `deepagent.py`:
```python
@tool
def generate_excel_report(data: dict, report_title: str = "Report") -> dict:
    # Your implementation
    return {"data": excel_base64, "filename": filename}
```

2. **Add to main agent tools**:
```python
graph = create_deep_agent(
    tools=[generate_csv_report, generate_pdf_report, generate_excel_report],
    # ...
)
```

3. **Update middleware mapping**:
```python
genui_middleware = GenUIMiddleware(
    tool_to_genui_map={
        "generate_csv_report": {"component_name": "csv_preview"},
        "generate_pdf_report": {"component_name": "pdf_preview"},
        "generate_excel_report": {"component_name": "excel_preview"},
    }
)
```

4. **Create React component** in `ui.tsx`:
```typescript
const ExcelPreview = () => {
  const context = useStreamContext();
  // Your component implementation
};

export default {
  csv_preview: CSVPreview,
  pdf_preview: PDFPreview,
  excel_preview: ExcelPreview,
};
```

### Styling

The UI components use Tailwind CSS. Customize by modifying classes in `ui.tsx`:

```typescript
// Example: Change button color
className="bg-blue-600 hover:bg-blue-700"  // Current
className="bg-purple-600 hover:bg-purple-700"  // Custom
```

## Key Concepts

### GenUI Middleware Pattern - How It Works

When you look at the middleware code, you'll see:

```python
push_ui_message(
    component_name,
    {},  # <-- Empty props! Why?
    metadata={
        "tool_call_id": tool_call["id"],
        "message_id": last_message.id
    },
    message=last_message
)
```

**Why empty props?** Because `after_model()` runs **after the LLM decides to call a tool, but before the tool executes**. The tool result doesn't exist yet!

#### The Complete Flow

```
1. User: "Generate CSV report"
   ↓
2. LLM: Decides to call generate_csv_report(data=...)
   ↓
3. Middleware (after_model): 
   - Detects the tool call
   - Pushes UI message: csv_preview with {} empty props
   - Includes metadata linking tool_call_id
   ↓
4. Frontend: 
   - Renders CSVPreview component immediately
   - Shows "pending" state (spinner)
   ↓
5. Tool Executes:
   - generate_csv_report() returns {"data": "...", "filename": "..."}
   ↓
6. Frontend Updates Automatically:
   - useStreamContext() receives tool result via metadata link
   - CSVPreview re-renders with actual data
   - Shows interactive table with download button
```

#### Why This Design

1. **Immediate Feedback**: UI renders instantly when tool is called, showing loading state
2. **Separation of Concerns**: Middleware doesn't need to know about tool results
3. **Automatic Updates**: LangGraph framework handles linking tool results to UI via `tool_call_id`
4. **Stateless Middleware**: No need to track execution or store results
5. **Flexible Data Flow**: React components parse tool results however they want

#### The Magic: Metadata Linking

The `metadata` passed to `push_ui_message` tells LangGraph:

> "When the tool call with this ID completes, send its result to this UI component"

The framework handles all the wiring automatically! The React component just reads from `useStreamContext()` and gets the result when it's ready.

### React Components with useStreamContext

Components don't use props - they read tool results from stream context:

```typescript
const context = useStreamContext();
const meta = context?.meta as any;
const result = meta?.result;  // Tool execution result (arrives after tool runs)
const status = meta?.status;  // pending/completed/error
```

The component lifecycle:
1. **Initial render**: `status: "pending"`, `result: null` → Show spinner
2. **Tool completes**: `status: "completed"`, `result: {...}` → Parse and display data
3. **Tool fails**: `status: "error"` → Show error message

### Tool Result Format

Tools return base64-encoded data with metadata:

```python
return {
    "data": base64_encoded_content,
    "filename": "report.csv",
    "rows": 5,
    "columns": ["date", "users", "signups"]
}
```

## Troubleshooting

### UI Components Not Showing

1. Check `langgraph.json` has the UI mapping:
```json
{
  "ui": {
    "agent": "./ui.tsx"
  }
}
```

2. Verify middleware is attached to the main agent (not subagent)

3. Check browser console for errors in React components

### Empty Props in UI

The middleware pushes empty props intentionally. Components read data from `useStreamContext().meta.result`, not from props.

### Tailwind Styles Not Applied

Make sure your frontend (LangGraph Studio or custom UI) processes Tailwind CSS. The components use standard Tailwind classes that should work automatically.

## Dependencies

### Python
- `deepagents>=0.2.6` - DeepAgent framework
- `langchain-openai>=1.0.2` - LLM integration
- `langgraph-cli[inmem]>=0.4.7` - LangGraph CLI
- `reportlab>=4.4.4` - PDF generation

### JavaScript
- `react@^18.3.1` - UI framework
- `@langchain/langgraph-sdk@^0.1.0` - LangGraph React hooks
- `tailwindcss@^4.0.0` - Styling

## 📚 Learn More

- [LangGraph Generative UI React Documentation](https://docs.langchain.com/langsmith/generative-ui-react)
- [DeepAgents Documentation](https://github.com/langchain-ai/deep-agents)

## 🤝 Contributing

This is an example project demonstrating GenUI patterns. Feel free to fork and adapt for your use cases!

## 📄 License

MIT

