"""MAPA metadata helpers."""

from __future__ import annotations

from datetime import date

from vaxintel.utils.metadata import SourceMetadata


def create_mapa_reference() -> SourceMetadata:
    """Create a metadata row for MAPA reference documentation."""
    return SourceMetadata(
        variable="sanitary_context_reference",
        description="Referencia institucional para contexto sanitario animal",
        source_name="MAPA / gov.br",
        source_url="https://www.gov.br/agricultura/pt-br/assuntos/saude-animal-e-bem-estar-animal",
        reference_year="vigente",
        extraction_date=date.today().isoformat(),
        file_path="docs/business_context.md",
        notes="Fonte de contexto, nao insumo quantitativo do score no MVP base.",
    )

