<template>
  <div class="container">
    <header class="header">
      <div>
        <h1>HelloIN Visitor Onboarding</h1>
        <p>Compila il tuo accesso in pochi minuti con firma digitale.</p>
      </div>
      <span class="badge">MVP Demo</span>
    </header>

    <nav class="section-menu" aria-label="Sezioni principali">
      <button
        type="button"
        class="menu-button"
        :class="{ active: activeSection === 'visitor' }"
        @click="activeSection = 'visitor'"
      >
        Area visitatori
      </button>
      <button
        type="button"
        class="menu-button"
        :class="{ active: activeSection === 'admin' }"
        @click="activeSection = 'admin'"
      >
        Area admin
      </button>
    </nav>

    <div v-if="activeSection === 'visitor'">
      <div class="grid">
        <section class="card">
          <h2>1. Dati visitatore</h2>
          <form @submit.prevent="submitVisit">
            <div class="form-group">
              <label for="firstName">Nome</label>
              <input id="firstName" v-model="form.first_name" required />
            </div>
            <div class="form-group">
              <label for="lastName">Cognome</label>
              <input id="lastName" v-model="form.last_name" required />
            </div>
            <div class="form-group">
              <label for="company">Azienda</label>
              <input id="company" v-model="form.company" required />
            </div>
            <div class="form-group">
              <label for="email">Email</label>
              <input id="email" type="email" v-model="form.email" required />
            </div>
            <div class="form-group">
              <label for="phone">Telefono</label>
              <input id="phone" v-model="form.phone" />
            </div>
            <div class="form-group">
              <label for="purpose">Motivo della visita</label>
              <textarea id="purpose" v-model="form.purpose"></textarea>
            </div>

            <div class="form-group">
              <label>Consensi</label>
              <div class="checkbox-row">
                <input id="privacy" type="checkbox" v-model="consents.privacy" />
                <label for="privacy">
                  Ho letto e accetto l'informativa privacy (obbligatoria).
                </label>
              </div>
              <div class="checkbox-row">
                <input id="marketing" type="checkbox" v-model="consents.marketing" />
                <label for="marketing">Accetto comunicazioni marketing (facoltativo).</label>
              </div>
            </div>

            <div class="form-group">
              <label>Firma digitale</label>
              <SignaturePad @signed="handleSignature" />
              <p v-if="signaturePreview" class="status info">Firma acquisita.</p>
            </div>

            <button class="primary" type="submit" :disabled="loading">
              {{ loading ? "Invio..." : "Invia dati" }}
            </button>
          </form>
        </section>

        <section class="card">
          <h2>2. Informativa privacy</h2>
          <div class="status info" v-if="privacy">
            <strong>Versione {{ privacy.version }}</strong>
            <p>{{ privacy.text }}</p>
          </div>
          <div v-else class="status info">Caricamento informativa...</div>

          <h2 style="margin-top: 24px">3. Stato onboarding</h2>
          <div class="timeline">
            <div class="timeline-item completed">
              <span class="timeline-dot"></span>
              <span>Accesso avviato</span>
            </div>
            <div class="timeline-item" :class="{ completed: status === 'submitted' || status === 'completed' }">
              <span class="timeline-dot"></span>
              <span>Dati e consensi inviati</span>
            </div>
            <div class="timeline-item" :class="{ completed: status === 'completed' }">
              <span class="timeline-dot"></span>
              <span>Onboarding completato</span>
            </div>
          </div>

          <div v-if="status === 'completed'" class="status success" style="margin-top: 20px">
            Grazie! La tua registrazione è stata completata con successo.
          </div>
          <div v-else class="status info" style="margin-top: 20px">
            {{ statusMessage }}
          </div>

          <button
            class="secondary"
            style="margin-top: 16px"
            @click="completeVisit"
            :disabled="status !== 'submitted'"
          >
            Completa check-in
          </button>
        </section>
      </div>
    </div>

    <section v-else class="card admin-section">
      <div class="admin-header">
        <div>
          <h2>Area admin</h2>
          <p>Accesso protetto per consultare statistiche e onboarding.</p>
        </div>
        <button v-if="adminAuthenticated" class="secondary" type="button" @click="logoutAdmin">
          Logout
        </button>
      </div>

      <div v-if="!adminAuthenticated" class="admin-login">
        <div class="form-group">
          <label for="adminUser">Nome utente</label>
          <input id="adminUser" v-model="adminCredentials.username" autocomplete="username" />
        </div>
        <div class="form-group">
          <label for="adminPassword">Password</label>
          <input
            id="adminPassword"
            v-model="adminCredentials.password"
            type="password"
            autocomplete="current-password"
          />
        </div>
        <button class="primary" type="button" @click="loginAdmin" :disabled="adminLoading">
          {{ adminLoading ? "Accesso..." : "Accedi" }}
        </button>
        <p v-if="adminError" class="status error" style="margin-top: 12px">{{ adminError }}</p>
      </div>

      <div v-else>
        <div class="admin-actions">
          <div class="admin-filters">
            <div class="form-group">
              <label for="adminSearch">Ricerca</label>
              <input
                id="adminSearch"
                v-model="adminSearch"
                type="search"
                placeholder="Cerca per nome, email, azienda o motivo"
              />
            </div>
            <div class="form-group">
              <label for="adminStatusFilter">Stato</label>
              <select id="adminStatusFilter" v-model="adminStatusFilter">
                <option value="all">Tutti</option>
                <option value="started">Avviati</option>
                <option value="submitted">Inviati</option>
                <option value="completed">Completati</option>
              </select>
            </div>
            <div class="form-group">
              <label for="adminConsentFilter">Consensi</label>
              <select id="adminConsentFilter" v-model="adminConsentFilter">
                <option value="all">Tutti</option>
                <option value="privacy_yes">Privacy: Sì</option>
                <option value="privacy_no">Privacy: No</option>
                <option value="marketing_yes">Marketing: Sì</option>
                <option value="marketing_no">Marketing: No</option>
              </select>
            </div>
          </div>
          <div class="admin-action-buttons">
            <span class="muted">
              {{ filteredVisits.length }} su {{ adminVisits.length }} registrazioni
            </span>
            <button class="secondary" type="button" @click="refreshAdminData" :disabled="adminLoading">
              {{ adminLoading ? "Aggiornamento..." : "Aggiorna dati" }}
            </button>
            <button
              class="danger"
              type="button"
              @click="deleteSelectedVisits"
              :disabled="adminLoading || selectedVisitIds.length === 0"
            >
              Elimina selezionati ({{ selectedVisitIds.length }})
            </button>
          </div>
        </div>

        <div v-if="adminStats" class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">Totale onboarding</span>
            <strong>{{ adminStats.total }}</strong>
          </div>
          <div class="stat-card">
            <span class="stat-label">Avviati</span>
            <strong>{{ adminStats.started }}</strong>
          </div>
          <div class="stat-card">
            <span class="stat-label">Inviati</span>
            <strong>{{ adminStats.submitted }}</strong>
          </div>
          <div class="stat-card">
            <span class="stat-label">Completati</span>
            <strong>{{ adminStats.completed }}</strong>
          </div>
        </div>

        <div class="admin-table" v-if="adminVisits.length">
          <table>
            <thead>
              <tr>
                <th class="select-column">
                  <input
                    type="checkbox"
                    :checked="allVisibleSelected"
                    :aria-checked="allVisibleSelected"
                    @change="toggleSelectAll($event.target.checked)"
                  />
                </th>
                <th>Visitatore</th>
                <th>Azienda</th>
                <th>Contatti</th>
                <th>Stato</th>
                <th>Consensi</th>
                <th>Timestamp</th>
                <th>Dati completi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="visit in filteredVisits" :key="visit._id">
                <td class="select-column">
                  <input
                    type="checkbox"
                    :checked="selectedVisitIds.includes(visit._id)"
                    @change="toggleVisitSelection(visit._id)"
                  />
                </td>
                <td>
                  <strong>{{ formatVisitorName(visit) }}</strong>
                  <div class="muted">{{ visit.form_data?.purpose || "N/D" }}</div>
                </td>
                <td>{{ visit.form_data?.company || "N/D" }}</td>
                <td>
                  <div>{{ visit.form_data?.email || "N/D" }}</div>
                  <div class="muted">{{ visit.form_data?.phone || "N/D" }}</div>
                </td>
                <td><span class="pill">{{ visit.status }}</span></td>
                <td>
                  <div>Privacy: {{ visit.consents?.privacy ? "Sì" : "No" }}</div>
                  <div class="muted">Marketing: {{ visit.consents?.marketing ? "Sì" : "No" }}</div>
                </td>
                <td>
                  <div>Creato: {{ visit.created_at }}</div>
                  <div class="muted">Aggiornato: {{ visit.updated_at }}</div>
                </td>
                <td>
                  <pre>{{ formatVisitJson(visit) }}</pre>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="adminVisits.length && filteredVisits.length === 0" class="status info" style="margin-top: 12px">
            Nessun risultato per i filtri selezionati.
          </div>
        </div>
        <div v-else class="status info" style="margin-top: 16px">
          Nessun onboarding disponibile.
        </div>
      </div>
    </section>

    <footer class="footer">HelloIN © 2024 · Demo onboarding visitatori</footer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import axios from "axios";
