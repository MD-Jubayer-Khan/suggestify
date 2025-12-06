from suggestify.core.suggester import QuerySuggester


suggester = QuerySuggester(data_source=None)

print("Type a query (or 'exit' to quit):")
while True:
    query = input("> ")
    if query.lower() == "exit":
        break

    suggestions = suggester.suggest(query, top_k=5)
    print("Suggestions:", suggestions)