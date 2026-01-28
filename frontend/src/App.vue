<template>
  <div class="container">
    <header class="header">
      <div>
        <h1>HelloIN Visitor Onboarding</h1>
        <p>Compila il tuo accesso in pochi minuti con firma digitale.</p>
      </div>
      <span class="badge">MVP Demo</span>
    </header>

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

        <button class="secondary" style="margin-top: 16px" @click="completeVisit" :disabled="status !== 'submitted'">
          Completa check-in
        </button>
      </section>
    </div>

    <section class="card admin-section">
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
          <button class="secondary" type="button" @click="refreshAdminData" :disabled="adminLoading">
            {{ adminLoading ? "Aggiornamento..." : "Aggiorna dati" }}
          </button>
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
              <tr v-for="visit in adminVisits" :key="visit._id">
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
  } catch (error) {
    adminError.value = "Credenziali non valide o errore di rete.";
    adminStats.value = null;
    adminVisits.value = [];
    adminAuthHeader.value = "";
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
