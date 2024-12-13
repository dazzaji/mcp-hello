# generic three server MCP
---


Okay, let's get started! Here's a step-by-step guide to set up the environment, create the servers, implement the logic, and test them using `mcp-inspector` with detailed logging.

**Step 1: Environment Setup**

1. **Create Project Directory:**
    ```bash
    mkdir mcp_test_project
    cd mcp_test_project
    ```

2. **Create Virtual Environment:**
    ```bash
    uv venv
    ```
    This creates a virtual environment in a hidden directory named `.venv`

3. **Activate Virtual Environment:**
    *   **macOS:**
        ```bash
        source .venv/bin/activate
        ```
   You'll see `(.venv)` prepended to your terminal prompt, indicating the virtual environment is active.

4. **Install `create-mcp-server`:**
    ```bash
    uv pip install create-mcp-server mcp
    ```
   This installs the `create-mcp-server` package along with the `mcp` library into your virtual environment.

**Step 2: Create Server Projects**

We'll generate the basic structure for each server using `create-mcp-server`. Run these commands from the `mcp_test_project` directory:

1. **Server 1 (Markdown Creator):**

    ```bash
    uvx create-mcp-server server_1
    ```

    When prompted, provide the following:
    *   Project Name: `markdown-creator`
    *   Project Description: `Creates markdown files from user input`
    *   Server Version: (Leave default: `0.1.0`)
    *   Enable Claude.app integration?: `y`

2. **Server 2 (Markdown Modifier):**

    ```bash
    uvx create-mcp-server server_2
    ```

    When prompted, provide the following:
    *   Project Name: `markdown-modifier`
    *   Project Description: `Modifies existing markdown files`
    *   Server Version: (Leave default: `0.1.0`)
    *   Enable Claude.app integration?: `y`

3. **Server 3 (Markdown Modifier):**

    ```bash
    uvx create-mcp-server server_3
    ```

    When prompted, provide the following:
    *   Project Name: `markdown-modifier2`
    *   Project Description: `Modifies existing markdown files`
    *   Server Version: (Leave default: `0.1.0`)
    *   Enable Claude.app integration?: `y`

Now your project structure should look like this:

```
mcp_test_project/
├── server_1/
│   ├── pyproject.toml
│   └── src/
│       └── markdown_creator/
│           ├── __init__.py
│           ├── __main__.py
│           └── server.py
├── server_2/
│   ├── pyproject.toml
│   └── src/
│       └── markdown_modifier/
│           ├── __init__.py
│           ├── __main__.py
│           └── server.py
└── server_3/
    ├── pyproject.toml
    └── src/
        └── markdown_modifier2/
            ├── __init__.py
            ├── __main__.py
            └── server.py
```

**Step 3: Implement Server Logic**

We will replace the contents of `server.py` in each of the server directories with the following code:

**server_1/src/markdown_creator/server.py:**

```python
import logging
import os
from pathlib import Path

import anyio
import mcp.types as types
from mcp.server import Server
from pydantic import BaseModel, Field

# Server setup
server = Server("markdown-creator")
logger = logging.getLogger(__name__)

# Ensure the output directory exists
OUTPUT_DIR = Path("./")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class CreateMarkdownArgs(BaseModel):
    content: str = Field(..., description="The main content of the markdown file.")
    template: str = Field(..., description="A content template for the markdown file.")

@server.tool()
async def create_markdown(arguments: CreateMarkdownArgs) -> list[types.TextContent]:
    """
    Creates a markdown file based on a template and adds content to it.
    """
    logger.info(f"Creating markdown file with content: {arguments.content}")

    # Generate the content using the template
    markdown_content = f"{arguments.template}\n\n{arguments.content}"

    # Determine the next file number
    existing_files = [f for f in OUTPUT_DIR.glob("output_*.md") if f.is_file()]
    next_number = len(existing_files) + 1
    file_path = OUTPUT_DIR / f"output_{next_number}.md"

    # Write to the file
    try:
        file_path.write_text(markdown_content, encoding="utf-8")
        return [
            types.TextContent(
                type="text", text=f"Created file: {file_path.name}"
            )
        ]
    except Exception as e:
        logger.error(f"Error creating file: {e}")
        return [
            types.TextContent(type="text", text=f"Error creating file: {e}")
        ]

async def run():
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the async event loop
    anyio.run(run)

if __name__ == "__main__":
    main()
```

