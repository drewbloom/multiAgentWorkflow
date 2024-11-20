### Multi-Agent Workflow Demo

Welcome to an in-progress demo for a multi-agent setup.

## Current Status
- Streamlit app has authentication and can handle both text and speech modalities
- AI assistant has tools to understand and query the attached database to help the user

# Next steps:
- Save conversation memory and cache database knowledge for each user
- Integrate with SharePoint data environment to expand assistant capabilities
- Create a vector store of the database as an additional tool for quick retrieval
    - This will be necessary for larger dbs, or dbs containing large documents

## Overall Goals
- Offer a user both text and speech modalities to accomplish tasks utilizing their own data
- Use common Python dependencies to connect together multiple AI agents that work together to determine how best to serve the user
- Include tool use that allows those agents to engage in semantic search and make SQL queries
- Integrate with sample data sources so this model can be replicated easily with other databases using SQL

## Replicating This Setup
- Must use a SQLite database or db file
- app folder contains deployments
- agents folder contains the agent setups
- database folder contains the database and scripting for interacting with it
* This may be all be migrated into utils.py once an appropriate setup is determined