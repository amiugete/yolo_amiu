

def get_segnalazioni_immagini() -> str: 
    """Restituisce la query per ottenere le segnalazioni immagini. parametri: (limit)"""
    return"""
        SELECT DISTINCT si.ID_RICHIESTA AS id_richiesta  ,si.IMAGES  AS url,sr.DESCRIPTION  AS descrizione_richiesta,
        si.FLG_LETTURA AS flg_lettura,
        si.FLG_ARCHIVIATA AS flg_archiviata
        FROM STRADE.SEGNALAZIONI_IMMAGINI si
        INNER JOIN STRADE.SEGNALAZIONI_RICHIESTE sr ON si.ID_RICHIESTA = sr.ID_RICHIESTA
        WHERE si.FLG_ARCHIVIATA = 1
        AND (:limit IS NULL OR ROWNUM <= :limit)
         """
         
def get_segnalazioni_immagini_da_archiviare() -> str: 
    """Restituisce la query per ottenere le segnalazioni immagini da archiviare. parametri: (limit)"""
    return"""
        SELECT si.ID_RICHIESTA AS id_richiesta  ,si.IMAGES  AS url,sr.DESCRIPTION  AS descrizione_richiesta,
        si.FLG_LETTURA AS flg_lettura,
        si.FLG_ARCHIVIATA AS flg_archiviata
        FROM STRADE.SEGNALAZIONI_IMMAGINI si
        INNER JOIN STRADE.SEGNALAZIONI_RICHIESTE sr ON si.ID_RICHIESTA = sr.ID_RICHIESTA
        WHERE si.ID_RICHIESTA = 503167
        AND (:limit IS NULL OR ROWNUM <= :limit)
         """
         
def get_segnalazioni_immagini_da_archiviare_2() -> str: 
    """Restituisce la query per ottenere le segnalazioni immagini da archiviare. parametri: (limit)"""
    return"""
        SELECT si.ID_RICHIESTA AS id_richiesta  ,si.IMAGES  AS url,sr.DESCRIPTION  AS descrizione_richiesta,
        si.FLG_LETTURA AS flg_lettura,
        si.FLG_ARCHIVIATA AS flg_archiviata
        FROM STRADE.SEGNALAZIONI_IMMAGINI si
        INNER JOIN STRADE.SEGNALAZIONI_RICHIESTE sr ON si.ID_RICHIESTA = sr.ID_RICHIESTA
        WHERE (si.FLG_ARCHIVIATA = 0 OR si.FLG_ARCHIVIATA IS NULL)
        AND (:limit IS NULL OR ROWNUM <= :limit)
         """
         
         
def update_flg_archiviata_segnalazioni_immagini() -> str:
    """Restituisce la query per aggiornare il flag archiviata a 1 per le segnalazioni immagini processate"""
    return """
        UPDATE STRADE.SEGNALAZIONI_IMMAGINI
        SET FLG_ARCHIVIATA = 1
        WHERE ID_RICHIESTA = :id_richiesta
        AND IMAGES = :url
    """


def update_flg_archiviata_segnalazioni_immagini_to_zero() -> str:
    """Restituisce la query per resettare il flag archiviata a 0 per una richiesta archiviate."""
    return """
        UPDATE STRADE.SEGNALAZIONI_IMMAGINI
        SET FLG_ARCHIVIATA = 0
        WHERE ID_RICHIESTA = :id_richiesta
        AND FLG_ARCHIVIATA = 1
    """         