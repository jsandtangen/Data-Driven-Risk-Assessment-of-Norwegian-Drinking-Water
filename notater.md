spørmsål 1 (24.09):

Kan vi predikere om et vannverk har minst ett avvik i et gitt år ut fra størrelse, vannbehandling, eierform og vannkilde?

Basert på `vannverk_final.csv`-strukturen vi laget:

**Fokuser på disse (features):**

*Kjernevariabler for anleggsstørrelse/omfang:*
- `vannprod` — vannproduksjon
- `ant_fastboende`, `ant_hytter`, `ant_husstander` — hvor mange anlegget forsyner

*Rensemetoder (sannsynligvis de mest interessante forklaringsvariablene):*
- `uv`, `klorering`, `koagulering`, `membranfiltrering`, `siling`, `lufting`, `ph_justering`, `antall_anlegg`
- `rensedata_rapportert` — bruk denne sammen med rensemetodene, ikke i stedet for dem

*Kontekst/kategori:*
- `orgform` — organisasjonsform (nå ryddet med "ANNET"-samlekategori)
- `boliger`, `helseinst`, `skoler`, `hyttercamp`, `gardsbruk` — hva slags bygg/virksomhet anlegget forsyner
- `beredsk_oppd`, `beredsk_ovelse` — beredskap
- `aktiv` — er anlegget aktivt

*Gråsone, kan inkluderes med forbehold:*
- `total_analyser` — grei å ha med, men husk at store anlegg naturlig får flere analyser og dermed statistisk sett høyere sjanse for minst ett avvik. Nevn dette som en confounder i rapporten hvis du bruker den.

**Se bort fra som features (bruk kun `avvik` som target):**
- `total_avvik`, `avvik_rate`, `koli_avvik`, `ecoli_avvik`, `enterok_avvik`, `bakterie_avvik` — alle er direkte avledet av target, gir datalekkasje
- `mtid_vf`, `navn` — identifikatorer, ingen prediktiv verdi (men `mtid_vf` trenger du for gruppebasert train/test-splitt)
- `kommune` — kan vurderes, men med over 400 unike verdier gir den enten veldig mange dummy-kolonner eller må grupperes (f.eks. til fylke) for å være nyttig
- `periode` — vurder om den skal være med som feature eller holdes utenfor og heller brukes til å dele opp tidsperioder

Vil du at jeg skriver koden som setter opp `X` og `y` konkret, med disse valgene innbakt?