# PII/PHI Scanner MCP Integration Guide (2025)

## Overview

The PII/PHI Scanner now includes a Model Context Protocol (MCP) server that enables seamless integration with AI assistants like Claude and ChatGPT. This allows you to access the scanner's powerful PII/PHI detection capabilities directly from your favorite AI assistant.

## What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI applications to securely connect to external data sources and tools. With MCP, your AI assistant can directly analyze database schemas for sensitive data without you having to copy and paste information back and forth.

## Features Available via MCP

### 🔧 Tools

1. **analyze_ddl_file**
   - Analyze DDL/SQL files for PII/PHI content
   - Supports GDPR and HIPAA compliance checking
   - Multiple output formats (detailed, summary, JSON)

2. **analyze_schema_data**
   - Analyze structured schema data (CSV/JSON format)
   - Batch processing for multiple tables
   - Comprehensive compliance reporting

3. **get_regulation_info**
   - Retrieve detailed GDPR and HIPAA guides
   - Compliance requirements and penalties
   - Best practices and recommendations

4. **validate_scanner_setup**
   - Verify scanner configuration
   - Test Azure OpenAI connectivity
   - Validate dependencies and setup

### 📚 Resources

1. **GDPR Regulation Guide** (`pii-scanner://regulations/gdpr`)
   - Complete GDPR compliance reference
   - Personal data categories and requirements
   - Penalties and enforcement information

2. **HIPAA Regulation Guide** (`pii-scanner://regulations/hipaa`)
   - Protected Health Information (PHI) definitions
   - Safe Harbor de-identification method
   - Compliance safeguards and requirements

3. **Sample DDL File** (`pii-scanner://examples/sample-ddl`)
   - Example database schema with PII/PHI fields
   - Educational reference for testing
   - Common healthcare and business data patterns

## Setup Instructions

### Prerequisites

1. **Python Environment**
   ```bash
   # Ensure Python 3.8+ is installed
   python --version
   
   # Install the PII/PHI Scanner dependencies
   cd pii_scanner_poc
   pip install -r requirements.txt
   ```

2. **Azure OpenAI Configuration**
   ```bash
   # Configure your .env file with Azure OpenAI credentials
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
   AZURE_OPENAI_API_VERSION=2023-08-01-preview
   AZURE_OPENAI_DEPLOYMENT=gpt-4
   ```

3. **Validate Setup**
   ```bash
   # Test the scanner setup
   python test_setup.py
   ```

### MCP Server Configuration

#### Method 1: Direct Python Execution

```bash
# Start the MCP server
cd pii_scanner_poc
python mcp_server.py
```

#### Method 2: Using MCP CLI (Recommended)

```bash
# Install MCP CLI if not already installed
pip install "mcp[cli]"

# Start the server using MCP CLI
cd pii_scanner_poc
mcp run python mcp_server.py
```

#### Method 3: Background Service

```bash
# Run as background service (Linux/macOS)
cd pii_scanner_poc
nohup python mcp_server.py > mcp_server.log 2>&1 &

# Windows (using PowerShell)
Start-Process python -ArgumentList "mcp_server.py" -WindowStyle Hidden
```

## AI Assistant Integration

### Claude Desktop Integration

1. **Install Claude Desktop**
   - Download from: https://claude.ai/desktop
   - Or use Claude web interface

2. **Configure MCP Connection**

   Create or edit your Claude Desktop configuration file:

   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   **Linux:** `~/.config/Claude/claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "pii-phi-scanner": {
         "command": "python",
         "args": ["/path/to/pii_scanner_poc/mcp_server.py"],
         "env": {
           "AZURE_OPENAI_API_KEY": "your_api_key_here",
           "AZURE_OPENAI_ENDPOINT": "https://your-endpoint.openai.azure.com",
           "AZURE_OPENAI_API_VERSION": "2023-08-01-preview",
           "AZURE_OPENAI_DEPLOYMENT": "gpt-4"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**
   - Close and reopen Claude Desktop
   - The PII/PHI Scanner tools should now be available

### ChatGPT Integration

1. **Using OpenAI's Function Calling (GPT-4)**

   The MCP server can be integrated with ChatGPT through custom function implementations. Contact OpenAI support for enterprise MCP integration options.

2. **Alternative: API Bridge**

   For immediate use, you can create a simple HTTP bridge:

   ```python
   # Create a simple HTTP wrapper (example)
   from flask import Flask, request, jsonify
   import subprocess
   import json

   app = Flask(__name__)

   @app.route('/analyze_ddl', methods=['POST'])
   def analyze_ddl():
       data = request.json
       # Call MCP server functions here
       return jsonify(result)

   if __name__ == '__main__':
       app.run(port=5000)
   ```

### Other AI Assistants

The MCP protocol is designed to be universal. Other AI assistants that support MCP can connect using similar configuration patterns.

## Usage Examples

### Basic DDL Analysis

```
Prompt to your AI Assistant:
"Please analyze this DDL file for PII/PHI content according to HIPAA regulations:

