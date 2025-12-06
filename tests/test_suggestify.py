from suggestify import QuerySuggester

def test_without_db():
    s = QuerySuggester()
    assert len(s.suggest("heart attack")) > 0

def test_with_fake_queries():
    s = QuerySuggester()
    s.queries = ["blood pressure check", "heart failure risk"]
    s.embeddings = s.model.encode(s.queries, convert_to_tensor=True)

    res = s.suggest("heart", top_k=1)
    assert "heart" in res[0].lower()
