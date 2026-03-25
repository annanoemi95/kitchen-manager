# Kitchen Manager

Questo documento raccoglie i passaggi minimi per configurare l'ambiente locale del progetto, sia lato backend sia lato frontend.     

## Setup iniziale del progetto

### 1. Clonare il repository

Apri il terminale nella cartella in cui vuoi salvare il progetto ed esegui:

```bash
git clone <URL_DEL_REPOSITORY>
cd kitchen-manager
```

Sostituisci `<URL_DEL_REPOSITORY>` con il link Git del repository condiviso su GitHub.

### 2. Creare il virtual environment

Dalla root del progetto crea un virtual environment locale:

```bash
python3 -m venv .venv
```

Per attivarlo:

```bash
source .venv/bin/activate
```

Se tutto e andato bene, nel terminale vedrai comparire il prefisso `(.venv)`.

### 3. Installare le dipendenze backend

Con il virtual environment attivo, installa i pacchetti Python richiesti dal progetto:

```bash
pip install -r backend/requirements.txt
```

Se vuoi verificare che `pip` stia usando davvero il virtual environment appena creato, puoi controllare con:

```bash
which python
which pip
```

## Backend

### 1. Setup rapido

Ogni volta che cloni il progetto da zero, elimini il database (`db.sqlite3`) o hai bisogno di riallineare i dati, esegui questo comando dal terminale nella cartella `backend/`:

```bash
./setup_dev.sh
```

Lo script usa automaticamente `../.venv/bin/python` se il virtualenv di progetto esiste; in alternativa ripiega su `python3`.

### 2. Nota per utenti Mac

Se ricevi un errore di "permessi negati" (`Permission denied`), dai i permessi di esecuzione allo script una sola volta con:

```bash
chmod +x setup_dev.sh
```

### 3. Cosa fa lo script

Per garantire che tutto il team lavori con gli stessi standard, lo script esegue automaticamente queste fasi:

1. **Migrazioni**: allinea le tabelle del database all'ultima versione.
2. **Seed Admin**: crea o aggiorna l'account amministratore `admin` / `admin123`.
3. **Seed Menu**: genera categorie e piatti di test, inclusi casi limite per la UX.
4. **Seed Orders**: genera ordini e recensioni di test per verificare il flow completo.

### 4. Credenziali admin

Per i test nel pannello di amministrazione usa sempre:

1. **Username**: `admin`
2. **Password**: `admin123`

### 5. Perché usare questo comando

- **Velocità**: configura database, utenti e dati seed in un solo passaggio.
- **Test Soft Delete**: il seed include piatti con `is_active=False` per verificare che restino nello storico ordini senza apparire nel menu pubblico.
- **Test Disponibilità**: include piatti con `is_available=False` per verificare la gestione dei prodotti "Sold Out" nel frontend.
- **Pattern Observer**: permette di testare immediatamente i signals usando dati reali e coerenti.
- **Flow completo**: prepara dati coerenti per testare login admin, ordini cliente, avanzamento stato e recensioni.

### 6. Configurazione Gemini API Key

Per motivi di sicurezza e per evitare di consumare la quota gratuita condivisa, ogni persona deve usare la propria chiave Gemini in locale.

Puoi partire dal file di esempio:

```bash
cp backend/.env.example backend/.env
```

### Come impostarla in 1 minuto

1. Vai su Google AI Studio.
2. Clicca su Get API Key.
3. Apri il file `backend/.env` locale.
4. Inserisci questa riga:

```bash
GEMINI_API_KEY=tua_chiave_qui
```

5. Riavvia il server backend.
6. L'endpoint `GET /api/reviews/ai-summary/` sarà attivo.

**Verifica locale**

Dopo aver salvato tutto:

1. crea `backend/.env` a partire da `backend/.env.example`
2. inserisci la tua chiave personale
3. avvia il backend da `backend/`
4. testa l'endpoint oppure il bottone nella pagina admin recensioni

Esempio:

```bash
cd backend
../.venv/bin/python manage.py runserver
```

Il backend sarà disponibile su `http://127.0.0.1:8000/` e le API su `http://127.0.0.1:8000/api/`.

## Frontend

### 1. Installazione dipendenze

Dalla cartella `frontend/` esegui:

```bash
npm install
```

### 2. Configurazione ambiente frontend

Se vuoi esplicitare la configurazione locale, crea il file `frontend/.env`.

La variabile disponibile è:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Se il backend gira in locale sulla porta standard, questo valore va già bene così.

Esempio:

```bash
echo "VITE_API_BASE_URL=http://127.0.0.1:8000/api" > frontend/.env
```

### 3. Avvio frontend in sviluppo

Dalla cartella `frontend/`:

```bash
npm run dev
```

Vite avvierà il frontend locale e mostrerà nel terminale l'URL da aprire nel browser, di solito `http://localhost:5173/`.

### 4. Build di verifica

Per controllare che il frontend compili correttamente:

```bash
npm run build
```

### 5. Flow consigliato per lavorare in locale

1. Avvia il backend da `backend/`.
2. Avvia il frontend da `frontend/`.
3. Accedi come admin con `admin` / `admin123` oppure registrati come cliente.
4. Verifica il flow completo: menu, creazione ordine, avanzamento stato, recensione e area admin.
