from Bio import SeqIO
from Bio.Seq import Seq
import io

def parse_fasta(raw_text: str) -> tuple[str, str]:
    """
    Parse FASTA or raw sequence input.
    Returns (sequence_name, clean_sequence).
    """
    raw_text = raw_text.strip()

    if raw_text.startswith(">"):
        # FASTA format
        handle = io.StringIO(raw_text)
        try:
            record = next(SeqIO.parse(handle, "fasta"))
            return record.id, str(record.seq).upper()
        except StopIteration:
            raise ValueError("Could not parse FASTA format. Check your input.")
    else:
        # Raw sequence
        clean = raw_text.upper().replace(" ", "").replace("\n", "").replace("\r", "")
        return "User sequence", clean

def gc_content(sequence: str) -> float:
    """Calculate GC content as percentage."""
    gc = sequence.count("G") + sequence.count("C")
    return round((gc / len(sequence)) * 100, 1) if sequence else 0.0

def estimate_genome_type(sequence: str) -> str:
    """Rough estimate of organism type based on length and GC."""
    length = len(sequence)
    gc = gc_content(sequence)

    if length < 10_000:
        return "plasmid or gene fragment"
    elif length < 1_000_000:
        if gc > 60:
            return "likely Pseudomonas or Streptomyces"
        elif gc < 35:
            return "likely Staphylococcus or Streptococcus"
        else:
            return "likely Enterobacteriaceae (E. coli, Klebsiella, etc.)"
    else:
        return "full bacterial chromosome"