import SignaturePad from "./components/SignaturePad.vue";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

const form = reactive({
  first_name: "",
  last_name: "",
  company: "",
  email: "",
  phone: "",
  purpose: "",
});

const consents = reactive({
  privacy: false,
  marketing: false,
});

const privacy = ref(null);
const token = ref("");
const status = ref("started");
const loading = ref(false);
const signaturePreview = ref("");
const adminCredentials = reactive({
  username: "",
  password: "",
});
const adminStats = ref(null);
const adminVisits = ref([]);
const adminError = ref("");
const adminLoading = ref(false);
const adminAuthHeader = ref("");
const adminSearch = ref("");
const adminStatusFilter = ref("all");
const adminConsentFilter = ref("all");
const selectedVisitIds = ref([]);
const activeSection = ref("visitor");

const statusMessage = computed(() => {
  if (status.value === "submitted") {
    return "Dati ricevuti. Completa il check-in quando pronto.";
  }
  if (status.value === "completed") {
    return "Check-in completato.";
  }
  return "Compila il form per continuare.";
});

const handleSignature = (dataUrl) => {
  signaturePreview.value = dataUrl;
};

const adminAuthenticated = computed(() => Boolean(adminAuthHeader.value));

const filteredVisits = computed(() => {
  const searchTerm = adminSearch.value.trim().toLowerCase();
  return adminVisits.value.filter((visit) => {
    const name = formatVisitorName(visit).toLowerCase();
    const company = visit.form_data?.company?.toLowerCase() || "";
    const email = visit.form_data?.email?.toLowerCase() || "";
    const phone = visit.form_data?.phone?.toLowerCase() || "";
    const purpose = visit.form_data?.purpose?.toLowerCase() || "";
    const status = visit.status?.toLowerCase() || "";
    const matchesSearch = !searchTerm
      ? true
      : [name, company, email, phone, purpose, status].some((value) => value.includes(searchTerm));

    const statusFilter = adminStatusFilter.value;
    const matchesStatus = statusFilter === "all" ? true : visit.status === statusFilter;

    const consentFilter = adminConsentFilter.value;
    let matchesConsent = true;
    if (consentFilter === "privacy_yes") {
      matchesConsent = Boolean(visit.consents?.privacy);
    } else if (consentFilter === "privacy_no") {
      matchesConsent = !visit.consents?.privacy;
    } else if (consentFilter === "marketing_yes") {
      matchesConsent = Boolean(visit.consents?.marketing);
    } else if (consentFilter === "marketing_no") {
      matchesConsent = !visit.consents?.marketing;
    }

    return matchesSearch && matchesStatus && matchesConsent;
  });
});

