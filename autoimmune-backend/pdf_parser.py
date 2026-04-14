import fitz  # pymupdf
import re

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF file"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()

def extract_lab_values(text: str) -> dict:
    """Extract lab values from PDF text using pattern matching"""
    
    def find_value(patterns, default=0.0):
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        return default

    def find_flag(keywords):
        for keyword in keywords:
            if keyword in text:
                return 1.0
        return 0.0

    return {
        # Continuous values
        "Age": find_value([
            r"age[:\s]+(\d+)",
            r"(\d+)\s*years?\s*old",
            r"dob.*?(\d+)\s*years"
        ], default=45.0),

        "Gender": 1.0 if any(w in text for w in ["female", "woman", "girl", "f /"]) else 0.0,

        "ESR": find_value([
            r"esr[:\s]+(\d+\.?\d*)",
            r"erythrocyte sedimentation[:\s]+(\d+\.?\d*)",
            r"sed rate[:\s]+(\d+\.?\d*)"
        ], default=15.0),

        "CRP": find_value([
            r"crp[:\s]+(\d+\.?\d*)",
            r"c.reactive protein[:\s]+(\d+\.?\d*)",
            r"c-reactive protein[:\s]+(\d+\.?\d*)"
        ], default=5.0),

        "C3": find_value([
            r"c3[:\s]+(\d+\.?\d*)",
            r"complement c3[:\s]+(\d+\.?\d*)"
        ], default=1.2),

        "C4": find_value([
            r"c4[:\s]+(\d+\.?\d*)",
            r"complement c4[:\s]+(\d+\.?\d*)"
        ], default=0.3),

        # Binary flags (positive/negative)
        "RF": find_flag(["rf positive", "rheumatoid factor positive",
                          "rf: positive", "rf : positive", "rf+", "rf reactive"]),

        "Anti_CCP": find_flag(["anti-ccp positive", "anti ccp positive",
                                "ccp positive", "anti-ccp: positive"]),

        "HLA_B27": find_flag(["hla-b27 positive", "hla b27 positive",
                               "b27 positive", "hla-b27: positive"]),

        "ANA": find_flag(["ana positive", "antinuclear positive",
                           "ana: positive", "ana titer", "ana reactive"]),

        "Anti_Ro": find_flag(["anti-ro positive", "anti ro positive",
                               "ssa positive", "anti-ro: positive"]),

        "Anti_La": find_flag(["anti-la positive", "anti la positive",
                               "ssb positive", "anti-la: positive"]),

        "Anti_dsDNA": find_flag(["anti-dsdna positive", "dsdna positive",
                                  "anti-dsdna: positive", "ds-dna positive"]),

        "Anti_Sm": find_flag(["anti-sm positive", "anti sm positive",
                               "anti-sm: positive"]),

        "ASCA": find_flag(["asca positive", "anti-saccharomyces positive"]),

        "Anti_CBir1": find_flag(["anti-cbir1 positive", "cbir1 positive"]),

        "Anti_OmpC": find_flag(["anti-ompc positive", "ompc positive"]),

        "pANCA": find_flag(["panca positive", "p-anca positive",
                             "panca: positive", "perinuclear anca positive"]),

        "EMA": find_flag(["ema positive", "endomysial positive",
                           "ema: positive"]),

        "DGP": find_flag(["dgp positive", "deamidated gliadin positive"]),

        "Anti_tTG": find_flag(["anti-ttg positive", "ttg positive",
                                "tissue transglutaminase positive"]),

        "Anti_TPO": find_flag(["anti-tpo positive", "tpo positive",
                                "thyroid peroxidase positive"]),

        "Anti_SMA": find_flag(["anti-sma positive", "sma positive",
                                "smooth muscle antibody positive"]),
    }