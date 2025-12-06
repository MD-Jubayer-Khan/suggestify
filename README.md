# 🚀 Suggestify — AI Query Suggestion Engine

Suggestify intelligently generates search query recommendations using NLP.
Works **with or without a database** — fully plug & play.

---

## 🔥 Features

| Feature | Supported |
|---|---|
| Semantic AI suggestions | ✔ |
| Works without DB | ✔ |
| Fuzzy matching | ✔ |
| Django + FastAPI + Flask adapters | ✔ |
| SQL / CSV history intake | ✔ |

---

### Basic Use

```python
from suggestify import QuerySuggester

s = QuerySuggester()
print(s.suggest("chest pain"))
