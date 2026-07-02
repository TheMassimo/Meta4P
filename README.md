# Meta4P - MetaProteins-Peptides-PSMs Parser

![Meta4P](M4P_icon.png)

## 📋 Descrizione

**Meta4P** è un'applicazione bioinformatica intuitiva e user-friendly progettata per integrare dati metaproteomici quantitativi *label-free* con annotazioni tassonomiche e funzionali.

L'applicazione consente di:
- **Recuperare, filtrare e processare** dati di identificazione e quantificazione da tre tipi di input:
  - Proteine
  - Peptidi
  - PSMs (Peptide Spectrum Matches)

- **Combinare** dati di abbondanza con informazioni tassonomiche e funzionali
- **Aggregare** i dati a diversi livelli personalizzabili:
  - Taxa
  - Funzioni
  - Pathways
  - Funzioni specifiche per taxa

- **Esportare** i risultati in diversi formati pronti per analisi statistiche downstream

---

## ✨ Caratteristiche

- ✅ Interfaccia grafica intuitiva (GUI tkinter)
- ✅ Supporto per molteplici formati di input (EXCEL, TXT, file delimitati)
- ✅ Normalizzazione flessibile dei dati
- ✅ Supporto per diverse metriche di quantificazione (Spectral Count, Intensity, MaxLFQ)
- ✅ Esportazione in molteplici formati
- ✅ Multi-threading per elaborazioni complesse
- ✅ Compatibilità Windows e MacOS
- ✅ Processamento di abbondanza proteica con filtri personalizzabili

---

## 🏗️ DIAGRAMMI ARCHITETTURALI

Meta4P dispone di una documentazione architetturale **completa in formato Mermaid** che rappresenta ogni aspetto del sistema:

### 📊 Diagrammi Disponibili:
1. **Architettura generale** - Componenti principali e flusso tra layer
2. **Diagramma delle classi** - Relazioni tra finestre GUI e moduli
3. **Flusso principale** - Percorso completo di un'analisi end-to-end
4. **Sequenza di esecuzione** - Interazione tra componenti nel tempo
5. **Diagramma di stato** - Stati dell'applicazione e transizioni
6. **Dipendenze moduli** - Come i moduli si collegano tra loro
7. **Architettura C4** - Visione multi-livello del sistema
8. **Attività di processamento** - Elaborazione dati passo per passo
9. **Timeline GANTT** - Fasi temporali di elaborazione
10. **Deployment** - Ambiente di sviluppo, build e produzione
11. **Struttura dati** - Flusso informativo e relazioni entità
12. **Gerarchia GUI** - Struttura navigazione interfaccia
13. **Aggregazione dati** - Processamento specializzato per tipo analisi

> 💡 **Visualizzazione**: I diagrammi sono in formato **Mermaid** e visualizzabili su **GitHub** (automaticamente), **VSCode** (con estensione), o esportabili in SVG/PNG

**📖 [Vedi tutti i diagrammi architetturali completi](ARCHITECTURE_DIAGRAMS.md)**

---

## 🖥️ Requisiti di Sistema

- **Python** 3.7+
- **tkinter** (incluso in Python)
- Pacchetti Python aggiuntivi (vedi `requirements.txt`)
- **Windows** o **MacOS**

---

## 📥 Installazione

### Opzione 1: Eseguibile pre-compilato (Consigliato)

Scarica l'ultima versione compilata dell'applicazione:

