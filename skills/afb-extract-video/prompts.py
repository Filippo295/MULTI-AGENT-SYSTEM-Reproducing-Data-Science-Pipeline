# AUTO-EXTRACTED VERBATIM from the original notebook — do not hand-edit.
from typing import Literal  # noqa
from pydantic import BaseModel, Field  # noqa

system_prompt = """
=== RUOLO ===
Sei un esperto analista di marketing nel campo dei social media, con vasta esperienza nell'analisi 
di contenuti video. Sei un professionista capace di identificare caratteristiche comunicative 
rilevanti da Reels e Stories Instagram e TikTok, con particolare attenzione agli elementi audio, visivi,  
corporei e alla performance vocale del creator.

=== CONTESTO ===
Aiuterai un gruppo di studenti in un progetto di data science focalizzato sull'analisi di contenuti 
video social e su cosa influenza l'engagement. Oltre alle feature testuali, è fondamentale estrarre 
feature strutturate legate alla componente audio e vocale del video.

=== TASK ===
Ti verrà fornito un video di un post Instagram Reel o TikTok. Il tuo obiettivo è estrarre esattamente 
le seguenti variabili dal video, seguendo attentamente le descrizioni e le categorie fornite per ciascuna.

=== VARIABILI DA ESTRARRE ===

tone_video: Estrai dal VIDEO. è il registro comunicativo complessivo del creator nel video, valutato 
attraverso la combinazione del tono della voce e del contenuto di ciò che viene detto. 

---

voice_speed_video: Estrai dal VIDEO. è il ritmo e la velocità del parlato del creator nel video.
Valuta la velocità media del parlato, ignorando pause musicali o silenzi non legati al parlato.
La musica di sottofondo e le scritte a schermo non costituiscono parlato e non vanno considerate. 

---

microkinetics_video: Estrai dal VIDEO. Classifica il comportamento non verbale del creator
secondo due assi INDIPENDENTI adattati dal modello Mehrabian (solo 
Dominance e Arousal; l'asse Pleasure/Valence è escluso):
• DOMINANCE — quanto il creator controlla e occupa lo spazio scenico 
(dominante vs contenuto).
• AROUSAL — quanta energia cinetica corporea esprime 
(attivato vs calmo).
Valuta SOLO marker fisicamente osservabili. NON valutare intenzione 
del creator, effetto sul pubblico, contenuto verbale o valenza 
emotiva.

---

activity_video: Estrai dal VIDEO. indica cosa sta facendo il creator nel video. La musica di sottofondo e le scritte 
a schermo non costituiscono parlato e non vanno considerate ai fini di questa variabile.

---

format_video: Estrai dal VIDEO. è il formato narrativo del contenuto video, ovvero la logica strutturale che guida 
il video. Non valutare il tema trattato, ma come il prodotto viene contestualizzato 
e cosa determina la struttura del video. Se il video combina più formati, scegli quello 
dominante per la maggior parte della durata.

---

product_integration: Estrai dal VIDEO. è la modalità con cui il prodotto o servizio brandizzato è presente 
nel contenuto video. Valuta esclusivamente ciò che appare o viene detto nel video, 
non il testo della caption. Basati su un unico criterio: cosa fa il creator con il prodotto o servizio.

---

funnel: Estrai dal VIDEO. è l'intenzione commerciale del contenuto, ovvero cosa vuole ottenere dal pubblico 
in termini di risposta. Non valutare il formato né come appare il prodotto, ma quale 
azione o stato mentale il contenuto sta cercando di generare nello spettatore.

---

posizionento: Estrai dal VIDEO. è la fascia di prezzo del brand o prodotto citato nel video, valutata 
in base alla categoria merceologica e al posizionamento noto del brand sul mercato. Non 
considerare l'estetica del video, il tono del creator o il contesto di presentazione, 
valuta esclusivamente il tipo di prodotto e il brand.
Scegli UNA delle seguenti categorie:


=== FORMATO DI OUTPUT ===
Rispondi SOLO con un oggetto JSON contenente tutte le variabili.
Nessuna spiegazione, nessun testo aggiuntivo.

=== LINEE GUIDA AGGIUNTIVE ===
Ragiona attentamente prima di rispondere.
Estrai il valore basandoti esclusivamente sulle descrizioni fornite.
Dove una variabile ha una procedura a passi, segui quella procedura nell'ordine indicato.
Dove una variabile NON ha una procedura esplicita, basati sulle definizioni fornite e, 
in caso di ambiguità, scegli la categoria più coerente con il comportamento predominante (nel caso di microkinetics),
o con il contenuto predominante della caption (per le altre variabili).
Non inventare informazioni non osservabili nel video.
"""


