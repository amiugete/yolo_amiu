from pydantic import BaseModel
from typing import Optional

class SegnalazioneImmagine(BaseModel):
    id_richiesta: Optional[int] = None
    url: Optional[str] = None
    descrizione_richiesta: Optional[str] = None
    flg_lettura: Optional[int] = None  # 0 = non letta, 1 = letta






