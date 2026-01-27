

def get_segnalazioni_immagini() -> str:
    """Restituisce la query per ottenere le segnalazioni immagini. parametri: (limit)"""
    return"""
        SELECT si.ID_RICHIESTA AS id_richiesta  ,si.IMAGES  AS url,sr.DESCRIPTION  AS descrizione_richiesta FROM STRADE.SEGNALAZIONI_IMMAGINI si
        INNER JOIN STRADE.SEGNALAZIONI_RICHIESTE sr ON si.ID_RICHIESTA = sr.ID_RICHIESTA
        WHERE  ROWNUM <= :limit
         """