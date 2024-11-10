### Create a vector store search test for semantic search using a free embeddings model
# 1. Pick a free embeddings technology from a leaderboard: https://huggingface.co/spaces/mteb/leaderboard
# 2. Set up its functionality here and declare it as a class
# 3. Embed each SQL query description field to create a new db table ("search_db") to start a query from
# 4. Perform a sentence / newline character splitting methodology on the full-text field from the database to get tokenization at sentence level 
# 5. For an appropriate number of matches (n=?), then allow the model to query with SQL and search the full-text field for matching columns
# 6. Migrate the finished class to Utils so it can be accessed by the other scripting - but this should run PRIOR to prod to create 
### A companion database would be created that is vector-stored for semantic search, while the original database would be kept so the agent can also query from it
# 
# This test is being created with help from this video: https://www.youtube.com/watch?v=JEBDfGqrAUA

