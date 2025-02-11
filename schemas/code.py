from pydantic import BaseModel, Field
from typing import List, Optional

class Ordine(BaseModel):
    """Classe che rappresenta un ordine professionale gastronomico nella Federazione Galattica."""
    nome: str = Field(..., description="Nome dell'ordine gastronomico")
    descrizione: str = Field(..., description="Descrizione dell'ordine e delle sue regole")

class SostanzaRegolamentata(BaseModel):
    """Classe che rappresenta una sostanza regolamentata dal Codice Galattico."""
    nome: str = Field(..., description="Nome della sostanza regolamentata")
    categoria: str = Field(..., description="Categoria della sostanza (Psicotrope, Mitiche, Xenobiologiche, Quantiche, Spazio-Temporali)")
    crp: Optional[float] = Field(None, description="CRP - Coefficiente di Risonanza Psionica (solo per sostanze psioniche)")
    ipm: Optional[float] = Field(None, description="IPM - Indice di Purezza Mitica (solo per sostanze mitiche)")
    ibx: Optional[float] = Field(None, description="IBX - Indice di Bioattività Xeno (solo per sostanze xenobiologiche)")
    iei: Optional[float] = Field(None, description="IEI")
    deltaQ: Optional[float] = Field(None, description="δQ - Fluttuazione Quantica (solo per sostanze quantiche)")
    mi: Optional[float] = Field(None, description="μ - Potenziale di mutazione per sostanze IBX (solo per sostanze xenobiologiche)")
    cdt: Optional[float] = Field(None, description="CDT - Coefficiente di Distorsione Temporale (solo per sostanze spazio-temporali)")
    theta: Optional[float] = Field(None, description="θ")
    limiti: str = Field(..., description="Descrizione delle restrizioni applicate alla sostanza")

class TecnicaCulinaria(BaseModel):
    """Classe che rappresenta una tecnica culinaria regolamentata."""
    nome: str = Field(..., description="Nome della tecnica culinaria")
    categoria: str = Field(..., description="Categoria della tecnica (es. Marinatura, Affumicatura, Fermentazione, Cottura, etc.)")
    descrizione: str = Field(..., description="Descrizione della tecnica culinaria e delle sue caratteristiche")
    licenze_richieste: List[str] = Field(..., description="Lista delle licenze necessarie per eseguire questa tecnica")
    grado_tecnologico: str = Field(..., description="Livello tecnologico richiesto per eseguire la tecnica")

class Licenza(BaseModel):
    """Classe che rappresenta una licenza necessaria per l'esercizio delle tecniche culinarie intergalattiche."""
    nome: str = Field(..., description="Nome della licenza")
    categoria: str = Field(..., description="Categoria della licenza (Psionica, Gravitazionale, Antimateria, Magnetica, Quantistica, Temporale)")
    livello: int = Field(..., description="Livello della licenza richiesto")

class Sanzione(BaseModel):
    """Classe che rappresenta una sanzione prevista dal Codice Galattico per violazioni alle norme alimentari."""
    violazione: str = Field(..., description="Descrizione della violazione al codice")
    categorie_coinvolte: List[str] = Field(..., description="Categorie protette coinvolte nella violazione")
    gravita: str = Field(..., description="Gravità dell'infrazione (bassa, media, alta)")
    penalita: str = Field(..., description="Tipo di sanzione applicata per questa violazione")

class CodiceGalattico(BaseModel):
    """Classe principale che rappresenta l'intero Codice Galattico e le sue regolamentazioni."""
    ordini_professionali: List[Ordine] = Field(..., description="Lista degli ordini professionali regolamentati nel codice")
    sostanze_regolamentate: List[SostanzaRegolamentata] = Field(..., description="Lista delle sostanze regolamentate e dei loro limiti di utilizzo")
    tecniche_culinarie: List[TecnicaCulinaria] = Field(..., description="Lista delle tecniche culinarie regolamentate con relative licenze richieste")
    licenze_disponibili: List[Licenza] = Field(..., description="Lista delle licenze ufficialmente riconosciute")
    sanzioni: List[Sanzione] = Field(..., description="Lista delle sanzioni previste per le violazioni alle normative alimentari")

