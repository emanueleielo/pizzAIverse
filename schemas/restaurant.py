from pydantic import BaseModel, Field
from typing import List, Optional

class Licenza(BaseModel):
    """Classe che rappresenta una licenza culinaria necessaria per l'esercizio di specifiche tecniche intergalattiche."""
    nome: str = Field(..., description="Nome della licenza culinaria")
    livello: int = Field(..., description="Livello della licenza")
    anno_ottenimento: Optional[int] = Field(None, description="Anno in cui la licenza è stata ottenuta (se disponibile)")

class TecnicaCulinaria(BaseModel):
    """Classe che rappresenta una tecnica culinaria avanzata utilizzata nella preparazione dei piatti."""
    nome: str = Field(..., description="Nome della tecnica culinaria")
    descrizione: Optional[str] = Field(None, description="Descrizione della tecnica culinaria")

class Ingrediente(BaseModel):
    """Classe che rappresenta un ingrediente utilizzato nei piatti intergalattici."""
    nome: str = Field(..., description="Nome dell'ingrediente")
    origine: Optional[str] = Field(None, description="Origine dell'ingrediente, se specificata")

class Piatto(BaseModel):
    """Classe che rappresenta un piatto servito in un ristorante intergalattico."""
    nome: str = Field(..., description="Nome del piatto")
    descrizione: Optional[str] = Field(None, description="Descrizione del piatto e della sua esperienza sensoriale")
    ingredienti: List[Ingrediente] = Field(..., description="Lista degli ingredienti utilizzati nel piatto")
    tecniche: List[TecnicaCulinaria] = Field(..., description="Lista delle tecniche di cottura o preparazione applicate")

class Recensione(BaseModel):
    """Classe che rappresenta una recensione di un critico gastronomico intergalattico su un ristorante."""
    titolo: str = Field(..., description="Titolo della recensione")
    autore: str = Field(..., description="Nome del critico gastronomico che ha scritto la recensione")
    pubblicazione: str = Field(..., description="Nome della pubblicazione intergalattica in cui è stata pubblicata la recensione")
    contenuto: str = Field(..., description="Testo completo della recensione")
    voto: float = Field(..., description="Valutazione numerica del ristorante su una scala da 0 a 10")


class Ristorante(BaseModel):
    """Classe che rappresenta un ristorante intergalattico con il suo menu e la sua filosofia culinaria."""
    nome: str = Field(..., description="Nome del ristorante")
    pianeta: str = Field(..., description="Pianeta in cui si trova il ristorante")
    chef: str = Field(..., description="Nome dello chef principale del ristorante")
    descrizione: str = Field(..., description="Descrizione del ristorante e della sua visione culinaria")
    licenze: List[Licenza] = Field(..., description="Lista delle licenze e certificazioni ottenute dal ristorante")
    menu: List[Piatto] = Field(..., description="Lista dei piatti serviti nel ristorante")
    recensioni: List[Recensione] = Field(..., description="Lista di recensioni gastronomiche intergalattiche")


