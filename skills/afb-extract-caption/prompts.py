# AUTO-EXTRACTED VERBATIM from the original notebook — do not hand-edit.
from typing import Literal  # noqa
from pydantic import BaseModel, Field  # noqa

system_prompt_caption = """
=== RUOLO ===
Sei un esperto analista di marketing nel campo dei social media, con vasta esperienza nell'analisi 
di tutti i tipi di dati social. Sei un professionista molto orientato ai dati, capace di identificare 
informazioni rilevanti da post, descrizioni e diversi tipi di dati di marketing e social media.

=== CONTESTO ===
Aiuterai un gruppo di studenti in un progetto di data science focalizzato sull'analisi di dati social 
media e su cosa influenza l'engagement. La maggior parte delle feature di questo dataset sono non 
strutturate, il che significa che non possono essere facilmente utilizzate in un modello statistico 
tradizionale. Diventa quindi fondamentale estrarre feature strutturate e significative da quelle non strutturate.

=== TASK ===
Ti verrà fornita la caption di un post Instagram o TikTok unita al nome del brand che sponsorizza ufficialmente. Il tuo obiettivo è estrarre esattamente 
le seguenti variabili dalla caption, seguendo attentamente le descrizioni e le categorie fornite per ciascuna. 

=== VARIABILI DA ESTRARRE ===

tone_caption: Estrai dalla CAPTION. è la valenza emotiva e il registro affettivo percepito nel testo della caption
Non è il tono strategico del brand, ma come il testo ti fa sentire leggendolo. Se il testo presenta più toni, scegli 
quello predominante, ma dando leggermente più peso all'ultima frasedel testo della caption che potrebbe cambiare il 
significato e quindi la valenza emotiva dell'intero testo.

---

funnel_caption: Estrai dalla CAPTION. è l'intenzione commerciale del testo della caption, ovvero cosa vuole ottenere dal pubblico
in termini di risposta. Non valutare il formato né come appare il prodotto, ma quale 
azione o stato mentale il testo della caption sta cercando di generare nello spettatore.

=== FORMATO DI OUTPUT ===
Rispondi SOLO con un oggetto JSON contenente tutte le variabili.
Nessuna spiegazione, nessun testo aggiuntivo.

=== LINEE GUIDA AGGIUNTIVE ===
Ragiona attentamente prima di rispondere.
Estrai il valore basandoti esclusivamente sulle descrizioni fornite.
In caso di ambiguità tra due categorie, scegli quella più coerente con il contenuto predominante della caption.
"""


