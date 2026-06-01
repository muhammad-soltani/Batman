from typing import List
from hazm import sent_tokenize

def chunk_sentences(text: str) -> List[str]:
    sentences = [s.strip() for s in sent_tokenize(text)]
    return [s for s in sentences if s]