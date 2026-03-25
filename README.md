# Kitchen Manager

Kitchen Manager è il progetto sviluppato dal team per la traccia "Sistema di Gestione per Ristorante / Dark Kitchen" della Dev, Cloud & Product Academy 2025/2026. L'obiettivo era realizzare in due settimane un prodotto presentabile con slide e demo live, composto da frontend, backend API e una funzionalità AI integrata nel flusso applicativo.

Il sistema centralizza menu, ordini e recensioni in un unico flusso digitale, riducendo il lavoro manuale su fogli di calcolo e chat e offrendo anche una sintesi AI dei feedback clienti.

## Contesto del progetto

### Brief generale

Il progetto nasce da un brief accademico in cui ogni team doveva:

- realizzare un prodotto software completo in due settimane
- presentarlo con slide finali e demo live
- costruire un frontend che dialogasse solo tramite API REST
- sviluppare il backend con Django e Django REST Framework
- integrare almeno un LLM in un endpoint del sistema
- documentare il progetto in repository

### Traccia assegnata

La traccia specifica richiedeva un sistema per una dark kitchen capace di:

- organizzare il menu
- ricevere e gestire ordini
- raccogliere recensioni
- fornire una funzionalita AI utile all'operativita

## Team

Il progetto e stato realizzato da:

- Chiara Branca
- Elisabetta Fino
- Anna Noemi Benincasa
- Serafina Marika di Bari
- Isabelle Adjetey

## Descrizione funzionale

### Problema

La dark kitchen cliente gestiva menu, ordini e recensioni con strumenti non centralizzati. Questo comportava:

- rischio di errori e duplicazioni
- scarsa tracciabilita del flusso operativo
- difficolta nel monitorare qualita del servizio e feedback

### Soluzione proposta

Kitchen Manager offre un flusso unico che copre:

- consultazione del menu
- autenticazione utente
- creazione ordine
- avanzamento stato ordine lato admin
- raccolta recensioni dopo la consegna
- analisi AI dei commenti dei clienti

### Target

- clienti finali che consultano il menu ed effettuano ordini
- amministratori o operatori che monitorano ordini, recensioni e insight

## Funzionalita implementate

### Lato cliente

- visualizzazione del menu pubblico
- filtro dei piatti per categoria nel frontend
- visualizzazione disponibilita dei piatti
- aggiunta piatti al carrello
- registrazione e login
- creazione ordine autenticato
- visualizzazione dello storico ordini
- inserimento recensione solo dopo consegna

### Lato admin

- visualizzazione di tutti gli ordini
- avanzamento dello stato ordine nel flusso `received -> preparing -> ready -> delivered`
- visualizzazione di tutte le recensioni
- generazione della sintesi AI delle recensioni

### Regole di business attualmente supportate

- i piatti inattivi non compaiono nel menu pubblico
- i piatti non disponibili risultano non ordinabili
- un ordine deve contenere almeno un piatto
- solo il proprietario dell'ordine puo recensirlo
- una recensione puo essere inserita solo quando l'ordine e `delivered`
- l'analisi AI e disponibile solo per admin e richiede almeno 3 recensioni

## Architettura tecnica

### Stack

- Frontend: React 19, TypeScript, Vite, React Router, Axios
- Backend: Django 6, Django REST Framework, Simple JWT
- Database di sviluppo: SQLite
- Provider AI: Google Gemini
- Versionamento: Git e GitHub

### Struttura del repository

```text
kitchen-manager/
|- backend/
|  |- config/
|  |- core/
|  |- menu/
|  |- manage.py
|  `- setup_dev.sh
|- frontend/
|  |- src/
|  |- public/
|  `- package.json
|- docs/
|  `- Setup_Ambiente.md
`- README.md
```

### Moduli principali

- `frontend/src/pages`: pagine principali del flusso utente e admin
- `frontend/src/api`: client API per auth, menu, ordini e recensioni
- `backend/core`: modelli, serializer, view e service layer usati dal flusso principale
- `backend/core/api/orders`: creazione ordine, dettaglio ordine e aggiornamento stato
- `backend/menu`: modulo legacy di supporto per la gestione menu

## Modello dati

| Entita | Campi principali | Relazioni |
| --- | --- | --- |
| `User` | `username`, `email`, `role` | un utente puo avere molti ordini |
| `Category` | `name` | una categoria puo avere molti piatti |
| `Dish` | `name`, `description`, `price`, `is_active`, `is_available` | ogni piatto appartiene a una categoria |
| `Order` | `user`, `status`, `created_at`, `notes`, `total_amount` | un ordine appartiene a un utente e contiene molti `OrderItem` |
| `OrderItem` | `dish`, `quantity`, `unit_price` | ogni riga collega un ordine a un piatto |
| `Review` | `order`, `rating`, `comment`, `created_at` | ogni recensione e associata one-to-one a un ordine |

## API principali

### Autenticazione

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`

### Menu

- `GET /api/categories/`
- `GET /api/dishes/`

### Ordini

- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/{id}/`
- `PATCH /api/orders/{id}/status/`

### Recensioni e AI

- `GET /api/reviews/`
- `POST /api/reviews/`
- `GET /api/reviews/ai-summary/`

## Variabili d'ambiente

Le variabili rilevanti per eseguire il progetto in locale sono:

