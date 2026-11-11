# Procedura per mantenere gli indici aggiornati

**Fonte operativa privata:** Google Sheet dell'autore *The -1 Guarantee - Editorial Map*. Non collegare pubblicamente il documento privato senza autorizzazione.

1. Dalla scheda **ARTICLES** includere **solo** righe con `Article ID`, data, titolo e URL Substack canonico; non includere duplicati.
2. Dalla scheda **VIDEOS** includere **solo** video confermati come pubblicati con URL YouTube; **VIDEO_CANDIDATES** contiene idee e non deve essere spacciata per catalogo pubblico.
3. Aggiornare insieme i due file `.md` e `.json` di ciascun catalogo, il conteggio e la data dello snapshot.
4. Per i video mantenere il legame all'`Article ID` solo quando verificato; non inventare transcript o mappature.
5. Non copiare in pubblico dati di analisi interni, metriche private o campi del foglio non destinati alla diffusione.
6. Controllare a campione link più vecchi, ultimi dieci link e duplicati.
7. La mappa editoriale privata resta il riferimento per **titoli e sottotitoli verificati**. Gli indici Substack di questo repository **si aggiornano ora automaticamente** dal repository sitemap pubblico; il radar/editorial map può richiedere una **riconciliazione successiva dei metadati** importati come provvisori.
8. Il catalogo YouTube non rientra in questa automazione: aggiornare solo video effettivamente pubblicati.

## Riconciliazione del 11 novembre 2026

- La mappa editoriale privata contiene **SUB-001–SUB-301** (301 articoli, fino al 10 novembre 2026).
- Il catalogo pubblico di questo repository è stato riallineato a **301 URL canonici unici**, includendo SUB-299, SUB-300 e SUB-301; mantiene SUB-220 con URL canonico corretto e SUB-279.
- La [sitemap pubblica di The -1 Guarantee](https://github.com/massimilianobanini/theminusoneguarantee-sitemap) è stata corretta nella stessa sessione: **301 articoli**, con URL SUB-220 riparato e SUB-279 recuperato.
- La riconciliazione iniziale dei 301 articoli è stata effettuata manualmente/assistita. **Successivamente, l'11 novembre 2026, è stata installata una sincronizzazione automatica** tra il repository pubblico della sitemap e il presente repository.
- **Fonte di verità per ID, titoli e sottotitoli:** la mappa editoriale privata verificata. La sitemap pubblica può essere usata come segnale di nuovi URL, non come sostituto dei titoli canonici, perché il suo parser Gmail può usare metadati abbreviati.

## Automazione attiva — GitHub Actions, dal 11 novembre 2026

- **Workflow:** [`.github/workflows/sync-substack-sitemap.yml`](.github/workflows/sync-substack-sitemap.yml) e [cronologia esecuzioni](https://github.com/massimilianobanini/negative-price-ultra-guarantee/actions/workflows/sync-substack-sitemap.yml).
- **Frequenza:** ogni 3 ore, ai minuti 17 UTC; disponibile anche **Run workflow** nell'interfaccia Actions. Non si basa su un token personale aggiuntivo.
- **Sorgente:** [`articles.json` pubblico della sitemap](https://github.com/massimilianobanini/theminusoneguarantee-sitemap/blob/main/articles.json), alimentato separatamente da Gmail → Apps Script; la credenziale di quella prima automazione **va mantenuta valida**.
- **Destinazioni:** `fonti/substack-articles.json` e `fonti/substack-articoli.md`. **Append-only**: gli articoli già catalogati non vengono modificati o cancellati; nessun nuovo commit quando non ci sono nuove uscite.
- **ID:** assegnati in ordine cronologico in forma `SUB-302`, `SUB-303`, ecc., soltanto per articoli successivi all'ultimo esistente. Nuove pubblicazioni storiche o dello stesso giorno richiedono una verifica di ordine e ID, quindi interrompono il workflow invece di introdurre errori silenziosi.
- **Qualità:** i metadati **nuovi** derivano dall'archivio Gmail pubblico e vengono marcati `metadata_status = provvisorio_da_verificare_con_mappa_editoriale`. La formula generica «View this post on the web at ...» **non viene trattata come un sottotitolo editoriale**. I titoli potenzialmente troncati con ellissi vengono segnalati.
- **Controlli:** URL su dominio Substack atteso, unicità, ID consecutivi, date coerenti, confronto tra storico del repository sorgente e destinazione; se la sorgente perde URL storici, la scrittura **fallisce senza cancellare nulla**. [Test Python](tests/test_sync_substack.py) eseguiti ad ogni run.
- **Credenziali:** lettura senza autenticazione dalla sitemap **pubblica**; `GITHUB_TOKEN` temporaneo con permesso `contents: write` solo per effettuare eventuali commit nel repository destinazione. Il token **Substack Gmail to GitHub** rimane necessario **solo** per l'automazione Gmail → Apps Script → sitemap.
- **Come verificare:** GitHub → repository Ultra-Garanzia → **Actions → Sync Substack public archive**. Verde = test e riconciliazione eseguiti senza errore; un run riuscito **non prova** da solo che siano stati pubblicati nuovi articoli. Un nuovo commit automatico compare solo quando il catalogo cambia.
- **Limiti:** la frequenza GitHub Actions non è garantita al minuto; i job schedulati possono subire ritardi. L'automazione non sostituisce la verifica quotidiana del Google Sheet privato.
