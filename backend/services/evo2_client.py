import httpx
import numpy as np
import asyncio
from config import get_settings

# Antibiotics we predict — matches BV-BRC training labels
ANTIBIOTICS = [
    {"name": "Ampicillin",      "class": "Penicillins"},
    {"name": "Ciprofloxacin",   "class": "Fluoroquinolones"},
    {"name": "Gentamicin",      "class": "Aminoglycosides"},
    {"name": "Tetracycline",    "class": "Tetracyclines"},
    {"name": "Trimethoprim",    "class": "Folate inhibitors"},
    {"name": "Chloramphenicol", "class": "Amphenicols"},
    {"name": "Meropenem",       "class": "Carbapenems"},
    {"name": "Colistin",        "class": "Polymyxins"},
]

MAX_TOKENS_PER_CALL = 8000
CHUNK_OVERLAP = 200


async def get_evo2_embedding(sequence: str) -> np.ndarray:
    """
    Call NVIDIA Evo 2 API and return aggregated embedding vector.

    Strategy:
    - If sequence <= MAX_TOKENS_PER_CALL: single call
    - If longer: sliding window chunks, mean-pool embeddings
    """
    settings = get_settings()
    chunks = _chunk_sequence(sequence)
    embeddings = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, chunk in enumerate(chunks):
            embedding = await _call_nvidia_api(client, chunk, attempt=0)
            embeddings.append(embedding)

            if i < len(chunks) - 1:
                await asyncio.sleep(6.5)

    if len(embeddings) == 1:
        return embeddings[0]
    else:
        return np.mean(embeddings, axis=0)


def _chunk_sequence(sequence: str) -> list[str]:
    """Split sequence into overlapping chunks."""
    if len(sequence) <= MAX_TOKENS_PER_CALL:
        return [sequence]

    chunks = []
    start = 0
    while start < len(sequence):
        end = min(start + MAX_TOKENS_PER_CALL, len(sequence))
        chunks.append(sequence[start:end])
        start += MAX_TOKENS_PER_CALL - CHUNK_OVERLAP

    return chunks


async def _call_nvidia_api(
    client: httpx.AsyncClient,
    sequence: str,
    attempt: int = 0
) -> np.ndarray:
    """
    Single NVIDIA API call with retry logic.
    Returns a numpy array (the embedding proxy via logits).
    """
    settings = get_settings()

    headers = {
        "Authorization": f"Bearer {settings.nvidia_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "sequence": sequence,
        "num_tokens": 1,
        "top_k": 1,
        "enable_sampled_probs": True,
    }

    try:
        response = await client.post(
            settings.nvidia_api_url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return _extract_embedding_from_response(data, sequence)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429 and attempt < 3:
            wait = (2 ** attempt) * 10
            await asyncio.sleep(wait)
            return await _call_nvidia_api(client, sequence, attempt + 1)
        elif e.response.status_code == 401:
            raise ValueError(
                "Invalid NVIDIA API key. "
                "Get a free key at https://build.nvidia.com/arc/evo2-40b"
            )
        else:
            raise RuntimeError(f"NVIDIA API error: {e.response.status_code} — {e.response.text}")

    except httpx.TimeoutException:
        if attempt < 2:
            await asyncio.sleep(15)
            return await _call_nvidia_api(client, sequence, attempt + 1)
        raise RuntimeError("NVIDIA API timed out. Try a shorter sequence.")


def _extract_embedding_from_response(data: dict, sequence: str) -> np.ndarray:
    """
    Extract a meaningful feature vector from the API response.

    The NVIDIA NIM endpoint returns sampled probabilities.
    We use these as a proxy embedding: the distribution over the
    vocabulary at each position encodes Evo 2's representation.
    """
    if "sampled_probs" in data:
        probs = data["sampled_probs"]
        if isinstance(probs, list) and len(probs) > 0:
            arr = np.array(probs, dtype=np.float32)
            return _featurise_probs(arr, sequence)

    raise RuntimeError(
        "Evo 2 API did not return sampled_probs. "
        "Check the API endpoint and payload format."
    )


def _featurise_probs(probs: np.ndarray, sequence: str) -> np.ndarray:
    """
    Convert probability array to fixed-size feature vector.
    Returns a vector of exactly 27 features so the classifier
    always sees a consistent shape.

    Strategy: replace the first 6 sequence-derived features with
    API-derived statistics to inject model signal.
    """
    seq_features = _sequence_features(sequence)

    api_stats = np.array([
        float(np.mean(probs)),
        float(np.std(probs)),
        float(np.min(probs)),
        float(np.max(probs)),
        float(np.percentile(probs, 25)),
        float(np.percentile(probs, 75)),
    ], dtype=np.float32)

    seq_features[:6] = api_stats
    return seq_features


def _sequence_features(sequence: str) -> np.ndarray:
    """
    27-dimensional sequence-derived feature vector.
    Captures: nucleotide frequencies, dinucleotide ratios, resistance motif signals.
    """
    features = []
    seq = sequence.upper()
    n = len(seq)

    # Nucleotide frequencies (4 features)
    features.append(seq.count("G") / n)
    features.append(seq.count("C") / n)
    features.append(seq.count("A") / n)
    features.append(seq.count("T") / n)

    # Dinucleotide frequencies (16 features)
    dinucs = ["AA","AT","AG","AC","TA","TT","TG","TC",
               "GA","GT","GG","GC","CA","CT","CG","CC"]
    for di in dinucs:
        count = sum(1 for i in range(n-1) if seq[i:i+2] == di)
        features.append(count / max(n-1, 1))

    # Resistance gene k-mer signals (7 features)
    resistance_motifs = [
        "ATGAGTATTCAACATTTCCGTGTCG",  # TEM-1 beta-lactamase start
        "ATGCGTTATTTCGAG",             # SHV start
        "ATGGATTTCGTGTTT",             # CTX-M start
        "ATGGAGAAAAAAATCACTGG",        # NDM-1 start
        "ATGCAGATCGGCGGC",             # OXA-type start
        "GCAGGCGGCGGCGGCG",            # Integron integrase motif
        "ATTGCTTGAAGCTGGA",            # Efflux pump signal
    ]

    for motif in resistance_motifs:
        hits = sum(1 for i in range(n - 10) if seq[i:i+10] == motif[:10])
        features.append(min(hits / max(n / 1000, 1), 1.0))

    return np.array(features, dtype=np.float32)
