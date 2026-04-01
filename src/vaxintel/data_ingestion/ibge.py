"""IBGE SIDRA ingestion helpers."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import requests

from vaxintel.utils.metadata import SourceMetadata

SIDRA_BASE_URL = "https://apisidra.ibge.gov.br/values"
DEFAULT_TIMEOUT = 60
UF_NAME_TO_CODE = {
    "Rondônia": "RO",
    "Acre": "AC",
    "Amazonas": "AM",
    "Roraima": "RR",
    "Pará": "PA",
    "Amapá": "AP",
    "Tocantins": "TO",
    "Maranhão": "MA",
    "Piauí": "PI",
    "Ceará": "CE",
    "Rio Grande do Norte": "RN",
    "Paraíba": "PB",
    "Pernambuco": "PE",
    "Alagoas": "AL",
    "Sergipe": "SE",
    "Bahia": "BA",
    "Minas Gerais": "MG",
    "Espírito Santo": "ES",
    "Rio de Janeiro": "RJ",
    "São Paulo": "SP",
    "Paraná": "PR",
    "Santa Catarina": "SC",
    "Rio Grande do Sul": "RS",
    "Mato Grosso do Sul": "MS",
    "Mato Grosso": "MT",
    "Goiás": "GO",
    "Distrito Federal": "DF",
}


def _request_json(path: str) -> list[dict[str, Any]]:
    """Execute a SIDRA request and return the parsed JSON payload."""
    response = requests.get(f"{SIDRA_BASE_URL}/{path.lstrip('/')}", timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"Unexpected SIDRA response for path {path!r}: {payload!r}")
    return payload


def _payload_to_frame(payload: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert SIDRA's header-plus-rows JSON format into a DataFrame."""
    return pd.DataFrame(payload[1:])


def _coerce_numeric(series: pd.Series) -> pd.Series:
    """Convert SIDRA numeric strings into floats, coercing masked values to NA."""
    return pd.to_numeric(series.replace({"X": None, "...": None, "..": None, "-": 0}), errors="coerce")


def fetch_bovine_herd_uf(reference_year: int = 2024) -> pd.DataFrame:
    """Fetch bovine herd counts by UF from PPM table 3939."""
    payload = _request_json(f"t/3939/n3/all/v/105/p/{reference_year}/c79/2670/f/n")
    df = _payload_to_frame(payload)
    return pd.DataFrame(
        {
            "uf": df["D1N"].map(UF_NAME_TO_CODE),
            "reference_year": int(reference_year),
            "bovine_herd": _coerce_numeric(df["V"]).astype("Int64"),
            "unit": df["MN"],
            "source_table": "3939",
        }
    )


def fetch_bovine_slaughter_quarterly(reference_year: int = 2024) -> pd.DataFrame:
    """Fetch quarterly slaughter counts and carcass weight by UF."""
    periods = ",".join(str(reference_year * 100 + quarter) for quarter in range(1, 5))
    animals = _payload_to_frame(
        _request_json(
            f"t/1092/n3/all/v/284/p/{periods}/c12716/115236/c18/992/c12529/118225/f/n"
        )
    )
    carcass = _payload_to_frame(
        _request_json(
            f"t/1092/n3/all/v/285/p/{periods}/c12716/115236/c18/992/c12529/118225/f/n"
        )
    )
    animals = animals.rename(columns={"V": "bovine_slaughter", "D3N": "quarter_label"})
    carcass = carcass.rename(columns={"V": "carcass_weight_kg", "D3N": "quarter_label"})
    merged = animals[["D1N", "quarter_label", "bovine_slaughter"]].merge(
        carcass[["D1N", "quarter_label", "carcass_weight_kg"]],
        on=["D1N", "quarter_label"],
        how="left",
    )
    merged["uf"] = merged["D1N"].map(UF_NAME_TO_CODE)
    merged["quarter"] = merged["quarter_label"].str.extract(r"(\d)º").iloc[:, 0].astype(int)
    merged["reference_year"] = reference_year
    merged["bovine_slaughter"] = _coerce_numeric(merged["bovine_slaughter"]).astype("Int64")
    merged["carcass_weight_kg"] = _coerce_numeric(merged["carcass_weight_kg"])
    return merged[["uf", "reference_year", "quarter", "bovine_slaughter", "carcass_weight_kg"]]


