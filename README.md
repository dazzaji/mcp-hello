# Incemental Model Context Protocol

This is a primative multi-agent modular initialization capability test prototype of Model Context Protocol.  

The purpose of this initial hello-mcp test is to create an mpc project that uses Claude Desktop as the client and it will create a markdown file that inserts content from an user's input into an existing markdown template including other content.

Template:

The user' goal is [inert the user input text here].  Subsquent work on this project will focus on achieving the user's goal.


# Roadmap:

## Example of multiple servers operating in a workflow

My further test project, after te initial hello-mcp test is working, will have multiple servers and clients.  They will operate in a modular way, the first will create a markdown file based on adding user input text to a content template and saving the file to root directory.  The second will ingest that file and add more info to it then save the updated version to the root.  The third will likewise ingest the output of the second and add still more content and export the third version of the file to the root.  Treat each of these three like back boxes in the sense that they will not share code or components but we will pretend they are running on different technologies to preserve the modular approach and we will for convenience be able to do things like share a virtual environment and requirements for this first test.  We work in VS Code on my mac.  See potential examples for ways to accomplish this in the Roadmap files from Gemini 1.5 and GPT-4o  [include all documentation for MCP]

---------

# POTENTIAL APPROACH

Okay, I've adjusted the previous response to fit the `mcp-hello` directory, and have populated each module's `server.py` with the code requested.  Let's continue to test `module1` using MCP inspector and a manual client

**Updated Project Structure:**

```
mcp-hello/
├── module1/                # First module: Creates a markdown file
│   ├── src/
│   │   └── create_markdown_server/
│   │       └── server.py   # Implementation of Module 1
│   ├── pyproject.toml
├── module2/                # Second module: Updates markdown file
│   ├── src/
│   │   ├── update_markdown_server/
│   │       └── server.py   # Implementation of Module 2
│   ├── pyproject.toml
├── module3/                # Third module: Finalizes markdown file
│   ├── src/
│   │   ├── finalize_markdown_server/
│   │       └── server.py   # Implementation of Module 3
│   ├── pyproject.toml
├── shared_logs/            # Shared logging directory for visibility
├── README.md               # Documentation
└── .vscode/                # VS Code configurations
    ├── launch.json         # Debugging configurations
    └── settings.json       # Project-specific settings
```
### Testing Steps

1.  **Run the Server:**
    *   Open a new terminal in your `mcp-hello/` directory.
    *   Make sure you're in the virtual environment: `source .venv/bin/activate`
    *   Run `uv run module1/src/create_markdown_server`

        You will see log entries from `module1` in `shared_logs/module1.log`.

2.  **Test with MCP Inspector:**
    *   Open another terminal in your `mcp-hello/` directory.
    *   Run the MCP Inspector with the following command from the `mcp-hello` directory:
        ```bash
        npx @modelcontextprotocol/inspector uv --directory module1/src/create_markdown_server run create_markdown_server
        ```
        You should see a URL printed in your terminal. Copy that and go to it in your browser.
    *   Click the "Connect" button.
    *   Navigate to the "Tools" Tab.
    *   You will see `create_markdown`.
    *   Enter values for the `content` and `template` fields, such as `"This is a test!"` and `"#Test\n\n{content}"` then click "Call Tool".
    *   You should see a response in the "Response" section and you should see `"Created markdown file"` log in your first terminal window, as well as a log entry in the `shared_logs/module1.log` file.
    *   You should also see the file created at the path `mcp-hello/output.md`.
    *   Inspect the log for any errors or warnings.

3.  **Test with a Manual Client:**
    *   Create a `test_client.py` file in the `mcp-hello` directory and add the following:

```python
import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os

load_dotenv()  # load environment variables from .env
# Set up a minimal logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("client")

class MyMCPClient:
    """A basic MCP Client that connects via stdio."""

    def __init__(self, server_command: str, server_args: list[str] | None = None):
        self.server_command = server_command
        self.server_args = server_args if server_args is not None else []

    @asynccontextmanager
    async def connect(self):
        """Connect to the server and get a ClientSession."""
        server_parameters = StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
        )
        async with stdio_client(server_parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session

async def main():
    # Load environment variables
    load_dotenv()
    
    # Read server configuration from environment variables, or fall back to example
    server_command = os.environ.get("MCP_SERVER_COMMAND")
    server_args_str = os.environ.get("MCP_SERVER_ARGS")
    server_args = server_args_str.split(" ") if server_args_str else None


    if server_command is None:
        print(
            "MCP_SERVER_COMMAND is not defined - defaulting to a Python server for this example."
        )
        server_command = "uv"
        server_args = ["run", "module1/src/create_markdown_server/"]
    else:
         print(f"Connecting to server: {server_command} {server_args or ''}")

    client = MyMCPClient(server_command, server_args)

    async with client.connect() as session:
        logger.info("Connected to server")
        # Example: Call the create_markdown tool
        try:
             response = await session.call_tool(
                 "create_markdown",
                 {
                     "content": "This is a manual test using a client!",
                      "template": "# Manual Test\n\n{content}"
                 }
             )
             logger.info(f"Call tool response:\n{response}")
        except Exception as e:
            logger.error(f"Error during communication: {e}")
 
if __name__ == "__main__":
    asyncio.run(main())
```
  - Make an `.env` file in your root directory with the following:
    ```
    MCP_SERVER_COMMAND=uv
    MCP_SERVER_ARGS=run module1/src/create_markdown_server/
    ```
  - Run `python test_client.py`
    - Verify that a `output.md` file was created in your root directory
    - Verify that a new log is written to `shared_logs/module1.log`

Let me know once you've tested Module 1, and we can proceed with Module 2!
