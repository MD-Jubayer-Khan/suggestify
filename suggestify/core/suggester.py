# suggestify/core/suggester.py
from sentence_transformers import SentenceTransformer, util
from suggestify.core.database import load_queries
from suggestify.core.fuzzy import fuzzy_match
import wikipediaapi
import spacy

# Load spaCy English model once
nlp = spacy.load("en_core_web_sm")

class QuerySuggester:
    def __init__(self, data_source=None, table=None, model_name='all-MiniLM-L6-v2', use_wiki=None, wiki_lang='en', user_agent="suggestify-bot"):
        """
        Initialize the Query Suggestion Engine.
        - data_source: list, CSV path, or DB connection string
        - use_wiki: None = auto (True if no dataset)
        """
        self.model = SentenceTransformer(model_name)
        self.data_source = data_source
        self.table = table

        # Load dataset queries
        self.queries = load_queries(data_source, table)
        self.embeddings = None
        if self.queries:
            self.embeddings = self.model.encode(self.queries, convert_to_tensor=True)

        # Wiki mode
        if use_wiki is None:
            self.use_wiki = not bool(self.queries)
        else:
            self.use_wiki = use_wiki

        if self.use_wiki:
            self.wiki = wikipediaapi.Wikipedia(language=wiki_lang, user_agent=user_agent)

    def _wiki_sentences(self, query, max_sentences=5):
        """Fetch first few sentences from Wikipedia page for the query"""
        page = self.wiki.page(query)
        if not page.exists():
            return []
        text = page.text
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        return sentences[:max_sentences]

    def _generate_dynamic_queries(self, query, sentences):
        """Generate query-style suggestions from sentences dynamically"""
        suggestions = []

        for sentence in sentences:
            doc = nlp(sentence)
            for chunk in doc.noun_chunks:
                noun = chunk.text.strip()
                if not noun:
                    continue

                # Focus on the main query term
                if query.lower() not in noun.lower() and query.lower() not in sentence.lower():
                    continue

                # Common patterns
                if any(tok.dep_ in ["attr", "ROOT"] for tok in doc):
                    suggestions.append(f"What is {noun}?")

                verbs = [tok.lemma_ for tok in doc if tok.pos_ == "VERB"]
                if any(v in ["produce", "grow", "use", "make", "process", "manufacture"] for v in verbs):
                    suggestions.append(f"How is {noun} used?")
                    suggestions.append(f"Where is {noun} produced?")

                if any(tok.ent_type_ == "DATE" for tok in doc):
                    suggestions.append(f"History of {noun}")

                # Fallback
                suggestions.append(f"Learn about {noun}")

        # Deduplicate while preserving order
        return list(dict.fromkeys(suggestions))

    def suggest(self, query, top_k=5, use_fuzzy=True):
        """
        Generate top_k suggestions for a query:
        - Semantic search over dataset (if exists)
        - Wikipedia dynamic suggestions (if wiki mode enabled)
        - Optional fuzzy expansion
        """
        suggestions = []

        # Semantic search
        if self.queries and self.embeddings is not None:
            query_emb = self.model.encode(query, convert_to_tensor=True)
            hits = util.semantic_search(query_emb, self.embeddings, top_k=top_k)[0]
            suggestions.extend([self.queries[h['corpus_id']] for h in hits])

        # Fuzzy expansion
        if use_fuzzy and self.queries:
            fz = fuzzy_match(query, self.queries)
            suggestions.extend([s for s in fz if s not in suggestions])

        # Wikipedia dynamic queries
        if self.use_wiki:
            sentences = self._wiki_sentences(query)
            wiki_suggestions = self._generate_dynamic_queries(query, sentences)
            suggestions.extend(wiki_suggestions)

        # Limit top_k
        return suggestions[:top_k]
