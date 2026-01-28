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