const allVisibleSelected = computed(() => {
  if (filteredVisits.value.length === 0) {
    return false;
  }
  return filteredVisits.value.every((visit) => selectedVisitIds.value.includes(visit._id));
});

const buildAdminAuthHeader = (username, password) => {
  return `Basic ${btoa(`${username}:${password}`)}`;
};

const fetchAdminData = async (authHeader) => {
  adminLoading.value = true;
  adminError.value = "";
  try {
    const [statsResponse, visitsResponse] = await Promise.all([
      axios.get(`${apiBaseUrl}/admin/stats`, {
        headers: { Authorization: authHeader },
      }),
      axios.get(`${apiBaseUrl}/admin/visits`, {
        headers: { Authorization: authHeader },
      }),
    ]);
    adminStats.value = statsResponse.data;
    adminVisits.value = visitsResponse.data;
    adminAuthHeader.value = authHeader;
    selectedVisitIds.value = [];
  } catch (error) {
    adminError.value = "Credenziali non valide o errore di rete.";
    adminStats.value = null;
    adminVisits.value = [];
    adminAuthHeader.value = "";
    selectedVisitIds.value = [];
  } finally {
    adminLoading.value = false;
  }
};

const loginAdmin = async () => {
  const authHeader = buildAdminAuthHeader(
    adminCredentials.username,
    adminCredentials.password
  );
  await fetchAdminData(authHeader);
};