CREATE TABLE patients (
    patient_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    ssn VARCHAR(11),
    email VARCHAR(100),
    phone VARCHAR(20)
);
"
```

The AI assistant will automatically use the `analyze_ddl_file` tool to process your request.

### Schema Data Analysis

```
Prompt:
"Analyze this CSV schema data for GDPR compliance:

schema_name,table_name,column_name,data_type
public,users,user_id,INTEGER
public,users,email_address,VARCHAR(255)
public,users,full_name,VARCHAR(100)
public,users,birth_date,DATE
"
```

### Regulation Information

```
Prompt:
"What are the key requirements for HIPAA compliance?"
```

The AI will use the `get_regulation_info` tool to provide comprehensive HIPAA guidance.

## Troubleshooting

### Common Issues

1. **"MCP server not responding"**
   ```bash
   # Check if the server is running
   ps aux | grep mcp_server.py
   
   # Check server logs
   tail -f mcp_server.log
   
   # Restart the server
   python mcp_server.py
   ```

2. **"Azure OpenAI API error"**
   ```bash
   # Validate your API credentials
   python -c "
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print('API Key:', os.getenv('AZURE_OPENAI_API_KEY')[:10] + '...')
   print('Endpoint:', os.getenv('AZURE_OPENAI_ENDPOINT'))
   "
   
   # Test the scanner directly
   python test_setup.py
   ```

3. **"Tools not appearing in AI assistant"**
   - Verify MCP configuration file syntax
   - Check file paths in configuration
   - Restart the AI assistant application
   - Review AI assistant logs for connection errors

4. **"Permission denied errors"**
   ```bash
   # Ensure proper file permissions
   chmod +x mcp_server.py
   
   # Check Python path
   which python
   
   # Verify virtual environment activation
   echo $VIRTUAL_ENV
   ```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
# Add to mcp_server.py temporarily
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

1. **Large Schema Files**
   - The scanner automatically uses batch processing
   - For very large schemas (1000+ tables), consider splitting analysis

2. **API Rate Limits**
   - The scanner includes retry logic and rate limiting
   - Monitor Azure OpenAI quota usage

3. **Memory Usage**
   - Large DDL files are processed in streaming mode
   - Temporary files are automatically cleaned up

## Security Considerations

### Data Privacy

1. **Local Processing**
   - All DDL parsing is done locally
   - Only field metadata is sent to Azure OpenAI
   - No actual data content is transmitted

2. **API Key Security**
   - Store API keys in environment variables
   - Never commit credentials to version control
   - Use Azure Key Vault for production deployments

3. **Network Security**
   - MCP communication is local (stdio)
   - Azure OpenAI uses HTTPS encryption
   - Consider VPN for enterprise deployments

### Access Control

1. **File System Permissions**
   ```bash
   # Restrict access to configuration files
   chmod 600 .env
   chmod 600 db_config.ini
   ```

2. **API Access**
   - Use dedicated Azure OpenAI resource
   - Implement usage monitoring
   - Set appropriate quota limits

## Advanced Configuration

### Custom Regulations

You can extend the scanner to support additional privacy regulations:

```python
# Add to your configuration
CUSTOM_REGULATIONS = {
    "CCPA": {
        "personal_identifiers": ["..."],
        "sensitive_categories": ["..."]
    }
}
```

### Enterprise Deployment

For enterprise environments:

1. **Container Deployment**
   ```dockerfile
   FROM python:3.11-slim
   COPY pii_scanner_poc /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   CMD ["python", "mcp_server.py"]
   ```

2. **Service Mesh Integration**
   - Use Kubernetes for orchestration
   - Implement service discovery
   - Add monitoring and alerting

3. **High Availability**
   - Deploy multiple MCP server instances
   - Use load balancing
   - Implement health checks

## Support and Resources

### Documentation

- **Main README**: `/pii_scanner_poc/README.md`
- **Project Overview**: `/pii_scanner_poc/PROJECT_OVERVIEW.md`
- **Code Documentation**: Inline comments throughout codebase

### Getting Help

1. **Configuration Issues**
   - Review setup scripts: `setup_project.bat` / `setup_project.sh`
   - Run validation: `python test_setup.py`

2. **Analysis Questions**
   - Check regulation guides via MCP resources
   - Review sample DDL file for examples

3. **Integration Problems**
   - Verify MCP server logs
   - Test tools individually
   - Check AI assistant documentation

### Updates and Maintenance

1. **Dependency Updates**
   ```bash
   # Check for updates
   pip list --outdated
   
   # Update packages
   pip install -r requirements.txt --upgrade
   ```

2. **MCP Protocol Updates**
   - Monitor MCP specification changes
   - Update FastMCP library as needed
   - Test compatibility with AI assistants

## Conclusion

The PII/PHI Scanner MCP integration provides a powerful, seamless way to access advanced privacy compliance analysis directly from your AI assistant. This integration maintains the security and accuracy of the standalone scanner while adding the convenience of conversational interaction.

For additional features or support, refer to the main project documentation or create an issue in the project repository.

---

**Version**: 2.0 - FastMCP Integration (2025)  
**Last Updated**: June 2025  
**Compatibility**: MCP 2025 Specification, Claude Desktop, ChatGPT Enterprise