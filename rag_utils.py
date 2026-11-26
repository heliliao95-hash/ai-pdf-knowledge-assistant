
import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_pdf_pages(pdf_bytes, filename="PDF"):
    pages = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page": page_number,
                    "filename": filename,
                    "text": text
                })

    return pages


def split_into_chunks(pages, chunk_size=500, overlap=80):
    chunks = []

    for item in pages:
        text = item["text"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "page": item["page"],
                    "filename": item.get("filename", "PDF"),
                    "text": chunk_text
                })

            start += chunk_size - overlap

    return chunks


def search_chunks(chunks, question, top_k=4):
    if not chunks or not question.strip():
        return []

    documents = [chunk["text"] for chunk in chunks]

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
        max_features=30000,
        sublinear_tf=True
    )

    try:
        matrix = vectorizer.fit_transform(documents + [question])
    except ValueError:
        return []

    scores = cosine_similarity(
        matrix[-1],
        matrix[:-1]
    ).flatten()

    ranked_indices = scores.argsort()[::-1][:top_k]

    return [
        {
            **chunks[index],
            "score": float(scores[index])
        }
        for index in ranked_indices
        if scores[index] > 0
    ]
