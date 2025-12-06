# suggestify/core/suggester.py
from sentence_transformers import SentenceTransformer, util
from suggestify.core.database import load_queries
from suggestify.core.fuzzy import fuzzy_match
from suggestify.core.wiki import wiki_expand
from typing import List

class QuerySuggester:
    def __init__(self, data_source=None, table=None, model_name='all-MiniLM-L6-v2', use_wiki=None):
        """
        Suggestify Intelligent Query Suggestion Engine

        Smart Mode:
         ✔ If dataset exists → semantic & fuzzy search (Wiki OFF)
         ✔ If no dataset → Wikipedia-powered expansion (Wiki ON)
        
        Override behavior manually:
         use_wiki=True  → force Wikipedia
         use_wiki=False → disable Wikipedia completely
        """
        self.model = SentenceTransformer(model_name)
        self.data_source = data_source
        self.table = table

        # Load dataset (if exists)
        self.queries = load_queries(data_source, table)

        if self.queries:
            self.embeddings = self.model.encode(self.queries, convert_to_tensor=True)
        else:
            self.embeddings = None
        
        # Dynamic Wiki Logic
        if use_wiki is None:             # auto mode
            self.use_wiki = (not bool(self.queries))
        else:
            self.use_wiki = use_wiki      # force ON/OFF manually

    def suggest(self, query: str, top_k: int = 5, use_fuzzy: bool = True) -> List[str]:
        query = (query or "").strip()
        if not query:
            return []

        suggestions = []

        # If dataset exists → semantic search first
        if self.queries and self.embeddings is not None:
            query_emb = self.model.encode(query, convert_to_tensor=True)
            hits = util.semantic_search(query_emb, self.embeddings, top_k=top_k)[0]
            suggestions = [self.queries[h['corpus_id']] for h in hits]

        # If no dataset & Wiki allowed → intelligent expansion
        elif self.use_wiki:
            wiki_suggestions = wiki_expand(query, top_k=top_k)
            if wiki_suggestions:
                suggestions = wiki_suggestions

        # Last fallback (no dataset, Wiki disabled, or Wiki empty)
        if not suggestions:
            suggestions = [
                f"{query} information",
                f"{query} details",
                f"{query} related data",
                f"search about {query}",
                f"what is {query}"
            ][:top_k]

        # Optional fuzzy expansion (only meaningful if dataset exists)
        if use_fuzzy and self.queries:
            fz = fuzzy_match(query, self.queries)
            for s in fz:
                if s not in suggestions:
                    suggestions.append(s)

        return suggestions[:top_k]