class Features(BaseModel):    
    tone_caption: Literal[
        "entusiasta/energico",
        "ironico/scherzoso",
        "calmo/confidenziale",
        "logico/informativo",
        "neutro/assente"
    ] = Field(
        description=("""
        Estrai dalla CAPTION. è la valenza emotiva e il registro affettivo percepito nel testo della caption.
        Non è il tono strategico del brand, ma come il testo ti fa sentire leggendolo. Se il tetso presenta più toni, scegli 
        quello predominante, ma dando leggermente più peso all'ultima frasedel testo della caption che potrebbe cambiare il 
        significato e quindi la valenza emotiva dell'intero testo.Scegli UNA categoria:

        - "entusiasta/energico": il testo trasmette energia positiva e vivacità. Sono presenti 
        esclamazioni frequenti, maiuscole enfatiche, ritmo incalzante, aggettivi forti. Il registro 
        è ad alta intensità emotiva positiva, trasmette eccitazione e coinvolgimento.
        Esempi: "Ragazzi è PAZZESCO, non ci posso credere!!!", uso abbondante di punti esclamativi, 
        aggettivi come "incredibile", "assurdo", "pazzesco", frasi brevi e energiche che si 
        susseguono rapidamente.

        - "ironico/scherzoso": il testo usa umorismo, autoironia, situazioni assurde o paradossali, 
        battute, doppi sensi come registro comunicativo principale. Il tono è leggero e non si 
        prende sul serio, usando la comicità come leva per coinvolgere il lettore e rendere 
        il messaggio promozionale più naturale e accessibile, spesso usa emonji, termini inusuali/paradossali
        sempre però allo scopo di coinvolgere umoristicamente e non per comunicare entusiasmo/eccitazione.
        Esempi: caption con doppi sensi, battute sulla vita quotidiana, tono canzonatorio, 
        situazioni volutamente assurde raccontate con leggerezza, humor sul rapporto di coppia 
        o coi coinquilini, emonji della risata.

        - "calmo/confidenziale": il testo ha un registro intimo e conversazionale, come se il creator 
        stesse scrivendo a un amico. Il ritmo è pacato, le frasi sono fluenti e naturali, senza 
        picchi di energia né distanza formale.
        Esempi: testo che inizia con "Vi racconto una cosa…", scrittura informale e diretta, 
        tono da chiacchierata, frasi riflessive e personali senza enfasi eccessiva.

        - "logico/informativo": il testo è deciso, strutturato e competente. Il registro è 
        quello di chi sa di cosa parla e lo comunica con chiarezza. Poche inflessioni emotive, 
        linguaggio preciso e ordinato.
        Esempi: testo con elenchi di informazioni, frasi costruite con logica sequenziale, 
        linguaggio tecnico o specifico del settore, tono da esperto che spiega senza coinvolgimento 
        emotivo marcato.

        - "neutro/assente": il testo è piatto e privo di carica emotiva dominante. Fornisce dati, 
        comunica un'offerta, annuncia date o luoghi, descrive prodotti senza narrativa emotiva.
        Esempi: annunci con orari e location, promozioni con date e prezzi, caption brevissime 
        con solo tag e hashtag, descrizioni di prodotto senza registro personale.
        """)
    )
    funnel_caption: Literal[
        "awareness",
        "consideration",
        "conversion"
    ] = Field(
        description=("""
        Estrai dalla CAPTION, considera il noime del brand ufficialmente sponsorizzato. è l'intenzione commerciale del testo della caption, ovvero cosa vuole ottenere dal pubblico
        in termini di risposta. Non valutare il formato né come appare il prodotto, ma quale 
        azione o stato mentale il tetso della caption sta cercando di generare nello spettatore.

        - "awareness": il contenuto rende visibile il brand o il prodotto senza svilupparne
        un'argomentazione di vendita. Il brand è menzionato, taggato o presente come elemento
        di scena, ma il testo della caption non spiega perché il pubblico dovrebbe volerlo:
        non ci sono benefit articolati, testimonianze d'uso, raccomandazioni motivate, né
        call to action. Rientrano qui i casi in cui la caption è costruita come comedy, meme,
        metafora, storytelling, avventura o lifestyle e il brand compare solo come tag, hashtag
        o micro-frase descrittiva (anche con hashtag-payoff slogan tipo #BrandRicaricaNoStress
        o #LaDolcezzaCheTiMeriti, finché la caption non ne sviluppa il contenuto). Il
        coinvolgimento del lettore con il contenuto creativo non equivale a intenzione
        commerciale sul prodotto. In dubbio tra awareness e consideration, scegliere awareness.
        Esempi: metafora poetica con brand solo nei tag ("L'amicizia è vedere il mondo
        attraverso lenti diverse... @prada #adv"), comedy con product placement narrativo
        ("Mentre aspetto mi faccio la fibra di @iliaditalia"), meme con hashtag-payoff
        ("Stress per la vacanza > stress da rientro #SupradynRicaricaNoStress").

        - "consideration": il contenuto argomenta esplicitamente perché il prodotto/brand
        merita l'interesse del pubblico. Richiede almeno un argomento di vendita sviluppato
        nel testo: un claim di beneficio articolato (es. "idrata la pelle", "dura tutto il
        giorno", "il kit giusto"), una testimonianza d'uso o recensione ("io lo uso da mesi",
        "ve lo consiglio"), un confronto/posizionamento, la descrizione di caratteristiche
        che giustificano l'acquisto, oppure una raccomandazione esplicita o implicita ma
        motivata (es. un imperativo come "sceglietelo" abbinato al tag del brand specifico).
        Non basta che il prodotto appaia in un contesto positivo, aspirazionale o di lifestyle:
        deve esserci un'argomentazione riconoscibile. Questa categoria si applica solo se
        nella caption non è presente nessuna call to action esplicita né nessun incentivo
        concreto all'azione.
        Esempi: creator che racconta i benefici di un prodotto usato ("da quando uso questo
        siero la pelle è più luminosa, ve lo consiglio"), micro-claim implicito + storytelling
        di prodotto in uso ("alla vetta in 2 ore con il kit giusto firmato Quechua"),
        imperativo + tag che funziona da raccomandazione del brand specifico ("Sceglieteli
        bene. @emporioarmani").

        - "conversion": il contenuto vuole che il pubblico faccia qualcosa di specifico e 
        immediato. Questa categoria ha priorità su consideration: se nella caption è presente 
        anche solo un elemento di call to action, classificare sempre come conversion 
        indipendentemente dal resto del contenuto.
        Esempi: link in bio o link nella caption, codice sconto, offerta a tempo limitato, invito diretto 
        all'acquisto o all'iscrizione, promozione con date o condizioni specifiche, espressioni
        che suggeriscono un'azione come 'basta andare/provare/comprare' riferite al prodotto o al brand.
        """)
    )


SYSTEM_PROMPT = system_prompt_caption