const refreshAdminData = async () => {
  if (!adminAuthHeader.value) {
    return;
  }
  await fetchAdminData(adminAuthHeader.value);
};

const logoutAdmin = () => {
  adminAuthHeader.value = "";
  adminCredentials.username = "";
  adminCredentials.password = "";
  adminStats.value = null;
  adminVisits.value = [];
  adminError.value = "";
  adminSearch.value = "";
  adminStatusFilter.value = "all";
  adminConsentFilter.value = "all";
  selectedVisitIds.value = [];
};

const toggleVisitSelection = (visitId) => {
  if (selectedVisitIds.value.includes(visitId)) {
    selectedVisitIds.value = selectedVisitIds.value.filter((id) => id !== visitId);
    return;
  }
  selectedVisitIds.value = [...selectedVisitIds.value, visitId];
};

const toggleSelectAll = (shouldSelect) => {
  if (!shouldSelect) {
    const visibleIds = filteredVisits.value.map((visit) => visit._id);
    selectedVisitIds.value = selectedVisitIds.value.filter((id) => !visibleIds.includes(id));
    return;
  }
  const selection = new Set(selectedVisitIds.value);
  filteredVisits.value.forEach((visit) => selection.add(visit._id));
  selectedVisitIds.value = Array.from(selection);
};

const deleteSelectedVisits = async () => {
  if (!adminAuthHeader.value || selectedVisitIds.value.length === 0) {
    return;
  }
  const confirmed = window.confirm(
    `Confermi l'eliminazione di ${selectedVisitIds.value.length} registrazioni?`
  );
  if (!confirmed) {
    return;
  }
  adminLoading.value = true;
  adminError.value = "";
  try {
    await axios.post(
      `${apiBaseUrl}/admin/visits/delete`,
      { ids: selectedVisitIds.value },
      { headers: { Authorization: adminAuthHeader.value } }
    );
    await fetchAdminData(adminAuthHeader.value);
  } catch (error) {
    adminError.value = "Impossibile eliminare le registrazioni selezionate.";
  } finally {
    adminLoading.value = false;
  }
};

const formatVisitorName = (visit) => {
  const firstName = visit.form_data?.first_name || "";
  const lastName = visit.form_data?.last_name || "";
  return `${firstName} ${lastName}`.trim() || "N/D";
};

const formatVisitJson = (visit) => JSON.stringify(visit, null, 2);

const fetchPrivacy = async () => {
  const { data } = await axios.get(`${apiBaseUrl}/privacy/latest`);
  privacy.value = data;
};

const startVisit = async () => {
  const { data } = await axios.post(`${apiBaseUrl}/visit/start`);
  token.value = data.token;
};

const submitVisit = async () => {
  loading.value = true;
  try {
    await axios.post(`${apiBaseUrl}/visit/${token.value}/submit`, {
      form_data: { ...form },
      consents: { ...consents },
      signature: {
        data_url: signaturePreview.value,
        signed_at: new Date().toISOString(),
      },
    });
    status.value = "submitted";
  } catch (error) {
    alert("Per favore accetta la privacy obbligatoria prima di inviare.");
  } finally {
    loading.value = false;
  }
};

const completeVisit = async () => {
  await axios.post(`${apiBaseUrl}/visit/${token.value}/complete`);
  status.value = "completed";
};

onMounted(async () => {
  await Promise.all([fetchPrivacy(), startVisit()]);
});
</script>