class Features(BaseModel):
    tone_video: Literal[
        "entusiasta/energico",
        "ironico/scherzoso",
        "calmo/confidenziale",
        "logico/informativo",
        "neutro/assente"
    ] = Field(
        description=("""
        Estrai dal VIDEO. è il registro comunicativo complessivo del creator nel video, valutato 
        attraverso la combinazione del tono della voce e del contenuto di ciò che viene detto. 
        Scegli UNA delle seguenti categorie:
        - "entusiasta/energico": voce vivace e ad alta energia, con esclamazioni frequenti e ritmo 
        incalzante. Il creator dice cose positive, esaltanti o di forte impatto emotivo, 
        comunicando eccitazione sia nel modo che nel contenuto.
        Esempi: "Ragazzi è PAZZESCO, non ci posso credere!!!", "Dovete assolutamente provarlo, 
        è una figata assurda!", esclamazioni continue, voce che sale di tono, frasi che esprimono 
        entusiasmo genuino per un'esperienza o una scoperta.

        - "ironico/scherzoso": tono leggero con inflessioni comiche, pause strategiche per effetto 
        umoristico. Il creator dice cose divertenti, usa battute, doppi sensi o situazioni assurde. 
        Sia la voce che le parole segnalano che il contenuto non va preso sul serio.
        Esempi: tono esageratamente serio su argomenti banali, imitazioni vocali accompagnate da 
        commenti comici, pause comiche prima di una battuta, racconto di situazioni assurde con 
        tono canzonatorio.

        - "calmo/confidenziale": tono basso e pacato, registro intimo e conversazionale. Il creator 
        dice cose personali, riflessive o private, come se stesse confidando qualcosa allo spettatore. 
        La voce e le parole trasmettono insieme vicinanza e autenticità.
        Esempi: "Vi racconto una cosa…", voce quasi sussurrata mentre condivide un'esperienza 
        personale, tono da chiacchierata tra amici abbinato a contenuti di vita quotidiana, 
        riflessioni intime dette con naturalezza.

        - "logico/informativo": tono deciso, chiaro e strutturato. Il creator dice cose concrete, 
        spiega procedimenti, fornisce informazioni o dati. Voce e parole comunicano competenza 
        e padronanza dell'argomento.
        Esempi: "Il primo passaggio è…", "È importante sapere che…", voce che scandisce bene 
        le parole mentre spiega istruzioni o fatti, ritmo costante abbinato a contenuto 
        strutturato e informativo.

        - "neutro/assente": voce piatta o assente, contenuto verbale minimo o inesistente. 
        Il creator non dice nulla di significativo oppure non parla affatto.
        Esempi: voce monocorde che legge uno script senza coinvolgimento, video basato su 
        testo a schermo o musica senza parlato umano, creator presente visivamente ma 
        silenzioso per tutta la durata del video.        
        """)
    )
    voice_speed_video: Literal[
        "lenta",
        "normale",
        "veloce",
        "assente"
    ] = Field(
        description=(""""
        Estrai dal VIDEO. è il ritmo e la velocità del parlato del creator nel video. Valuta la velocità 
        media del parlato, ignorando pause musicali o silenzi non legati al parlato. La musica di 
        sottofondo e le scritte a schermo non costituiscono parlato e non vanno considerate.
        Scegli UNA delle seguenti categorie:

        - "lenta": il parlato è percepibilmente più lento di una conversazione quotidiana. Le parole 
        sono scandite una alla volta con pause lunghe tra una frase e l'altra, il creator sembra 
        pesare ogni concetto prima di dirlo. La sensazione è che il video potrebbe venire accelerato 
        senza perdere nulla.
        Esempi: creator che parla con enfasi e pause ponderate tra un concetto e l'altro, tono 
        meditativo o solenne, sensazione che ogni parola venga pesata prima di essere detta.

        - "normale": il ritmo corrisponde a quello di una conversazione faccia a faccia. Le frasi 
        scorrono con pause brevi e naturali, il flusso non richiede sforzo per essere seguito né 
        trasmette fretta. È il ritmo con cui si racconta qualcosa a una persona.
        Esempi: creator che racconta un aneddoto o spiega qualcosa con calma, senza effetti di 
        velocità in nessuna direzione.

        - "veloce": il parlato è percepibilmente più rapido di una conversazione quotidiana. Le frasi 
        si susseguono con pause minime o assenti, le parole si accavallano quasi, seguire il discorso 
        richiede attenzione attiva. La sensazione è che il creator stia cercando di dire il massimo 
        nel minor tempo possibile.
        Esempi: creator che parla senza fermarsi tra un pensiero e l'altro, flusso quasi ininterrotto 
        di parole, sensazione di dover stare attenti per seguire tutto.

        - "assente": nessuna voce umana presente nel video. Rientrano in questa categoria anche i video 
        con sola musica senza parlato e i video basati esclusivamente su scritte a schermo senza 
        voce del creator.
        """)
    )
    microkinetics_video: Literal[
        "charismatic_performer",
        "authoritative_expert",
        "soft_engager",
        "intimate_confidant",
        "assente",
    ] = Field(
        description=(
        "Estrai dal VIDEO. Classifica il comportamento non verbale del creator "
        "secondo due assi INDIPENDENTI adattati dal modello Mehrabian (solo "
        "Dominance e Arousal; l'asse Pleasure/Valence è escluso):\n"
        "• DOMINANCE — quanto il creator controlla e occupa lo spazio scenico "
        "(dominante vs contenuto).\n"
        "• AROUSAL — quanta energia cinetica corporea esprime "
        "(attivato vs calmo).\n\n"
        "Valuta SOLO marker fisicamente osservabili. NON valutare intenzione "
        "del creator, effetto sul pubblico, contenuto verbale o valenza "
        "emotiva.\n\n"

        # ── PASSO 0 — SCREENING 'ASSENTE' ──────────────────────────────
        "═══ PASSO 0 · SCREENING 'ASSENTE' ═══\n"
        "Il creator si rivolge alla camera in modo performativo per almeno "
        "~5 secondi complessivi E il suo volto è chiaramente visibile?\n"
        "→ NO: classifica 'assente'. STOP.\n"
        "Rientrano in 'assente': "
        "(i) video senza volto umano del creator (solo mani, oggetti, "
        "scenografie — non confondere oggetti tondi/scuri per occhi); "
        "(ii) video candid (ballo, shopping, prova vestiti, interazione "
        "con altri) senza address diretto e sostenuto all'audience; "
        "(iii) b-roll senza creator in campo; "
        "(iv) creator inquadrato solo parzialmente o presente per meno "
        "di ~5 secondi performativi.\n"
        "→ SÌ: prosegui al Passo 0b.\n\n"

        # ── PASSO 0b — VIDEO MISTI ─────────────────────────────────────
        "═══ PASSO 0b · VIDEO MISTI ═══\n"
        "Se il video alterna momenti performativi e non performativi, "
        "valuta SOLO i momenti performativi verso la camera. Se questi "
        "momenti hanno registri corporei diversi (es. prima calmo, poi "
        "energico), usa il registro prevalente per durata.\n\n"

        # ── PASSO 1 — DOMINANCE ────────────────────────────────────────
        "═══ PASSO 1 · VALUTA DOMINANCE ═══\n"
        "Osserva postura, occupazione dello spazio e zona delle mani.\n\n"

        "Definizioni spaziali (riferite al corpo anatomico, non al frame):\n"
        "• 'zona ampia': mani che escono lateralmente oltre le spalle, "
        "O salgono sopra le spalle, O si protendono verso la camera.\n"
        "• 'zona contenuta': mani tra ombelico e clavicola, entro la "
        "larghezza delle spalle.\n"
        "• 'postura aperta': busto frontale, spalle indietro, petto "
        "visibile, palmi visibili almeno a tratti.\n"
        "• 'postura raccolta': spalle in linea naturale o avanti, busto "
        "poco proteso, gesti vicini al corpo.\n\n"

        "D+ (dominante) — il creator occupa attivamente lo spazio scenico. "
        "Assegna D+ se osservi una COMBINAZIONE di almeno due dei seguenti "
        "marker:\n"
        "  · zona ampia anatomica ricorrente (≥2 volte ogni 10s) con "
        "intento comunicativo\n"
        "  · postura aperta sostenuta per la maggior parte del tempo "
        "performativo\n"
        "  · sguardo fisso in lente sostenuto\n"
        "  · busto proteso verso la camera; corpo che riempie "
        "l'inquadratura intenzionalmente (non solo per prossimità "
        "della camera)\n"
        "ECCEZIONE: performance teatrale evidente (skit recitato, "
        "personaggio interpretato) → D+ anche da sola, anche se la "
        "gestualità del personaggio è raccolta.\n"
        "Nota: gesti ampi funzionali (alzare un piatto, mettere una "
        "borsa a tracolla) NON sono marker D+, salvo showmanship "
        "esplicito.\n\n"

        "D− (contenuto) — il creator occupa poco spazio scenico. "
        "Assegna D− se sono presenti TUTTI i seguenti:\n"
        "  · zona contenuta per ≥80% del tempo performativo\n"
        "  · postura raccolta\n"
        "  · performance non teatralizzata\n\n"

        "Se né D+ né D− sono chiaramente soddisfatti, scegli quello "
        "più vicino ai marker osservati.\n\n"

        # ── PASSO 2 — AROUSAL ──────────────────────────────────────────
        "═══ PASSO 2 · VALUTA AROUSAL ═══\n"
        "Osserva frequenza gestuale, velocità dei movimenti, mimica "
        "facciale e stabilità del busto. Valuta questo asse IN MODO "
        "INDIPENDENTE dalla Dominance appena assegnata.\n\n"

        "Definizioni:\n"
        "• 'gesto comunicativo': movimento intenzionale di una mano che "
        "cambia chiaramente posizione (non micro-aggiustamento).\n"
        "• 'cambio di espressione marcato': passaggio visibile tra due "
        "stati facciali distinti.\n\n"

        "A+ (attivato) — il corpo esprime alta energia cinetica. "
        "Assegna A+ se osservi almeno DUE dei seguenti marker in modo "
        "chiaro e sostenuto (non episodi isolati):\n"
        "  · gesti comunicativi frequenti (≥3 ogni 5s)\n"
        "  · movimenti rapidi o a scatti\n"
        "  · mimica caricaturale (occhi spalancati, smorfie, espressioni "
        "'meme', sopracciglia cartoon)\n"
        "  · cambi di posizione del busto frequenti (salti, rotazioni, "
        "oscillazioni, avvicinamenti bruschi alla camera)\n"
        "  · jump cut / zoom dinamici sincronizzati con i movimenti del "
        "creator\n\n"

        "A− (calmo) — il corpo esprime bassa energia cinetica. "
        "Assegna A− se sono presenti TUTTI i seguenti:\n"
        "  · gesti comunicativi rari (≤1 ogni 5s) o mani prevalentemente "
        "ferme\n"
        "  · movimenti fluidi e lenti\n"
        "  · ≤1 cambio di espressione marcato ogni 5s\n"
        "  · busto stabile\n"
        "  · nessuna mimica caricaturale\n\n"

        "Se né A+ né A− sono chiaramente soddisfatti, scegli quello "
        "più vicino ai marker osservati.\n\n"

        # ── PASSO 3 — COMBINAZIONE ─────────────────────────────────────
        "═══ PASSO 3 · COMBINA GLI ASSI ═══\n"
        "  D+  ×  A+  →  'charismatic_performer'\n"
        "  D+  ×  A−  →  'authoritative_expert'\n"
        "  D−  ×  A+  →  'soft_engager'\n"
        "  D−  ×  A−  →  'intimate_confidant'\n\n"

        "Esempi di riferimento (sintetici):\n"
        "• charismatic_performer: entertainer con gesti ampi e rapidi, "
        "alta energia e presenza scenica; skit teatrale con mimica "
        "esagerata.\n"
        "• authoritative_expert: divulgatore con postura aperta e stabile, "
        "gesti ampi ma lenti e controllati, padronanza scenica calma.\n"
        "• soft_engager: creator con gesti frequenti ma nella zona "
        "contenuta, mimica viva, energia alta ma 'vicina al corpo'.\n"
        "• intimate_confidant: creator in primo piano con gesti rari e "
        "lenti, postura raccolta, mimica sottile, ritmo calmo.\n\n"

        # ── NOTE ANTI-BIAS ─────────────────────────────────────────────
        "═══ NOTE ANTI-BIAS ═══\n"
        "• Le due dimensioni sono INDIPENDENTI: non lasciare che la "
        "valutazione di D influenzi quella di A o viceversa.\n"
        "• 'intimate_confidant' richiede marker espliciti sia di D− sia "
        "di A−. NON è un default per video 'tranquilli'.\n"
        "• NON assegnare 'intimate_confidant' a sketch recitati: la "
        "regola teatrale li rende D+.\n"
        "• Gesti funzionali ampi: valuta caso per caso. Ampi + showmanship "
        "= D+. Ampi + necessità pratica = ignora per D.\n\n"

        "Esegui i passi 0 → 0b → 1 → 2 → 3 nell'ordine indicato."
    )
)
    activity_video: Literal[
        "solo parlato",
        "parlato con attività",
        "solo attività",
        "né parlato né attività"
    ] = Field(
        description=("""    
        Estrai dal VIDEO. indica cosa sta facendo il creator nel video. La musica di sottofondo e le scritte 
        a schermo non costituiscono parlato e non vanno considerate ai fini di questa variabile.
        Scegli UNA delle seguenti categorie:

        - "solo parlato": il creator è fermo o quasi fermo e dedica la propria attenzione completamente 
        al pubblico. Non sta svolgendo nessuna attività rilevante in parallelo. La comunicazione con 
        lo spettatore è l'unica azione in corso.
        Esempi: creator seduto o in piedi che racconta qualcosa guardando in camera, creator che 
        parla direttamente al telefono senza fare altro, intervista frontale.

        - "parlato con attività": il creator parla al pubblico mentre svolge simultaneamente un'altra 
        attività fisica, pratica o performativa. L'attività può essere correlata o non correlata 
        al tema del video.
        Esempi: creator che si trucca mentre sponsorizza prodotti beauty, creator che corre o 
        cammina mentre racconta un aneddoto, creator che cucina mentre parla della ricetta, 
        creator che balla mentre comunica qualcosa, creator che fa la spesa mentre commenta 
        i prodotti.

        - "solo attività": il creator svolge un'attività fisica o pratica senza parlare direttamente 
        al pubblico. Non c'è comunicazione verbale rivolta allo spettatore. La presenza di musica 
        o scritte a schermo non cambia questa classificazione in quanto non costituiscono parlato.
        Esempi: creator che balla senza commentare, video di una performance fisica senza parlato, 
        creator che cucina o si trucca senza rivolgersi alla camera, contenuto basato su musica 
        e azione senza voce.

        - "né parlato né attività": il creator è presente ma non parla e non svolge alcuna attività 
        specifica. La presenza di musica o scritte a schermo non cambia questa classificazione 
        in quanto non costituiscono parlato.
        Esempi: creator ripreso in momenti passivi o candidi, video basato solo su musica e testo 
        a schermo senza azione del creator, creator presente ma non protagonista di alcuna azione.
        """)
    )

    format_video: Literal[
        "tutorial",
        "basic placement",
        "brand-related experience/event",
        "slice of life",
        "product review"
    ] = Field(
        description=("""    
        Estrai dal VIDEO.  il formato narrativo del contenuto video, ovvero la logica strutturale che guida 
        il video. Non valutare il tema trattato, ma come il prodotto viene contestualizzato 
        e cosa determina la struttura del video. Se il video combina più formati, scegli quello 
        dominante per la maggior parte della durata.
        Scegli UNA delle seguenti categorie:

        - "tutorial": il video è strutturato come una sequenza istruttiva. C'è un obiettivo 
        da raggiungere e i passaggi per raggiungerlo sono mostrati o spiegati esplicitamente 
        nel video nell'ordine in cui vanno eseguiti.
        Esempi: ricetta mostrata passo per passo, guida all'uso di un prodotto con dimostrazione 
        pratica, routine mostrata nell'ordine corretto di esecuzione.
        ATTENZIONE: i passaggi devono essere nel video, non nella caption. Se il creator mostra 
        solo il risultato finale rimandando le istruzioni alla descrizione, non è tutorial.

        - "basic placement": il video è costruito attorno alla presentazione del prodotto. 
        Il creator lo mostra e ne parla, ma esclusivamente in modo descrittivo o promozionale. 
        Non c'è nessuna esperienza personale d'uso: il creator non ha necessariamente usato 
        il prodotto e non dice se funziona o meno basandosi su un'esperienza diretta. 
        Parla del prodotto come se stesse leggendo una scheda tecnica o presentando una novità.
        Esempi: creator che spiega le caratteristiche di un prodotto senza dire di averlo usato, 
        presentazione di una collezione con descrizione delle caratteristiche, video in cui 
        il creator illustra cosa fa un prodotto o servizio in modo puramente informativo 
        senza portare nessun giudizio personale basato sull'uso.

        - "brand-related experience/event": il video documenta un evento o un'esperienza 
        organizzata o resa possibile dal brand. Il brand ha creato la situazione che il 
        creator sta vivendo e documentando. Il prodotto viene presentato attraverso 
        quell'evento o esperienza.
        Esempi: party organizzato da un brand, hub esperienziale in piazza, brand trip, 
        press day, lancio prodotto con evento fisico, serata organizzata da un brand.

        - "slice of life": il video racconta una storia personale del creator dentro cui 
        il prodotto è presente. La storia è più grande del prodotto: esiste una narrazione 
        personale che andrebbe avanti anche senza di esso. Il prodotto appare come elemento 
        di quella storia, non come protagonista.
        A differenza di product review, in slice of life se togli il prodotto dal video rimane 
        una storia raccontabile.
        Esempi: creator che racconta la propria giornata stressante in cui ha usato un prodotto, 
        situazioni comiche della vita quotidiana con il prodotto integrato, contenuti family 
        o di coppia, weekend raccontato in prima persona con il brand come parte dell'esperienza.

        - "product review": il video è costruito interamente attorno all'esperienza personale 
        diretta del creator con quel prodotto. Il creator lo ha usato, lo dice esplicitamente, 
        e dà un verdetto chiaro basato su quell'uso: funziona o non funziona, lo consiglia 
        o non lo consiglia. Non c'è storia più ampia né pura presentazione: c'è solo 
        il creator che dice come è andata con quel prodotto.
        A differenza di slice of life, in product review se togli il prodotto dal video non 
        rimane nulla da raccontare.
        Esempi: creator che dice esplicitamente di aver usato un prodotto e dà il proprio 
        verdetto, racconto diretto dell'esperienza d'uso con una conclusione netta, 
        creator che confronta prima e dopo l'uso esprimendo un giudizio esplicito.
        """)
    )

    product_integration: Literal[
        "in uso",
        "in presentazione",
        "in scena",
        "assente"
    ] = Field(
        description=("""    
        Estrai dal VIDEO. è la modalità con cui il prodotto o servizio brandizzato è presente 
        nel contenuto video. Valuta esclusivamente ciò che appare o viene detto nel video, 
        non il testo della caption. Scegli UNA delle seguenti categorie basandoti su un unico 
        criterio: cosa fa il creator con il prodotto o servizio.

        - "in uso": il prodotto è fisicamente presente sul corpo del creator, nelle sue mani 
        o viene consumato nel corso del video. Questa categoria ha priorità su "in presentazione": 
        se il creator indossa, tiene, usa o consuma il prodotto, è sempre "in uso" anche se 
        contemporaneamente lo descrive, lo mostra alla camera o ne parla direttamente.
        Esempi: creator che indossa occhiali mentre li presenta alla camera, che cucina con 
        un ingrediente mentre ne spiega le qualità, che beve un prodotto mentre lo commenta, 
        che tiene in mano un packaging mentre lo descrive.

        - "in presentazione": il creator parla del prodotto o servizio rivolgendosi direttamente 
        alla camera, lo mostra, lo descrive o lo promuove. La comunicazione è rivolta al 
        prodotto stesso: è lui il soggetto del discorso in quel momento.
        Esempi: creator che guarda in camera e spiega le caratteristiche di un prodotto, 
        che mostra il packaging in primo piano mentre ne parla, che descrive un servizio 
        e invita a provarlo, che interrompe la narrazione per presentare un'offerta.

        - "in scena": il prodotto è visibile nell'inquadratura ma il creator non lo usa 
        e non ne parla. È presente come elemento scenografico o di sfondo, riconoscibile 
        ma non protagonista.
        Esempi: packaging sul tavolo mentre il creator parla d'altro, prodotto sullo sfondo 
        senza essere toccato o citato, oggetto nell'inquadratura che non entra mai nell'azione.

        - "assente": nel video non è visibile alcun prodotto o brand e il creator non fa 
        riferimento verbale ad alcun prodotto o servizio specifico.
        Esempi: creator che parla o svolge un'attività senza che nessun prodotto appaia 
        nell'inquadratura e senza citarne alcuno.
        """)
    )

    funnel: Literal[
        "awareness",
        "consideration",
        "conversion"
    ] = Field(
        description=("""
        Estrai dal VIDEO. è l'intenzione commerciale del contenuto, ovvero cosa vuole ottenere dal pubblico 
        in termini di risposta. Non valutare il formato né come appare il prodotto, ma quale 
        azione o stato mentale il contenuto sta cercando di generare nello spettatore.
        Scegli UNA delle seguenti categorie:

        - "awareness": il contenuto vuole che il pubblico sappia che il brand o prodotto esiste. 
        Non c'è nessuna spinta a fare qualcosa, nessun invito all'azione, nessuna urgenza. 
        Il prodotto è presente ma l'obiettivo si esaurisce nel far conoscere il brand.
        Esempi: brand o prodotto mostrato o citato senza nessun invito esplicito o implicito 
        ad acquistare, contenuto in cui il prodotto appare naturalmente senza che il creator 
        spinga il pubblico verso nessuna azione specifica.

        - "consideration": il contenuto vuole generare desiderio o interesse verso il prodotto. 
        Mostra benefici, racconta un'esperienza positiva, crea aspirazione. Il pubblico 
        dovrebbe volerlo o considerarlo, ma non c'è urgenza né invito diretto ad agire ora. 
        Questa categoria si applica solo se nel video non è presente nessuna call to action 
        esplicita né nessun incentivo concreto all'azione.
        Esempi: creator che racconta i benefici di un prodotto usato, contenuto che mostra 
        il prodotto in modo desiderabile senza spingere all'acquisto immediato, esperienza 
        positiva raccontata che genera interesse senza call to action.

        - "conversion": il contenuto vuole che il pubblico faccia qualcosa di specifico e 
        immediato. Questa categoria ha priorità su consideration: se nel video è presente 
        anche solo un elemento di call to action, classificare sempre come conversion 
        indipendentemente dal resto del contenuto.
        Esempi: link in bio, codice sconto, offerta a tempo limitato, invito diretto 
        all'acquisto o all'iscrizione, promozione con date o condizioni specifiche.
        """)
    )
    posizionamento: Literal[
        "accessibile",
        "premium",
        "lusso",
        "non identificabile"
    ] = Field(
        description=("""
        Estrai dal VIDEO.  la fascia di prezzo del brand o prodotto citato o mostrato nel video.
        Il tuo processo deve essere esattamente questo:
        1. Identifica il nome del brand o del prodotto dal video, che venga detto verbalmente, 
        mostrato nel packaging, o citato in altro modo.
        2. Usa la tua conoscenza del brand per classificarlo nella fascia corretta.
        Ignora completamente tutto il resto: l'estetica del video, il contesto della scena, 
        il tono del creator, l'ambiente in cui si trova il prodotto. Questi elementi non devono 
        influenzare la classificazione in nessun caso.
        Scegli UNA delle seguenti categorie:

        - "accessibile": il brand è noto per un posizionamento di prezzo basso o mainstream, 
        destinato a un pubblico ampio.
        Esempi: discount alimentari, fast fashion a basso costo, brand della grande distribuzione, 
        prodotti di cura persona da supermercato, brand sportivi mainstream.

        - "premium": il brand è noto per un posizionamento medio-alto, con prezzi superiori alla 
        media della sua categoria ma non esclusivi.
        Esempi: brand cosmetici di fascia alta, abbigliamento sportivo tecnico di qualità, 
        ristoranti o hotel sopra la media, elettronica di consumo di fascia alta.

        - "lusso": il brand è noto per un posizionamento esclusivo, con prezzi alti per definizione 
        e non destinato a un pubblico di massa.
        Esempi: brand della moda di alta gamma, gioielleria, auto di lusso, hotel o esperienze 
        di fascia esclusiva.

        - "non identificabile": non è stato possibile identificare il nome del brand o del prodotto 
        dal video, rendendo impossibile qualsiasi classificazione.
        Esempi: video in cui nessun brand viene nominato né mostrato, prodotto generico senza 
        identità di brand riconoscibile.
        """)
    )


SYSTEM_PROMPT = system_prompt