**server_2/src/markdown_modifier/server.py:**

```python
import logging
import os
from pathlib import Path

import anyio
import mcp.types as types
from mcp.server import Server
from pydantic import BaseModel, Field

# Server setup
server = Server("markdown-modifier")
logger = logging.getLogger(__name__)

# Ensure the output directory exists
OUTPUT_DIR = Path("./")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class ModifyMarkdownArgs(BaseModel):
    file_path: str = Field(..., description="Path to the markdown file to modify.")
    additional_info: str = Field(..., description="Additional information to add to the file.")

@server.tool()
async def modify_markdown(arguments: ModifyMarkdownArgs) -> list[types.TextContent]:
    """
    Modifies an existing markdown file by appending additional information.
    """
    logger.info(f"Modifying markdown file: {arguments.file_path}")

    file_path = OUTPUT_DIR / arguments.file_path

    # Check if the file exists
    if not file_path.exists():
        return [
            types.TextContent(type="text", text=f"Error: File not found: {arguments.file_path}")
        ]

    try:
        # Read existing content
        existing_content = file_path.read_text(encoding="utf-8")

        # Append additional information
        updated_content = f"{existing_content}\n\n{arguments.additional_info}"

        # Determine the next file number for the modified file
        existing_files = [f for f in OUTPUT_DIR.glob("output_*.md") if f.is_file()]
        next_number = len(existing_files) + 1
        new_file_path = OUTPUT_DIR / f"output_{next_number}.md"

        # Write updated content to a new file
        new_file_path.write_text(updated_content, encoding="utf-8")

        return [
            types.TextContent(
                type="text", text=f"Modified file saved as: {new_file_path.name}"
            )
        ]
    except Exception as e:
        logger.error(f"Error modifying file: {e}")
        return [
            types.TextContent(type="text", text=f"Error modifying file: {e}")
        ]

async def run():
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the async event loop
    anyio.run(run)

if __name__ == "__main__":
    main()
```

**server_3/src/markdown_modifier2/server.py:**

```python
import logging
import os
from pathlib import Path

import anyio
import mcp.types as types
from mcp.server import Server
from pydantic import BaseModel, Field

# Server setup
server = Server("markdown-modifier2")
logger = logging.getLogger(__name__)

# Ensure the output directory exists
OUTPUT_DIR = Path("./")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class ModifyMarkdown2Args(BaseModel):
    file_path: str = Field(..., description="Path to the markdown file to modify.")
    additional_info: str = Field(..., description="Additional information to add to the file.")

@server.tool()
async def modify_markdown_2(arguments: ModifyMarkdown2Args) -> list[types.TextContent]:
    """
    Modifies an existing markdown file by appending even more additional information.
    """
    logger.info(f"Modifying markdown file: {arguments.file_path}")

    file_path = OUTPUT_DIR / arguments.file_path

    # Check if the file exists
    if not file_path.exists():
        return [
            types.TextContent(type="text", text=f"Error: File not found: {arguments.file_path}")
        ]

    try:
        # Read existing content
        existing_content = file_path.read_text(encoding="utf-8")

        # Append additional information
        updated_content = f"{existing_content}\n\n{arguments.additional_info}"

        # Determine the next file number for the modified file
        existing_files = [f for f in OUTPUT_DIR.glob("output_*.md") if f.is_file()]
        next_number = len(existing_files) + 1
        new_file_path = OUTPUT_DIR / f"output_{next_number}.md"

        # Write updated content to a new file
        new_file_path.write_text(updated_content, encoding="utf-8")

        return [
            types.TextContent(
                type="text", text=f"Modified file saved as: {new_file_path.name}"
            )
        ]
    except Exception as e:
        logger.error(f"Error modifying file: {e}")
        return [
            types.TextContent(type="text", text=f"Error modifying file: {e}")
        ]

async def run():
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the async event loop
    anyio.run(run)

if __name__ == "__main__":
    main()
```

**Explanation of Changes:**

*   **File I/O:** The `create_markdown` function now saves the generated markdown content to a file in the root directory. The `modify_markdown` function reads and updates an existing file.
*   **Error Handling:** Basic error handling is included to catch file I/O issues.
*   **Logging:** The `logger` is used to provide info and error messages.

**Step 4: Test with MCP Inspector**

