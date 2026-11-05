DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size"
        )

    if not text.strip():
        return []

    chunks = []
    step = chunk_size - chunk_overlap

    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size]
        chunks.append(chunk)

        if start + chunk_size >= len(text):
            break

    return chunks
