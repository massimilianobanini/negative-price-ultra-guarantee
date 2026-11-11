# Procedura per mantenere gli indici aggiornati

**Fonte operativa privata:** Google Sheet dell'autore *The -1 Guarantee - Editorial Map*. Non collegare pubblicamente il documento privato senza autorizzazione.

1. Dalla scheda **ARTICLES** includere **solo** righe con `Article ID`, data, titolo e URL Substack canonico; non includere duplicati.
2. Dalla scheda **VIDEOS** includere **solo** video confermati come pubblicati con URL YouTube; **VIDEO_CANDIDATES** contiene idee e non deve essere spacciata per catalogo pubblico.
3. Aggiornare insieme i due file `.md` e `.json` di ciascun catalogo, il conteggio e la data dello snapshot.
4. Per i video mantenere il legame all'`Article ID` solo quando verificato; non inventare transcript o mappature.
5. Non copiare in pubblico dati di analisi interni, metriche private o campi del foglio non destinati alla diffusione.
6. Controllare a campione link più vecchi, ultimi dieci link e duplicati.
7. Il radar editoriale già esistente che aggiorna il foglio **non aggiorna automaticamente questo repository**: serve un'ulteriore integrazione autorizzata dopo la pubblicazione.

## Riconciliazione del 11 novembre 2026

- La mappa editoriale privata contiene **SUB-001–SUB-301** (301 articoli, fino al 10 novembre 2026).
- Il catalogo pubblico di questo repository è stato riallineato a **301 URL canonici unici**, includendo SUB-299, SUB-300 e SUB-301; mantiene SUB-220 con URL canonico corretto e SUB-279.
- La [sitemap pubblica di The -1 Guarantee](https://github.com/massimilianobanini/theminusoneguarantee-sitemap) è stata corretta nella stessa sessione: **301 articoli**, con URL SUB-220 riparato e SUB-279 recuperato.
- **Questi aggiornamenti sono manuali/assistiti, non una nuova automazione**: lo script Gmail → Apps Script esistente alimenta la sitemap, mentre questo repository richiede ancora una procedura di sincronizzazione dedicata.
- **Fonte di verità per ID, titoli e sottotitoli:** la mappa editoriale privata verificata. La sitemap pubblica può essere usata come segnale di nuovi URL, non come sostituto dei titoli canonici, perché il suo parser Gmail può usare metadati abbreviati.