def fetch_milk_quarterly(reference_year: int = 2024) -> pd.DataFrame:
    """Fetch quarterly milk volume and average milk price by UF."""
    periods = ",".join(str(reference_year * 100 + quarter) for quarter in range(1, 5))
    volume = _payload_to_frame(
        _request_json(
            f"t/1086/n3/all/v/282/p/{periods}/c12716/115236/c12529/118225/f/n"
        )
    )
    price = _payload_to_frame(
        _request_json(
            f"t/1086/n3/all/v/2522/p/{periods}/c12716/115236/c12529/118225/f/n"
        )
    )
    volume = volume.rename(columns={"V": "milk_production_thousand_liters", "D3N": "quarter_label"})
    price = price.rename(columns={"V": "milk_price_brl_per_liter", "D3N": "quarter_label"})
    merged = volume[["D1N", "quarter_label", "milk_production_thousand_liters"]].merge(
        price[["D1N", "quarter_label", "milk_price_brl_per_liter"]],
        on=["D1N", "quarter_label"],
        how="left",
    )
    merged["uf"] = merged["D1N"].map(UF_NAME_TO_CODE)
    merged["quarter"] = merged["quarter_label"].str.extract(r"(\d)º").iloc[:, 0].astype(int)
    merged["reference_year"] = reference_year
    merged["milk_production_thousand_liters"] = _coerce_numeric(merged["milk_production_thousand_liters"])
    merged["milk_price_brl_per_liter"] = _coerce_numeric(merged["milk_price_brl_per_liter"])
    merged["milk_production_liters"] = merged["milk_production_thousand_liters"] * 1000
    merged["estimated_milk_value_brl"] = (
        merged["milk_production_liters"] * merged["milk_price_brl_per_liter"]
    )
    return merged[
        [
            "uf",
            "reference_year",
            "quarter",
            "milk_production_thousand_liters",
            "milk_production_liters",
            "milk_price_brl_per_liter",
            "estimated_milk_value_brl",
        ]
    ]


def aggregate_bovine_slaughter_year(quarterly_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate slaughter quarterly data into annual totals by UF."""
    annual = (
        quarterly_df.groupby(["uf", "reference_year"], as_index=False)
        .agg(
            bovine_slaughter=("bovine_slaughter", "sum"),
            carcass_weight_kg=("carcass_weight_kg", "sum"),
        )
    )
    return annual


def aggregate_milk_year(quarterly_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate quarterly milk data into annual totals and weighted average price."""
    grouped = quarterly_df.groupby(["uf", "reference_year"], as_index=False).agg(
        milk_production_liters=("milk_production_liters", "sum"),
        estimated_milk_value_brl=("estimated_milk_value_brl", "sum"),
    )
    grouped["milk_price_brl_per_liter"] = (
        grouped["estimated_milk_value_brl"] / grouped["milk_production_liters"]
    )
    return grouped


def create_ibge_source_templates() -> list[SourceMetadata]:
    """Create source metadata rows for the MVP's IBGE-based variables."""
    extraction_date = date.today().isoformat()
    return [
        SourceMetadata(
            variable="bovine_herd",
            description="Efetivo bovino por UF",
            source_name="IBGE SIDRA / PPM tabela 3939",
            source_url="https://apisidra.ibge.gov.br/values/t/3939/n3/all/v/105/p/2024/c79/2670/f/n",
            reference_year="2024",
            extraction_date=extraction_date,
            file_path="data/interim/bovine_herd.csv",
            notes="Variavel 105 com classificacao tipo de rebanho bovino c79=2670.",
        ),
        SourceMetadata(
            variable="bovine_slaughter",
            description="Quantidade anual de bovinos abatidos por UF, agregada dos quatro trimestres",
            source_name="IBGE Pesquisa Trimestral do Abate tabela 1092",
            source_url="https://apisidra.ibge.gov.br/values/t/1092/n3/all/v/284/p/202401,202402,202403,202404/c12716/115236/c18/992/c12529/118225/f/n",
            reference_year="2024",
            extraction_date=extraction_date,
            file_path="data/interim/bovine_slaughter.csv",
            notes="Variavel 284; total do trimestre, total do rebanho bovino e total da inspecao.",
        ),
        SourceMetadata(
            variable="milk_production",
            description="Quantidade anual de leite adquirida por UF, agregada dos quatro trimestres",
            source_name="IBGE Pesquisa Trimestral do Leite tabela 1086",
            source_url="https://apisidra.ibge.gov.br/values/t/1086/n3/all/v/282/p/202401,202402,202403,202404/c12716/115236/c12529/118225/f/n",
            reference_year="2024",
            extraction_date=extraction_date,
            file_path="data/interim/milk_production.csv",
            notes="Variavel 282; total do trimestre e total da inspecao.",
        ),
        SourceMetadata(
            variable="estimated_milk_value_brl",
            description="Valor anual estimado da captacao de leite por UF a partir de volume e preco medio do leite",
            source_name="IBGE Pesquisa Trimestral do Leite tabela 1086",
            source_url="https://apisidra.ibge.gov.br/values/t/1086/n3/all/v/2522/p/202401,202402,202403,202404/c12716/115236/c12529/118225/f/n",
            reference_year="2024",
            extraction_date=extraction_date,
            file_path="data/interim/production_value.csv",
            notes="Preco medio variable 2522. O valor anual e estimado por volume trimestral x preco medio trimestral.",
        ),
    ]
