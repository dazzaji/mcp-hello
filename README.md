# Incemental Model Context Protocol

This is a primative multi-agent modular initialization capability test prototype of Model Context Protocol.  

The purpose of this initial hello-mcp test is to create an mpc project that uses Claude Desktop as the client and it will create a markdown file that inserts content from an user's input into an existing markdown template including other content.

Template:

The user' goal is [inert the user input text here].  Subsquent work on this project will focus on achieving the user's goal.


# Future Roadmap:

## Example of future goal for multiple servers operating in a workflow

My further test project, after te initial hello-mcp test is working, will have multiple servers and clients.  They will operate in a modular way, the first will create a markdown file based on adding user input text to a content template and saving the file to root directory.  The second will ingest that file and add more info to it then save the updated version to the root.  The third will likewise ingest the output of the second and add still more content and export the third version of the file to the root.  Treat each of these three like back boxes in the sense that they will not share code or components but we will pretend they are running on different technologies to preserve the modular approach and we will for convenience be able to do things like share a virtual environment and requirements for this first test.  We work in VS Code on my mac.  See potential examples for ways to accomplish this in the Roadmap files from Gemini 1.5 and GPT-4o  [include all documentation for MCP]

---------

# POTENTIAL APPROACH


### **Project Structure**
```plaintext
mcp-hello/
├── module1/                # First module: Creates a markdown file
│   ├── src/
│   │   ├── create_markdown_server/
│   │   │   ├── __init__.py
│   │   │   ├── __main__.py
│   │   │   └── server.py
│   ├── pyproject.toml
├── shared_logs/            # Shared logging directory for visibility
├── .vscode/                # VS Code configurations
│   └── launch.json         # Debugging configurations
├── .env
└── README.md               # Documentation
```

### **Step 1: Setting up the Environment**

1.  **Create Project Directory:**

    ```bash
    mkdir mcp-hello
    cd mcp-hello
    ```

2.  **Create Virtual Environment:**

    ```bash
    uv venv
    ```

3.  **Activate Virtual Environment:**
    *   **macOS:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Install `create-mcp-server` and `mcp`:**

    ```bash
    uv pip install create-mcp-server mcp python-dotenv
    ```

### **Step 2: Scaffold the Server**

1.  **Create the Server:**
    ```bash
    uvx create-mcp-server module1/src/create_markdown_server
    ```

2.  When prompted, provide the following:
    *   Project Name: `markdown-creator`
    *   Project Description: `Creates a markdown file from user input and a template`
    *   Server Version: (leave default)
    *   Enable Claude.app integration?: `y`

### **Step 3: Implement Server Logic**

Replace the default content of the `src/create_markdown_server/server.py` file with the following code:

```python
import logging
import os
from pathlib import Path

import anyio
import mcp.types as types
from mcp.server import Server
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(dotenv_path="../../../.env")

# Set up logging
LOG_DIR = "../../../shared_logs/"  # Log to the shared logs directory
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "module1.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("MarkdownCreator")

# Define input model
class MarkdownInput(BaseModel):
    content: str = Field(..., description="The content of the markdown file.")

@server.call_tool()
async def create_markdown(arguments: dict) -> list[types.TextContent]:
    """Creates a markdown file with the provided content."""
    try:
        # Parse arguments using the input model
        input_data = MarkdownInput(**arguments)

        # Read content template
        template = "The user' goal is {content}. Subsequent work on this project will focus on achieving the user's goal."

        # Generate the markdown content using the template
        markdown_content = template.format(content=input_data.content)

        # Define output path
        file_path = os.path.join("../../../", "output.md")
        
        # Write content to the markdown file
        with open(file_path, "w") as file:
            file.write(markdown_content)

        logger.info(f"Markdown file created: {file_path}")
        return [
            types.TextContent(
                type="text", text=f"Created markdown file: {file_path}."
            )
        ]
    except Exception as e:
        logger.error(f"Error creating markdown file: {e}")
        raise e

async def run():
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

def main():
    # Run the async event loop
    anyio.run(run)

if __name__ == "__main__":
    main()

```

**Changes:**