1. **Launch MCP Inspector:**
    ```bash
    npx @modelcontextprotocol/inspector
    ```
    This will open the MCP Inspector in your browser (usually at `http://localhost:5173`).

2. **Connect to the Servers:**
    *   In the Inspector, you will see three fields: `Command`, `Arguments`, and `Environment Variables`.

    *   **For `server_1`:**
        *   **Command:** `uv`
        *   **Arguments:**  `run mcp-simple-prompt`
        *   **Environment Variables:** Leave empty

    *   **For `server_2`:**
        *   **Command:** `uv`
        *   **Arguments:**  `run mcp-simple-resource`
        *   **Environment Variables:** Leave empty
    *   **For `server_3`:**
        *   **Command:** `uv`
        *   **Arguments:**  `run mcp-simple-tool`
        *   **Environment Variables:** Leave empty

    *   For each server's entry, click "Connect". The status should change to "connected". You will need to hit the `Format` button in the `Commands` box to get each server to connect.

3. **Interact with the Servers:**
    *   Go to the "Tools" tab. You should see the tool `create-markdown` listed for `server_1` and `modify-markdown` listed for `server_2`, and `modify_markdown_2` listed for `server_3`.
    *   Select the `create-markdown` tool.
    *   Enter values for the `content` and `template` fields.
    *   Click "Call Tool".
    *   You should see a response in the "Response" area indicating that the file was created.
    *   Select the `modify-markdown` tool.
    *   Enter a value for the `file_path` argument (e.g. `output_1.md`).
    *   Enter a value for the `additional_info` argument.
    *   Click "Call Tool".
    *   You should see a response in the "Response" area indicating that the file was modified.
    *   Repeat the prior two steps but with the `modify_markdown_2` tool and the `output_2.md` file.
    *   Open the `output_3.md` file in the root directory to verify the contents.

**Step 5: Test with Claude Desktop**

1. **Configure Claude Desktop:**
    *   Go to your Claude Desktop configuration file (`claude_desktop_config.json`).
    *   Add entries for each server under `mcpServers` :

    ```json
    "mcpServers": {
        "markdown-creator": {
          "command": "uv",
          "args": ["--directory", "server_1", "run", "mcp-simple-prompt"],
          "env": {}
        },
        "markdown-modifier": {
          "command": "uv",
          "args": ["--directory", "server_2", "run", "mcp-simple-resource"],
          "env": {}
        },
        "markdown-modifier2": {
          "command": "uv",
          "args": ["--directory", "server_3", "run", "mcp-simple-tool"],
          "env": {}
        }
    }
    ```

    Make sure to replace `"server_1"`, `"server_2"`, and `"server_3"` with the correct paths to your server directories.

2. **Restart Claude Desktop:**
    *   Completely quit and restart the Claude Desktop application.

3. **Interact with the Servers:**
    *   In a new conversation, use the 🔌 icon to select a server and see its tools.
    *   Invoke the tools using their names and providing necessary arguments.

**Example Claude Conversation:**

> **User:** /tools

*Claude will show the available tools. You can select `create-markdown`.*

> **Claude:** (Provides inputs for `content` and `template`)
>
> **User:**
>
> ```json
> {
>   "content": "This is the initial content.",
>   "template": "# My Document\n\n{content}"
> }
> ```

*Claude should respond, indicating that `output_1.md` was created.*

> **User:** /tools

*Claude will show the available tools. You can select `modify-markdown`.*

> **Claude:** (Provides inputs for `file_path` and `additional_info`)
>
> **User:**
>
> ```json
> {
>   "file_path": "output_1.md",
>   "additional_info": "This is additional information appended to the file."
> }
> ```

*Claude should respond, indicating that `output_2.md` was created.*

> **User:** /tools

*Claude will show the available tools. You can select `modify_markdown_2`.*

> **Claude:** (Provides inputs for `file_path` and `additional_info`)
>
> **User:**
>
> ```json
> {
>   "file_path": "output_2.md",
>   "additional_info": "This is even more additional information appended to the file."
> }
> ```

*Claude should respond, indicating that `output_3.md` was created.*

You have now successfully set up and tested a modular MCP project with three servers! You can expand on this by adding more complex tools and interactions. Remember to consult the MCP documentation for details on the protocol's features and capabilities. Let me know if you want to make changes to the project or explore more advanced MCP features.
