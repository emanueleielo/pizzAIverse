from pydantic import BaseModel, Field
from typing import List, Optional


class Licenza(BaseModel):
    """Classe che rappresenta una licenza culinaria intergalattica necessaria per l'esercizio di specifiche tecniche di cucina spaziale."""
    nome: str = Field(..., description="Nome della licenza culinaria")
    livello: int = Field(..., description="Livello della licenza (es. da 0 a VI+)")
    descrizione: str = Field(..., description="Descrizione delle capacità e delle limitazioni del livello di licenza")


class OrdineGastronomico(BaseModel):
    """Classe che rappresenta un ordine gastronomico con le sue regole e principi specifici."""
    nome: str = Field(..., description="Nome dell'ordine gastronomico")
    descrizione: str = Field(..., description="Descrizione dell'ordine e delle sue regole fondamentali")


class TecnicaPreparazione(BaseModel):
    """Classe che rappresenta una tecnica di preparazione culinaria avanzata."""
    nome: str = Field(..., description="Nome della tecnica di preparazione")
    descrizione: str = Field(..., description="Descrizione del processo di preparazione")
    vantaggi: str = Field(..., description="Benefici della tecnica")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o rischi associati alla tecnica")


class TecnicaCottura(BaseModel):
    """Classe che rappresenta una tecnica di cottura avanzata utilizzata nello spazio."""
    nome: str = Field(..., description="Nome della tecnica di cottura")
    descrizione: str = Field(..., description="Descrizione del funzionamento della tecnica di cottura")
    vantaggi: str = Field(..., description="Benefici della tecnica di cottura")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o potenziali problematiche nell'uso della tecnica")


class TecnicaTaglio(BaseModel):
    """Classe che rappresenta una tecnica avanzata di taglio degli ingredienti nello spazio."""
    nome: str = Field(..., description="Nome della tecnica di taglio")
    descrizione: str = Field(..., description="Descrizione della tecnica di taglio")
    vantaggi: str = Field(..., description="Benefici della tecnica di taglio")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o problemi legati alla tecnica di taglio")


class TecnicaAffumicatura(BaseModel):
    """Classe che rappresenta una tecnica di affumicatura avanzata utilizzata nella cucina intergalattica."""
    nome: str = Field(..., description="Nome della tecnica di affumicatura")
    descrizione: str = Field(..., description="Descrizione del processo di affumicatura")
    vantaggi: str = Field(..., description="Benefici della tecnica di affumicatura")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o limiti della tecnica")


class TecnicaFermentazione(BaseModel):
    """Classe che rappresenta una tecnica di fermentazione avanzata utilizzata nello spazio."""
    nome: str = Field(..., description="Nome della tecnica di fermentazione")
    descrizione: str = Field(..., description="Descrizione del processo di fermentazione")
    vantaggi: str = Field(..., description="Benefici della fermentazione")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o rischi associati alla tecnica")


class TecnicaImpasto(BaseModel):
    """Classe che rappresenta una tecnica avanzata di impasto intergalattico."""
    nome: str = Field(..., description="Nome della tecnica di impasto")
    descrizione: str = Field(..., description="Descrizione del metodo di impasto")
    vantaggi: str = Field(..., description="Benefici dell'impasto")
    svantaggi: Optional[str] = Field(None, description="Svantaggi della tecnica di impasto")


class TecnicaSferificazione(BaseModel):
    """Classe che rappresenta una tecnica avanzata di sferificazione utilizzata nella cucina intergalattica."""
    nome: str = Field(..., description="Nome della tecnica di sferificazione")
    descrizione: str = Field(..., description="Descrizione del processo di sferificazione")
    vantaggi: str = Field(..., description="Benefici della tecnica di sferificazione")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o limiti della tecnica")


class TecnicaDecostruzione(BaseModel):
    """Classe che rappresenta una tecnica avanzata di decostruzione nella cucina intergalattica."""
    nome: str = Field(..., description="Nome della tecnica di decostruzione")
    descrizione: str = Field(..., description="Descrizione del processo di decostruzione culinaria")
    vantaggi: str = Field(..., description="Benefici della tecnica di decostruzione")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o problemi della tecnica")


class TecnicaSottovuoto(BaseModel):
    """Classe che rappresenta una tecnica avanzata di cottura sottovuoto utilizzata nello spazio."""
    nome: str = Field(..., description="Nome della tecnica di cottura sottovuoto")
    descrizione: str = Field(..., description="Descrizione della tecnica di cottura sottovuoto")
    vantaggi: str = Field(..., description="Benefici della tecnica di cottura sottovuoto")
    svantaggi: Optional[str] = Field(None, description="Svantaggi o problemi della tecnica")


class ManualeCucinaSpaziale(BaseModel):
    """Classe che rappresenta il manuale di cucina intergalattica di Sirius Cosmo."""
    autore: str = Field(..., description="Nome dell'autore del manuale")
    introduzione: str = Field(..., description="Introduzione del manuale")
    licenze: List[Licenza] = Field(..., description="Lista delle licenze culinarie richieste")
    ordini_gastronomici: List[OrdineGastronomico] = Field(..., description="Lista degli ordini gastronomici esistenti")
    tecniche_preparazione: List[TecnicaPreparazione] = Field(..., description="Lista delle tecniche di preparazione")
    tecniche_cottura: List[TecnicaCottura] = Field(..., description="Lista delle tecniche di cottura")
    tecniche_taglio: List[TecnicaTaglio] = Field(..., description="Lista delle tecniche di taglio")
    tecniche_affumicatura: List[TecnicaAffumicatura] = Field(..., description="Lista delle tecniche di affumicatura")
    tecniche_fermentazione: List[TecnicaFermentazione] = Field(..., description="Lista delle tecniche di fermentazione")
    tecniche_impasto: List[TecnicaImpasto] = Field(..., description="Lista delle tecniche di impasto")
    tecniche_sferificazione: List[TecnicaSferificazione] = Field(..., description="Lista delle tecniche di sferificazione")
    tecniche_decostruzione: List[TecnicaDecostruzione] = Field(..., description="Lista delle tecniche di decostruzione")
    tecniche_sottovuoto: List[TecnicaSottovuoto] = Field(..., description="Lista delle tecniche di cottura sottovuoto")
