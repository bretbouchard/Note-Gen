# Note-Gen MCP Server Documentation

This directory contains documentation for the Note-Gen MCP (Model-Controller-Presenter) Server for Musical Composition with AI Integration.

## Files

- **rfp.md**: Main RFP document outlining the project's goals, architecture, and development phases
- **app_flow_mcp.md**: High-level overview of the MCP architecture and application flow
- **app_flow_detail_mcp.md**: Detailed technical breakdown of the MCP architecture, including data types and component interactions

## Legacy Files

The following files are kept for historical reference but may not reflect the current MCP architecture:

- **app_flow.md**: Original app flow document based on the Schillinger System
- **app_flow_detail.md**: Original detailed app flow document

## Architecture

The Note-Gen application follows the Model-Controller-Presenter (MCP) architecture pattern:

1. **Models**: Data structures and business logic
2. **Controllers**: Business logic and application flow
3. **Presenters**: Data transformation for presentation
4. **Repositories**: Data access layer

## Key Features

- MongoDB database for storing musical components
- FastAPI for RESTful API endpoints
- Pydantic for data validation
- Asynchronous operations using Motor
- AI integration for musical composition

## Next Steps

1. Implement remaining controllers (ValidationController, UtilityController)
2. Enhance AI integration interfaces
3. Expand import/export capabilities
4. Implement advanced pattern generation algorithms
