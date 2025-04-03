# Note-Gen MCP Server Documentation

This directory contains documentation for the Note-Gen MCP (Model-Controller-Presenter) Server for Musical Composition with AI Integration.

## Files

- **rfp.md**: Main RFP document outlining the project's goals, architecture, and development phases
- **app_flow_mcp.md**: High-level overview of the MCP architecture and application flow
- **app_flow_detail_mcp.md**: Detailed technical breakdown of the MCP architecture, including data types and component interactions

## Musical Algorithm Documentation

The following files contain detailed specifications for the musical algorithms that will be implemented within the MCP architecture:

- **app_flow.md**: Overview of the Schillinger System musical algorithms
- **app_flow_detail.md**: General detailed flow of musical algorithms
- **app_flow_detail_rhythm.md**: Detailed implementation of rhythm generation algorithms
- **app_flow_detail_harmony.md**: Detailed implementation of harmony generation algorithms
- **app_flow_detail_melody.md**: Detailed implementation of melody generation algorithms
- **app_flow_detail_geometry.md**: Detailed implementation of geometric transformations
- **app_flow_detail_integrate.md**: Detailed implementation of harmony-melody integration
- **app_flow_detail_output.md**: Detailed implementation of output generation

These files contain essential musical theory and algorithms that will be integrated into the MCP architecture. The algorithms described in these files will be implemented within the appropriate controllers and models of the MCP server.

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