**[📦 Scarica Meta4P.exe](https://github.com/TheMassimo/Meta4P/releases)**

Estrai l'archivio e avvia `Meta4P.exe`.

### Opzione 2: Esecuzione da sorgente Python

#### Passo 1: Clona il repository
```bash
git clone https://github.com/TheMassimo/Meta4P.git
cd Meta4P
```

#### Passo 2: Crea ambiente virtuale
```bash
python -m venv env
```

#### Passo 3: Attiva l'ambiente
- **Windows**: 
  ```bash
  env\Scripts\activate
  ```
- **MacOS/Linux**: 
  ```bash
  source env/bin/activate
  ```

#### Passo 4: Installa dipendenze
```bash
pip install -r requirements.txt
```

#### Passo 5: Avvia l'applicazione
```bash
python main.py
```

---

## 🚀 Utilizzo Rapido

1. **Avvia** Meta4P
2. **Seleziona il tipo di input**: Proteine, Peptidi o PSMs
3. **Carica il file** di dati (EXCEL, TXT, o file delimitati)
4. **Configura i parametri**:
   - Tipo di quantificazione
   - Normalizzazione (based on total abundance before/after filtering)
   - Filtri personalizzati
5. **Seleziona il livello di aggregazione**: Tassonomico, Funzionale, Composti Organici
6. **Esegui l'elaborazione**
7. **Esporta i risultati** nel formato desiderato

---

## 📁 Struttura del Progetto

```
Meta4P/
├── main.py                              # Punto di ingresso principale
├── config.py                            # Configurazioni globali (font, formati, ecc.)
├── COG_name.py                          # Gestione nomi COG
├── MyUtility.py                         # Funzioni utility generiche
├── MyMultiThreading.py                  # Gestione multi-threading
│
├── 🪟 INTERFACCIA PRINCIPALE
├── WindowMenu.py                        # Finestra principale del menu
├── WindowLoading.py                     # Finestra di caricamento/progress
├── WindowInputType.py                   # Selezione tipo di input
├── WindowInformationLevel.py            # Livello di informazione
│
├── 🪟 ELABORAZIONE DATI
├── WindowAggregation.py                 # Configurazione aggregazione
├── WindowNameExtension.py               # Gestione estensioni nomi
├── WindowRenameColumns.py               # Rinominazione colonne
│
├── 🪟 ANALISI TASSONOMICA
├── WindowTaxonomicMenu.py               # Menu tassonomico
├── WindowDynamicTaxonomic.py            # Analisi dinamica tassonomica
├── WindowStandardTaxonomic.py           # Analisi standard tassonomica
│
├── 🪟 ANALISI FUNZIONALE
├── WindowFunctionalMenu.py              # Menu funzionale
├── WindowDynamicFunctional.py           # Analisi dinamica funzionale
├── WindowStandardFunctional.py          # Analisi standard funzionale
│
├── 🪟 ANALISI COMPOSTI ORGANICI
├── WindowDynamicOrganicCompounds.py     # Analisi composti organici dinamici
├── WindowStandardOrganicCompounds.py    # Analisi composti organici standard
│
├── 📊 METRICHE E SINTESI
├── WindowSummaryMetricsPre.py           # Metriche di sintesi (pre-filtering)
├── WindowSummaryMetricsPost.py          # Metriche di sintesi (post-filtering)
│
├── 🔧 BUILD E CONFIGURAZIONE
├── main.spec                            # Configurazione PyInstaller (python)
├── Meta4P.exe.spec                      # Spec per eseguibile Windows
├── Meta4P.pyproj                        # Progetto Visual Studio
├── requirements.txt                     # Dipendenze Python
│
├── build/                               # Cartella build
└── README.md                            # Questo file
```

---

## 📤 Formati di Input Supportati

| Formato | Estensione |
|---------|-----------|
| Microsoft Excel | `.xlsx` |
| Testo | `.txt` |
| File delimitati da tabulazioni | `.*` (generico) |

---

## 📊 Metriche di Quantificazione Supportate

### FragPipe Quantitative
- Spectral Count
- Unique Spectral Count
- Total Spectral Count
- Intensity
- Unique Intensity
- Total Intensity
- MaxLFQ Intensity
- Unique MaxLFQ Intensity
- Total MaxLFQ Intensity

---

## 🔨 Compilazione dell'Eseguibile

Per creare un eseguibile standalone per Windows:

```bash
# Installa PyInstaller se non presente
pip install pyinstaller

# Compila l'eseguibile usando il file spec
pyinstaller main.spec
```

L'eseguibile compilato sarà disponibile in `build/dist/Meta4P.exe`

Per distribuire:
```bash
# Copia l'eseguibile e l'icona nella cartella build
cp M4P_icon.png build/dist/
```

---

## 👨‍💻 Sviluppo

### Struttura del Codice

L'applicazione utilizza:
- **tkinter**: Per l'interfaccia grafica
- **Threading**: Per operazioni non-bloccanti
- **PyInstaller**: Per la compilazione in eseguibile

### Pattern di Finestre

Ogni finestra GUI è implementata in un file separato (`Window*.py`) per:
- Migliore modularità
- Facilità di manutenzione
- Riutilizzabilità del codice

### Aggiungere una Nuova Finestra

1. Crea un nuovo file `WindowNuovoFeature.py`
2. Importalo in `WindowMenu.py`
3. Aggiungi il pulsante/menu per accedervi

---

## 📝 Configurazione Globale

Le configurazioni globali sono gestite in [config.py](config.py):

- **Icona**: `M4P_icon.png`
- **Font**: Calibri (vari stili e dimensioni)
- **Formati file**: EXCEL, TXT, generici
- **Metriche di normalizzazione**: Pre/post-filtering
- **Metriche di quantificazione**: Tutte le varianti

---

## 🐛 Bug Report e Contributi

Segnala problemi e suggerimenti su:
📧 **[GitHub Issues](https://github.com/TheMassimo/Meta4P/issues)**

Se desideri contribuire:
1. Fork il repository
2. Crea un branch per la tua feature: `git checkout -b feature/AmazingFeature`
3. Commit i cambiamenti: `git commit -m 'Add some AmazingFeature'`
4. Push al branch: `git push origin feature/AmazingFeature`
5. Apri una Pull Request

---

## 📜 Licenza

[Inserire informazioni sulla licenza - es. MIT, GPL, ecc.]

---

## 👨‍⚖️ Autori

- **Massimo** ([@TheMassimo](https://github.com/TheMassimo))
- **Luca** ([@lvannucci-jpg](https://github.com/lvannucci-jpg))

---

## 📚 Riferimenti

- **Repository**: [GitHub - Meta4P](https://github.com/TheMassimo/Meta4P)
- **Releases**: [GitHub Releases](https://github.com/TheMassimo/Meta4P/releases)
- **Python**: [python.org](https://www.python.org)
- **tkinter**: [docs.python.org/tkinter](https://docs.python.org/3/library/tkinter.html)
- **PyInstaller**: [pyinstaller.org](https://www.pyinstaller.org)

---

## 📋 Changelog

Per visualizzare le novità e gli aggiornamenti di ogni versione, consulta:
🔗 **[Release Notes](https://github.com/TheMassimo/Meta4P/releases)**

---

**Versione**: Vedi ultime release  
**Ultima modifica**: Aprile 2026  
**Piattaforme supportate**: Windows, MacOS  

For Windows and MacOS

Download last version at:
https://github.com/TheMassimo/Meta4P/releases
