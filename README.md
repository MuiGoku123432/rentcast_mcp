# RentCast MCP Server

A Model Context Protocol (MCP) server that provides complete access to the [RentCast Real Estate API](https://developers.rentcast.io/reference/introduction) for AI assistants like Claude Desktop.

## Demo
<video src="https://github.com/vtrivedy/rentcast_mcp/blob/main/assets/rentcast_mcp.mp4">
  Your browser does not support the video tag.
</video>


## 🏠 What This Enables

This MCP server gives AI assistants access to **140+ million property records** and real estate data, enabling powerful use cases like:

- **Property Research**: Search and analyze properties by address, city, or ZIP code
- **Market Analysis**: Get market statistics and trends for any ZIP code
- **Property Valuation**: Get AI-powered rent and value estimates (AVM) 
- **Listing Discovery**: Find active sale and rental listings with detailed filtering
- **Investment Analysis**: Compare properties, analyze cash flow, and evaluate markets
- **Real Estate Automation**: Build AI workflows for property management, lead generation, and market research

## 🚀 Features

### Complete RentCast API Coverage (11 Tools)

**🏠 Property Data (3 tools)**
- `search_property` - Search properties by address, city, state, or ZIP
- `get_property_by_id` - Get detailed property information by RentCast ID
- `get_random_properties` - Get sample properties for testing and exploration

**💰 Property Valuation (2 tools)**
- `get_value_estimate` - Get AI-powered property value estimates (AVM)
- `get_rent_estimate` - Get AI-powered rent estimates for any address

**📋 Property Listings (4 tools)**
- `search_sale_listings` - Find active properties for sale
- `search_rental_listings` - Find active rental listings
- `get_sale_listing_by_id` - Get detailed sale listing information
- `get_rental_listing_by_id` - Get detailed rental listing information

**📈 Market Data (1 tool)**
- `get_market_stats` - Get comprehensive market statistics for any ZIP code

**⚙️ Utilities (1 tool)**
- `ping_rate_limit` - Check your API usage and remaining quota

## 📋 Prerequisites

1. **RentCast API Key**
   - Sign up at [RentCast](https://developers.rentcast.io/) 
   - Generate your API key from the dashboard
   - Free tier includes 50 requests/month

2. **Claude Desktop App**
   - Download from [Claude Desktop](https://claude.ai/download)
   - Works on macOS, Windows, and Linux

3. **Python 3.10+**

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rentcast-mcp
cd rentcast-mcp
```
> Replace `yourusername` with the actual GitHub username where this repository is hosted.

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```bash
echo "RENTCAST_API_KEY=your_actual_api_key_here" > .env
```
Replace `your_actual_api_key_here` with your actual RentCast API key.

### 4. Test the Server
```bash
python rentcast_mcp_server.py
```
If everything is working, you should see the server start without errors. Press `Ctrl+C` to stop.

## 🔧 Claude Desktop Configuration

### 1. Locate Claude Desktop Config
The configuration file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Update Configuration
Add the RentCast MCP server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "rentcast-local": {
      "command": "/path/to/your/project/.venv/bin/python",
             "args": ["/path/to/your/project/rentcast_mcp_server.py"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

**Important**: Replace `/path/to/your/project` with the actual path to where you cloned this repository.

#### Example Paths:
- **macOS/Linux**: `/Users/yourusername/rentcast-mcp`
- **Windows**: `C:\Users\yourusername\rentcast-mcp`

### 3. Restart Claude Desktop
Close and reopen Claude Desktop for the changes to take effect.

## 🎯 Usage Examples

Once configured, you can use natural language to access real estate data through Claude:

### Property Search & Analysis
```
"Search for properties in Austin, TX and analyze the market trends"
```

### Property Valuation
```
"Get both rent and value estimates for 123 Main St, San Francisco, CA"
```

### Market Research
```
"Find rental listings in Denver, CO under $2000/month and analyze the market statistics for that area"
```

### Investment Analysis
```
"Search for properties in zip code 78701 and get market statistics to help me understand the investment potential"
```

### Property Comparison
```
"Find 3 similar properties to 456 Oak Avenue, Seattle, WA and compare their estimated values"
```

## 🔑 API Key Management

The server automatically uses your API key from the `.env` file, so Claude won't need to ask for it with each request. This provides a seamless experience while keeping your credentials secure.

If you prefer to provide the API key manually for specific requests, all tools also accept an optional `api_key` parameter.

## 📊 Rate Limits

- **Free Tier**: 50 requests/month
- **Paid Tiers**: Higher limits available
- Use the `ping_rate_limit` tool to check your current usage
- Visit [RentCast Pricing](https://developers.rentcast.io/) for upgrade options

## 🔍 Troubleshooting

### Server Not Starting
1. Ensure your virtual environment is activated
2. Check that all dependencies are installed: `pip install -r requirements.txt`
3. Verify your `.env` file contains a valid API key

### Claude Desktop Not Connecting
1. Verify the paths in your `claude_desktop_config.json` are correct
2. Ensure Claude Desktop has been restarted after configuration changes
3. Check that the MCP server shows up in Claude Desktop settings

### API Errors
1. Verify your RentCast API key is valid
2. Check your API quota with the `ping_rate_limit` tool
3. Some areas may have limited data availability

## 🚧 Future Enhancements

- **Cloud Deployment**: Deploy to Modal, AWS, or other cloud platforms
- **Caching Layer**: Add Redis caching for frequently requested data
- **Batch Processing**: Support for bulk property analysis
- **Custom Filters**: Advanced filtering and sorting options
- **Data Enrichment**: Integration with additional real estate data sources

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [RentCast API Documentation](https://developers.rentcast.io/reference/introduction)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)

## ⭐ Support

If this project helps you, please consider giving it a star on GitHub and sharing it with others in the real estate and AI communities!

---

**Built with ❤️ using the Model Context Protocol and RentCast API**
```bash
python -m pip install --upgrade modal-cli
modal login                         # paste your token