*  **`dotenv` dependency**: Includes python-dotenv to load from a `.env` file
*   **Logging:** Includes basic logging using Python's `logging` module, sending logs to `shared_logs/module1.log`.
*   **Error Handling:** Basic error handling is implemented, including invalid arguments.
*   **Template:** The user input is now inserted into this template:
     `The user's goal is {content}. Subsequent work on this project will focus on achieving the user's goal.`
*   **Single file write:** The output is now a single file called `output.md`.

### **Step 4: Configure `.vscode/launch.json`**
If your `.vscode` folder or `launch.json` file do not exist, create the folder and then add this to the new file located at `mcp-hello/.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Module 1",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/module1/src/create_markdown_server/__main__.py",
            "console": "integratedTerminal"
        }
    ]
}
```
This configures VS Code to run your `server.py` script from the debugger with the integrated terminal.

**Step 5: Configure Claude Desktop**

1. Create or update your `claude_desktop_config.json` file located at:
   *   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   *   **Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

2. Add an entry for the new server under `mcpServers`, using the absolute path to your folder:

```json
{
    "mcpServers": {
        "markdown-creator": {
        "command": "uv",
        "args": ["--directory", "/path/to/your/mcp-hello/module1/src/create_markdown_server/", "run", "mcp-simple-prompt"],
        "env": {}
        }
     }
}
```
Be sure to change the `"/path/to/your/mcp-hello/module1/src/create_markdown_server/"` to the actual path on your machine.

3. Save the configuration file.

**Step 6: Test the Prototype**

1.  **Run the Server:**
    *   Open a new terminal in your `mcp-hello/` directory.
    *   Make sure you're in the virtual environment: `source .venv/bin/activate`
    *   Run `uv run module1/src/create_markdown_server`

2.  **Test with MCP Inspector:**
    *   Open another terminal in your `mcp-hello/` directory.
    *   Run the MCP Inspector: `npx @modelcontextprotocol/inspector uv --directory module1/src/create_markdown_server run create_markdown_server`.
    *   Click the "Connect" button.
    *   Navigate to the "Tools" Tab.
    *   You will see `create_markdown`.
    *   Enter a string for the `content` , such as `"This is a test!"`.
    *   Click "Call Tool".
    *   You should see the response and logs, as well as a file called `output.md` at the root of `mcp-hello`.

3.  **Test with Claude Desktop:**
    *   Restart Claude Desktop (quit and relaunch).
    *   Open a new conversation with Claude and select the "MarkdownCreator" server using the 🔌 icon.
    *   Type: `/tools` which should display available tools.
    *   Select `create_markdown`
    *   Enter text and Claude should respond with a message indicating success.
    *   Verify the `output.md` file has been created in your project's root directory.

**Code**
For reference, here is a listing of the code that you'll end up with in `src/markdown_creator/server.py` after completing the above steps:
```python
import os
import logging
from pathlib import Path

import anyio
import mcp.types as types
from mcp.server import Server
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(dotenv_path="../../../.env")

# Set up logging
LOG_DIR = "../../shared_logs/"  # Log to the shared logs directory
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "module1.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("MarkdownCreator")

# Define input model
class MarkdownInput(BaseModel):
    content: str = Field(..., description="The content of the markdown file.")

@server.call_tool()
async def create_markdown(arguments: dict) -> list[types.TextContent]:
    """Creates a markdown file with the provided content."""
    try:
        # Parse arguments using the input model
        input_data = MarkdownInput(**arguments)

        # Read content template
        template = "The user' goal is {content}. Subsequent work on this project will focus on achieving the user's goal."

        markdown_content = template.format(content=input_data.content)
        # Write content to the markdown file
        filepath = os.path.join("../../", "output.md")
        with open(filepath, "w") as file:
            file.write(markdown_content)

        logger.info(f"Markdown file created: {filepath}")
        return [
            types.TextContent(
                type="text", text=f"Created markdown file: {filepath}."
            )
        ]
    except Exception as e:
        logger.error(f"Error creating markdown file: {e}")
        raise e

async def run():
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

def main():
    # Run the async event loop
    anyio.run(run)

if __name__ == "__main__":
    main()
```
This should create a single server that handles input, and writes a file to disk. Please confirm that all the steps above are working before moving forward with implementing further modules or making code changes.
