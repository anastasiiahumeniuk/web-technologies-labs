from functools import lru_cache
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "lang-uk/ukr-paraphrase-multilingual-mpnet-base"


@lru_cache(maxsize=1)
def get_model():
    """
    Lazy-loaded embedding model.
    Will NOT be loaded during import.
    """
    return SentenceTransformer(_MODEL_NAME)


def generate_embedding(text: str) -> str:
    """
    Generate embedding for input text
    and return it as pgvector-compatible string.
    """
    model = get_model()
    vector = model.encode(text)
    return ",".join(map(str, vector))
