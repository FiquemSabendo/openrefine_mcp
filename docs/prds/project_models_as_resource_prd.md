# Product Requirements Document: Convert Project Models to Resource

## Overview

This PRD outlines the conversion of the `get_project_models` functionality from a FastMCP tool to a resource, improving the user experience and aligning with MCP design patterns.

## Problem Statement

Currently, `get_project_models` is implemented as a tool that requires explicit function calls to retrieve project metadata. This approach has several limitations:

1. **Poor UX**: Users must explicitly call a tool to access basic project information
2. **Context Loading Issues**: Project structure information isn't automatically available to the LLM
3. **Design Pattern Mismatch**: Project models represent read-only metadata, not actions
4. **Inefficient Interactions**: Users need to make separate tool calls to understand project structure

## Proposed Solution

Convert `get_project_models` from a tool to a resource accessible via URI `openrefine://project/{project_id}/models`.

## Why Resource Instead of Tool

### Resource Characteristics (✅ Matches Project Models)
- **Read-Only Data Access**: Project models contain static metadata about columns, records, and scripting capabilities
- **Idempotent Retrieval**: Same project ID always returns the same structural information
- **No State Changes**: Getting models doesn't modify the project or trigger side effects
- **Informational Purpose**: Models provide context about data structure, not actions

### Tool Characteristics (❌ Doesn't Match Project Models)
- **Action-Oriented**: Tools perform actions, change state, or trigger side effects
- **Function Calls**: Require explicit invocation with parameters
- **State Changes**: Imply potential modifications to the system
- **Command Pattern**: "Do something" rather than "Get information"

### FastMCP Design Alignment

According to FastMCP documentation:
- **Resources**: "Read-only access to data" (like GET requests)
- **Tools**: "Perform actions, change state, trigger side effects" (like POST requests)

Project models clearly fit the resource pattern as they provide read-only structural information.

## Benefits

### 1. Improved User Experience
- **Natural Language Access**: Users can reference project structure naturally ("show me the columns in project 123")
- **Contextual Awareness**: LLM automatically has access to project structure when needed
- **Reduced Friction**: No need for explicit tool calls to understand basic project information

### 2. Better LLM Integration
- **Proactive Context Loading**: Project structure loaded into LLM context automatically
- **Intelligent References**: LLM can reference specific columns or features without explicit calls
- **Enhanced Reasoning**: LLM has structural information available for better decision-making

### 3. RESTful Design
- **URI-Based Access**: Clean, predictable resource URIs (`openrefine://project/123/models`)
- **Standard Patterns**: Follows established REST conventions
- **Discoverability**: Resources can be listed and browsed

### 4. Performance Optimization
- **Caching Opportunities**: Resource responses can be cached more effectively
- **Lazy Loading**: Resources loaded only when referenced
- **Reduced API Calls**: Fewer explicit function calls needed

## Implementation Plan

### Phase 1: Resource Implementation
```python
@app.resource("openrefine://project/{project_id}/models")
async def get_project_models_resource(project_id: int) -> str:
    """Get project models information from OpenRefine.

    Returns structural information about the project including:
    - Column definitions and metadata
    - Record model configuration
    - Available scripting languages
    - Overlay models

    This resource provides the foundation for understanding project structure
    and enables intelligent column references and operation planning.
    """
    client = get_client()
    result = await client.get_project_models(project_id)
    return result.model_dump_json()
```

### Phase 2: Tool Removal
- Remove the existing `get_project_models` tool
- Update documentation and examples
- Ensure backward compatibility during transition

### Phase 3: Enhanced Resource Features
- Add resource listing capability
- Implement resource caching
- Add resource validation and error handling

## Technical Specifications

### Resource URI Pattern
```
openrefine://project/{project_id}/models
```

### Response Format
```json
{
  "columnModel": {
    "columns": [
      {
        "cellIndex": 0,
        "originalName": "id",
        "name": "id"
      }
    ],
    "keyCellIndex": 0,
    "keyColumnName": "id",
    "columnGroups": []
  },
  "recordModel": {
    "hasRecords": false
  },
  "overlayModels": {},
  "scripting": {
    "grel": {
      "name": "GREL",
      "defaultExpression": "value"
    },
    "jython": {
      "name": "Jython",
      "defaultExpression": "return value"
    },
    "clojure": {
      "name": "Clojure",
      "defaultExpression": "value"
    }
  }
}
```

### Error Handling
- Invalid project ID: Return 404 with descriptive error
- Network errors: Return 503 with retry guidance
- Authentication errors: Return 401 with auth requirements

## Success Metrics

### User Experience
- **Reduced Tool Calls**: 50% reduction in explicit project structure queries
- **Faster Interactions**: 30% faster time to first meaningful operation
- **Natural Language Usage**: 80% of project structure references use natural language

### Technical Performance
- **Resource Hit Rate**: 90% of project operations reference the models resource
- **Cache Efficiency**: 70% of resource requests served from cache
- **Error Rate**: <1% resource access failures

### Adoption
- **Documentation Usage**: 100% of examples updated to use resource pattern
- **Developer Feedback**: Positive feedback on resource-based approach
- **Community Adoption**: Resource pattern adopted in related MCP servers

## Risks and Mitigation

### Risk: Breaking Changes
**Mitigation**: Maintain tool during transition period, deprecate gradually

### Risk: Performance Impact
**Mitigation**: Implement resource caching and lazy loading

### Risk: User Confusion
**Mitigation**: Clear documentation and migration guide

## Future Enhancements

### Resource Variants
- `openrefine://project/{project_id}/models/columns` - Column-specific info
- `openrefine://project/{project_id}/models/scripting` - Scripting capabilities only

### Resource Templates
- Dynamic resource generation based on project state
- Filtered resource views for specific use cases

### Resource Discovery
- Resource listing and browsing capabilities
- Resource metadata and documentation

## Conclusion

Converting `get_project_models` to a resource aligns with MCP design principles, improves user experience, and enables more natural LLM interactions. The resource pattern is the correct architectural choice for read-only metadata access, providing a foundation for enhanced OpenRefine MCP server capabilities.

This change represents a significant improvement in the server's design and user experience, setting the stage for future enhancements and better integration with LLM workflows.