| Variabile | Dove | Obbligatoria | Descrizione |
| --- | --- | --- | --- |
| `GEMINI_API_KEY` | `backend/.env` | si, per la feature AI | API key personale per l'analisi delle recensioni |
| `VITE_API_BASE_URL` | `frontend/.env` | consigliata | URL base delle API backend, di default `http://127.0.0.1:8000/api` |

Per ottenere `GEMINI_API_KEY` e possibile usare Google AI Studio.

## Setup ambiente

Le istruzioni dettagliate per installazione e avvio locale sono documentate in [docs/Setup_Ambiente.md](/Users/elisabettafino/Desktop/Dark-kitchen/kitchen-manager/docs/Setup_Ambiente.md).

Panoramica rapida:

- clonare il repository
- creare e attivare il virtual environment `.venv`
- installare le dipendenze backend da `backend/requirements.txt`
- eseguire il setup iniziale da `backend/` con `./setup_dev.sh`
- configurare `backend/.env` con `GEMINI_API_KEY` per la feature AI
- installare le dipendenze frontend con `npm install`
- avviare backend e frontend in locale

## Flusso di utilizzo

1. Avviare backend e frontend in locale.
2. Aprire il menu pubblico.
3. Registrarsi come cliente oppure accedere.
4. Creare un ordine con uno o piu piatti.
5. Accedere come admin per aggiornare lo stato dell'ordine.
6. Dopo la consegna, lasciare una recensione dal profilo cliente.
7. Accedere all'area admin recensioni per generare la sintesi AI.

Credenziali admin di test:

- username: `admin`
- password: `admin123`

## AWS Architecture

La struttura AWS proposta e concettuale e serve a mostrare come il progetto potrebbe essere organizzato in produzione, senza effettuare il deploy reale.

### Architettura proposta

| Servizio AWS | Ruolo nell'architettura |
| --- | --- |
| `Amazon Route 53` | Instrada il dominio verso frontend e API. |
| `Amazon CloudFront` | Pubblica il frontend in HTTPS e distribuisce i contenuti statici. |
| `Amazon S3` | Ospita la build statica React. |
| `Application Load Balancer` | Riceve il traffico API e lo distribuisce ai servizi backend. |
| `Amazon ECS Fargate` | Esegue il backend Django DRF in container senza gestire server EC2. |
| `Amazon RDS PostgreSQL` | Sostituisce SQLite in uno scenario di produzione. |
| `AWS Secrets Manager` | Conserva secret key, credenziali database e API key fuori dal codice. |
| `Amazon CloudWatch` | Raccoglie log, metriche e allarmi. |
| `External AI Provider` | Gestisce l'integrazione con Google Gemini API. |

### Strategia di sicurezza

| Aspetto | Sintesi |
| --- | --- |
| `Secrets Manager` | Secret key, credenziali database e API key verrebbero mantenute fuori dal codice. |
| `IAM roles e IAM policies` | Ogni componente riceverebbe solo i permessi minimi necessari. |
| `Security Groups` | Il load balancer sarebbe esposto verso l'esterno, mentre backend e database resterebbero accessibili solo ai componenti autorizzati. |
| Configurazione applicativa | In produzione andrebbero disattivati i parametri di sviluppo e configurati correttamente host consentiti, HTTPS e CORS. |

### Scalabilita e alta disponibilita

| Aspetto | Sintesi |
| --- | --- |
| Frontend | `S3 + CloudFront` permette di servire contenuti statici in modo facilmente scalabile. |
| Backend | `ECS Fargate` puo eseguire piu task distribuiti su Availability Zone diverse. |
| Load balancing | `Application Load Balancer` distribuisce il traffico solo verso task sani. |
| Crescita e guasti | In caso di aumento del carico si possono aumentare i task; in caso di guasto di una zona, l'altra puo continuare a servire l'applicazione. |
| Database | `RDS PostgreSQL` rende il livello dati piu adatto a un contesto di produzione rispetto a SQLite. |

### Stima indicativa dei costi

| Voce principale | Sintesi |
| --- | --- |
| `Amazon ECS Fargate` | Costo basato su CPU, memoria e storage utilizzati. |
| `Application Load Balancer` | Costo basato sul tempo di utilizzo e sul traffico gestito. |
| `Amazon RDS PostgreSQL` | Costo legato a istanza e storage scelti. |
| `Amazon S3 / Amazon CloudFront` | Costo contenuto per hosting e distribuzione del frontend statico. |
| `AWS Secrets Manager` | Costo dipendente dal numero di secret e dalle chiamate API. |

Ordine di grandezza stimato:

- versione essenziale: circa `50-90 USD` al mese
- versione piu robusta: circa `120-200 USD` al mese

## Project Management

Il team ha lavorato in modalita cross-funzionale con:

- brainstorming iniziale e selezione dell'idea
- definizione del problema e del target
- progettazione UX/UI e architettura applicativa
- suddivisione del lavoro per responsabilita
- versionamento su GitHub con branch dedicati
- allineamenti periodici in stile stand-up

## Note di coerenza rispetto al codice attuale

Questo README descrive il comportamento effettivamente supportato dal codice presente nel repository. In particolare:

- la feature AI attuale e focalizzata sull'analisi recensioni
- il menu esposto nel flusso principale e oggi read-only lato API pubblica
- la documentazione AWS rappresenta un bonus architetturale e non un deploy reale
