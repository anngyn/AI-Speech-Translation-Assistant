"""OnPoint terms that should be preserved during interpretation."""

GLOSSARY_TERMS: tuple[str, ...] = (
    "OnPoint",
    "Opollo",
    "CREA",
    "GMV",
    "SKU",
    "KPI",
    "Marketplace",
    "TikTok Shop",
    "Shopee",
    "Lazada",
)


def glossary_prompt_fragment() -> str:
    return ", ".join(GLOSSARY_TERMS)
