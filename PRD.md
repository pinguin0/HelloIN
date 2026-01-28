# PRD – HelloIN Vibe Coding

Questo documento contiene il **Product Requirement Document (PRD)** per sviluppare un software con approccio **vibe coding** (iterativo, AI-assisted, focus su UX e velocità).

---

# PRD – HelloIN Software di Onboarding Visitatori

## 1. Visione del Prodotto

Realizzare un software web che consenta alle aziende di **gestire l'onboarding delle persone esterne** (visitatori, consulenti, fornitori) tramite un flusso digitale semplice, conforme alla privacy e con **firma elettronica**.

Il prodotto deve ridurre attriti, eliminare carta e garantire tracciabilità e compliance.

---

## 2. Obiettivi

* Digitalizzare il processo di accoglienza
* Garantire accettazione privacy e raccolta firma
* Migliorare la sicurezza e la compliance
* Ridurre il tempo di check-in

**Metriche di successo (KPI)**

* Tempo medio di completamento onboarding
* % onboarding completati senza assistenza
* Errori o campi incompleti per modulo

---

## 3. Target Utenti

* Visitatori aziendali
* Reception / HR
* Compliance / Legal

---

## 4. User Journey (Happy Path)

1. Il visitatore riceve un link (email / QR) oppure accede dal tablet presente in reception
2. Compila il modulo di ingresso (nome, cognome, email, cellulare, azienda, motivo visita, privecy e marketing)
3. Visualizza informativa privacy e marketing
4. Accetta e firma digitalmente
5. Conferma completamento
6. L’azienda riceve notifica via mail e registra l’accesso su DB

---

## 5. Funzionalità Core (MVP)

### 5.1 Gestione Moduli

* Campi configurabili (nome, documento, email, cellulare,azienda, motivo visita, privacy e marketing)
* Validazione client/server
* Localizzazione lingua

### 5.2 Privacy & Consenso

* Visualizzazione informativa GDPR
* Checkbox obbligatorie
* Versioning della privacy

### 5.3 Firma Digitale

* Firma disegnata (canvas)
* Timestamp e hash
* Associazione firma ↔ documento

### 5.4 Backend & Storage

* Salvataggio sicuro dati su DB
* Audit log
* Export PDF
* Procedura che cancella i dati più vecchi di 6 mesi (o configurabile)
---

## 6. Funzionalità Future

* Integrazione badge / tornelli
* OCR documento
* Firma avanzata (SPID / eIDAS)
* Dashboard analytics

---

## 7. Requisiti Non Funzionali

* Mobile-first
* GDPR compliant
* SLA ≥ 99.9%
* Hosting cloud

---

## 8. Tech & Vibe Coding Notes

* Frontend: Web responsive Vue.JS
* Backend: API REST Python Flask 
* Database: MongoDB
* Firma: canvas HTML5
* AI usage: generazione moduli, UX copy

