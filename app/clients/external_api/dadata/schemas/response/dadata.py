from pydantic import BaseModel


class DadataCountryData(BaseModel):
    code: int
    alfa2: str
    alfa3: str
    name_short: str
    name: str


class DadataCountrySuggestion(BaseModel):
    value: str
    unrestricted_value: str
    data: DadataCountryData


class DadataCountryResponse(BaseModel):
    suggestions: list[DadataCountrySuggestion]
