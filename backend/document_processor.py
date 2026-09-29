from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# This model runs locally, so it does not use an OpenAI/Groq API.
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_text(file_path: str) -> str:
    """
    Extract plain text from a TXT or PDF file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        return "\n".join(pages)

    raise ValueError("Unsupported file type. Only PDF and TXT are supported.")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Split text into overlapping chunks.

    chunk_size:
        Approximate number of words per chunk.

    overlap:
        Number of words repeated between adjacent chunks.
    """

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def create_embeddings(chunks):
    """
    Convert text chunks into numerical vectors.
    """

    if not chunks:
        return []

    embeddings = _embedding_model.encode(
        chunks,
        normalize_embeddings=True
    )

    return embeddings.tolist()


def process_document(file_path: str):
    """
    Complete local document-processing pipeline:

    file
      ↓
    text extraction
      ↓
    chunking
      ↓
    embeddings
    """

    text = extract_text(file_path)

    chunks = chunk_text(text)

    embeddings = create_embeddings(chunks)

    return {
        "file_name": Path(file_path).name,
        "text": text,
        "chunks": chunks,
        "embeddings": embeddings,
    }