# mcp-mcp test.

This is a primative multi-agent modular initialization capability test prototype of Model Context Protocol.  

The purpose of this initial hello-mcp test is to create an mpc project that uses Claude Desktop as the client and it will create a markdown file that inserts content from an user's input into an existing markdown template including other content.



# Roadmap:

## Example of multiple servers operating in a workflow

My further test project, after te initial hello-mcp test is working, will have multiple servers and clients.  They will operate in a modular way, the first will create a markdown file based on adding user input text to a content template and saving the file to root directory.  The second will ingest that file and add more info to it then save the updated version to the root.  The third will likewise ingest the output of the second and add still more content and export the third version of the file to the root.  Treat each of these three like back boxes in the sense that they will not share code or components but we will pretend they are running on different technologies to preserve the modular approach and we will for convenience be able to do things like share a virtual environment and requirements for this first test.  We work in VS Code on my mac.  See potential examples for ways to accomplish this in the Roadmap files from Gemini 1.5 and GPT-4o  [include all documentation for MCP]