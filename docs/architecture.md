# Architecture

The system follows a layered command-and-control design:

1. **Ingest / monitor** disaster events and zones
2. **Assess** geospatial impact on the map
3. **Predict** resource demand with trained regressors
4. **Adjust** demand using vulnerability weighting
5. **Allocate** limited supplies with OR-Tools
6. **Route** depot-to-zone logistics
7. **Assign** field missions
8. **Analyze** post-event performance

Frontend talks only to FastAPI. Models are loaded once at API startup and reused for every prediction request.
