from suggestify.core.wiki import wiki_expand

def test_wiki_expand_basic():
    res = wiki_expand("diabetes", top_k=3)
    assert isinstance(res, list)
    assert len(res) <= 3
