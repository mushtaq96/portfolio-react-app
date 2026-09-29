"""
Manual retrieval check for the bilingual claim in DESIGN_DECISIONS.md (ADR-002).

Question: does a German query retrieve German documents, and an English query
English ones, with an English-trained embedding model? This prints the top hits
for each query so you can judge relevance yourself, plus one objective number:
how often the retrieved chunk's language tag matches the query language.

Run locally, where the index and the embedding model exist:

    cd backend && python check_retrieval.py

It reads the local .chroma_db (build it first with `python build.py`) and prints
short snippets of your documents to the terminal only.
"""
from document_processor import initialize_collection

# (language, question). Edit these to match what recruiters actually ask.
CASES = [
    ("en", "What is your work experience?"),
    ("en", "Which programming languages do you use?"),
    ("en", "Where did you study?"),
    ("en", "Do you have cloud experience?"),
    ("de", "Welche Berufserfahrung haben Sie?"),
    ("de", "Welche Programmiersprachen verwenden Sie?"),
    ("de", "Wo haben Sie studiert?"),
    ("de", "Haben Sie Erfahrung mit Cloud-Technologien?"),
]
TOP_K = 3


def snippet(text: str, width: int = 70) -> str:
    return " ".join(text.split())[:width]


def main() -> None:
    collection = initialize_collection()
    matches = {"en": [0, 0], "de": [0, 0]}  # language -> [hits in same language, total hits]

    for lang, question in CASES:
        result = collection.query(
            query_texts=[question],
            n_results=TOP_K,
            include=["documents", "metadatas", "distances"],
        )
        print(f"\n[{lang}] {question}")
        for doc, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            meta = meta or {}
            hit_lang = meta.get("language", "?")
            matches[lang][1] += 1
            matches[lang][0] += hit_lang == lang
            print(f"   {hit_lang:>2}  {meta.get('source_doc', '?'):<32} d={dist:.3f}  {snippet(doc)}")

    print("\nLanguage match (retrieved chunk language == query language):")
    for lang, (same, total) in matches.items():
        rate = f"{same}/{total} ({100 * same / total:.0f}%)" if total else "n/a"
        print(f"   {lang}: {rate}")
    print("\nThis only measures language, not relevance. Read the snippets above and "
          "decide whether the German answers are actually on topic before claiming "
          "German support.")


if __name__ == "__main__":
    main()
