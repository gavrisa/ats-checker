# Figma MCP Setup for Cursor

## ✅ What I've Done

1. **Installed mcp-figma package** locally in your project
2. **Created MCP configuration files** in two locations:
   - `~/.config/cursor/mcp_config.json`
   - `/Users/jekaterinagavrisa/Library/Application Support/Cursor/User/mcp_config.json`

## 🔧 Next Steps

### 1. Get Your Figma API Key

1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Navigate to the "Personal Access Tokens" section
3. Click "Create a new personal access token"
4. Enter a name (e.g., "Cursor MCP Integration")
5. Click "Create token"
6. Copy the token (starts with `figd_`)

### 2. Configure Cursor

The MCP configuration is already set up. You may need to:

1. **Restart Cursor** to load the new MCP configuration
2. **Check Cursor settings** to ensure MCP is enabled

### 3. Test the Integration

Once Cursor is restarted, you can test the Figma MCP integration by asking Cursor to:

```
Please use mcp-figma to set my Figma API key: figd_your_token_here
```

### 4. Available Figma MCP Commands

Once configured, you can use these commands with Cursor:

#### File Operations
- `get_file`: Get a Figma file by key
- `get_file_nodes`: Get specific nodes from a file
- `get_image`: Get images for nodes
- `get_image_fills`: Get URLs for images used in a file

#### Comments
- `get_comments`: Get comments on a file
- `post_comment`: Post a comment on a file
- `delete_comment`: Delete a comment

#### Teams & Projects
- `get_team_projects`: Get projects for a team
- `get_project_files`: Get files for a project

#### Components & Styles
- `get_team_components`: Get components for a team
- `get_file_components`: Get components from a file
- `get_component`: Get a component by key
- `get_team_styles`: Get styles for a team
- `get_file_styles`: Get styles from a file
- `get_style`: Get a style by key

## 📝 Example Usage

Once set up, you can ask Cursor things like:

```
Please use mcp-figma to get the file with key abc123def456
```

```
Please use mcp-figma to get all components from file abc123def456
```

```
Please use mcp-figma to post a comment on file abc123def456 saying "This design looks great!"
```

## 🔍 Troubleshooting

1. **MCP not working**: Restart Cursor after creating the config file
2. **API key issues**: Make sure your Figma token is valid and has the right permissions
3. **File access**: Ensure you have access to the Figma files you're trying to access
4. **Rate limits**: The Figma API has rate limits, so don't make too many requests quickly

## 📁 Configuration Files Created

- `~/.config/cursor/mcp_config.json`
- `/Users/jekaterinagavrisa/Library/Application Support/Cursor/User/mcp_config.json`

Both files contain the same configuration for the Figma MCP server.




