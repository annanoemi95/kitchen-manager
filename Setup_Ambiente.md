# Kitchen Manager

## 🚀 Configurazione Rapida Ambiente (Backend)

Questo documento spiega come configurare o resettare velocemente l'ambiente di sviluppo locale per il progetto Kitchen Manager.

### 1. Cosa fare (Esecuzione)

Ogni volta che cloni il progetto da zero, elimini il database (`db.sqlite3`) o hai bisogno di riallineare i dati, esegui questo comando dal terminale nella cartella `backend/`:

```
./setup_dev.sh
```

### 🍎 Nota per utenti Mac
Se ricevi un errore di "permessi negati" (Permission denied), dai i permessi di esecuzione allo script una sola volta con:

```
chmod +x setup_dev.sh
```

### 2. Cosa fa lo script?
Per garantire che tutto il team lavori con gli stessi standard, lo script esegue automaticamente:

1. **Migrazioni**: Allinea le tabelle del database all'ultima versione.
2. **Seed Admin**: Crea (o aggiorna) un account amministratore con permessi completi e ruolo di business `admin`.

### 3. Credenziali di Accesso Admin
D'ora in poi, per i test nel pannello di amministrazione (`/admin/`), usa sempre queste credenziali:

1. **Username**: `admin`
2. **Password**: `admin123`

### 4. Perché usare questo comando?
- **Velocità**: Non devi usare `createsuperuser` manualmente ogni volta.
- **Coerenza**: Assicura che l'utente admin abbia già il campo `role="admin"` necessario per le logiche del nostro progetto.
- **Pattern Observer**: Permette di testare immediatamente i segnali (Signals) del backend e i vincoli sulle recensioni usando un utente con pieni poteri.