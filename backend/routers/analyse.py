from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import time
import asyncio
from typing import Optional

from models.schemas import AnalyseRequest, AnalyseResponse, ErrorResponse
from services.evo2_client import get_evo2_embedding
from services.classifier import predict_resistance, compute_overall_risk
from services.sequence_validator import parse_fasta, estimate_genome_type
from services.sae_client import get_sae_features

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post(
    "/analyse",
    response_model=AnalyseResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def analyse_sequence(request: AnalyseRequest):
    """
    Main analysis endpoint.
    Accepts a DNA sequence, returns a resistance profile.
    """
    start_time = time.time()

    try:
        # 1. Parse and clean sequence
        name, clean_seq = parse_fasta(request.sequence)
        display_name = request.sequence_name or name

        # 2. Get Evo 2 embedding via NVIDIA API
        embedding = await get_evo2_embedding(clean_seq)

        # 3. Run classifier
        predictions = predict_resistance(embedding)

        # 4. Compute SAE interpretability features
        sae_features = get_sae_features(embedding, clean_seq)

        # 5. Compute overall risk
        risk_level, risk_explanation = compute_overall_risk(predictions)

        # 6. Build genomic summary
        genome_type = estimate_genome_type(clean_seq)
        gc = round((clean_seq.count("G") + clean_seq.count("C")) / len(clean_seq) * 100, 1)
        genomic_summary = (
            f"Analysed {len(clean_seq):,} base pairs of DNA. "
            f"GC content: {gc}% (consistent with {genome_type}). "
            f"Evo 2 processed the full sequence using its 1-million base-pair context window, "
            f"reading the plasmid architecture, resistance gene scaffolds, and chromosomal context simultaneously."
        )

        elapsed = round(time.time() - start_time, 2)

        return AnalyseResponse(
            sequence_name=display_name,
            sequence_length=len(clean_seq),
            overall_risk=risk_level,
            risk_explanation=risk_explanation,
            antibiotics=predictions,
            sae_features=sae_features,
            genomic_summary=genomic_summary,
            processing_time_seconds=elapsed,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid sequence",
                "detail": str(e),
                "suggestion": "Ensure your input is valid DNA (A, T, G, C only) or a standard FASTA file."
            }
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "detail": str(e),
                "suggestion": "Check your NVIDIA API key or try a shorter sequence."
            }
        )


@router.post("/analyse/file")
async def analyse_file(
    file: UploadFile = File(...),
    sequence_name: Optional[str] = Form(None)
):
    """Accept a FASTA file upload and run analysis."""
    if not file.filename.endswith((".fasta", ".fa", ".fna", ".txt")):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid file type",
                "detail": "Please upload a .fasta, .fa, .fna, or .txt file.",
                "suggestion": "Export your sequence in FASTA format from your sequencing software."
            }
        )

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File encoding error",
                "detail": "Could not read file. Ensure it is a plain text FASTA file.",
                "suggestion": "Open in a text editor and save as UTF-8."
            }
        )

    request = AnalyseRequest(
        sequence=text,
        sequence_name=sequence_name or file.filename
    )
    return await analyse_sequence(request)
