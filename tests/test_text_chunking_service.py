import pytest

from app.services.text_chunking_service import split_text_into_chunks


def test_empty_text_returns_empty_list():
    result = split_text_into_chunks("")

    assert result == []


def test_short_text_returns_single_chunk():
    text = "This is a short document."

    result = split_text_into_chunks(text, chunk_size=100, chunk_overlap=20)

    assert result == [text]


def test_long_text_respects_chunk_size_and_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"

    result = split_text_into_chunks(
        text,
        chunk_size=10,
        chunk_overlap=3,
    )

    assert result == [
        "abcdefghij",
        "hijklmnopq",
        "opqrstuvwx",
        "vwxyz",
    ]


@pytest.mark.parametrize("chunk_size", [0, -1])
def test_invalid_chunk_size_raises_error(chunk_size):
    with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
        split_text_into_chunks("Some text", chunk_size=chunk_size)


@pytest.mark.parametrize("chunk_overlap", [-1, 10, 15])
def test_invalid_chunk_overlap_raises_error(chunk_overlap):
    with pytest.raises(
        ValueError,
        match="chunk_overlap must be non-negative and smaller than chunk_size",
    ):
        split_text_into_chunks(
            "Some text",
            chunk_size=10,
            chunk_overlap=chunk_overlap,
        )


def test_zero_overlap_produces_non_overlapping_chunks():
    result = split_text_into_chunks(
        "abcdefghij",
        chunk_size=4,
        chunk_overlap=0,
    )

    assert result == ["abcd", "efgh", "ij"]


def test_text_exactly_chunk_size_returns_single_chunk():
    text = "abcdefghij"

    result = split_text_into_chunks(
        text,
        chunk_size=10,
        chunk_overlap=3,
    )

    assert result == [text]


def test_text_one_character_over_chunk_size():
    text = "abcdefghijk"

    result = split_text_into_chunks(
        text,
        chunk_size=10,
        chunk_overlap=3,
    )

    assert result == ["abcdefghij", "hijk"]


@pytest.mark.parametrize("text", [" ", "   ", "\n\n", "\n\n "])
def test_whitespace_only_text_returns_empty_list(text):
    result = split_text_into_chunks(text)

    assert result == []


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [
        (5, 0),
        (5, 2),
        (10, 3),
        (20, 5),
        (30, 10),
    ],
)
def test_chunking_preserves_text_and_overlap(chunk_size, chunk_overlap):
    text = "abcdefghijklmnopqrstuvwxyz" * 4

    chunks = split_text_into_chunks(
        text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    assert all(0 < len(chunk) <= chunk_size for chunk in chunks)

    reconstructed_text = chunks[0]

    for previous, current in zip(chunks, chunks[1:], strict=False):
        if chunk_overlap:
            assert previous[-chunk_overlap:] == current[:chunk_overlap]

        reconstructed_text += current[chunk_overlap:]

    assert reconstructed_text == text


def test_default_chunking_parameters():
    text = "a" * 1200

    chunks = split_text_into_chunks(text)

    assert len(chunks) == 2
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 400
    assert chunks[0][-200:] == chunks[1][:200]
