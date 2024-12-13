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