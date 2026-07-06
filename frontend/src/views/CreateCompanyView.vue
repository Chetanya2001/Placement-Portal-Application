<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import { registerCompany } from "./../services/company.service";

const router = useRouter();

const user = JSON.parse(localStorage.getItem("user"));

const form = ref({
  user_id: user.id,
  company_name: "",
  hr_name: "",
  hr_email: "",
  website: "",
  description: "",
});

const loading = ref(false);
const message = ref("");
const error = ref("");

async function submitForm() {
  loading.value = true;
  message.value = "";
  error.value = "";

  try {
    const res = await registerCompany(form.value);

    if (res.message) {
      message.value = res.message;

      setTimeout(() => {
        router.push("/company-dashboard");
      }, 1500);
    }
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to create company profile.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page">
    <div class="card">
      <div class="card-header">
        <div class="brand">
          <span class="brand-mark">&lt;/&gt;</span>
          <span class="brand-name">Placement Portal</span>
        </div>
        <h2>Create Company Profile</h2>
        <p class="subtitle">
          Tell us about your company so students and admins can find you. An
          admin will review this before you can post drives.
        </p>
      </div>

      <form class="profile-form" @submit.prevent="submitForm">
        <label class="field">
          <span class="field-label">Company Name</span>
          <input v-model="form.company_name" type="text" required />
        </label>

        <div class="field-row">
          <label class="field">
            <span class="field-label">HR Name</span>
            <input v-model="form.hr_name" type="text" required />
          </label>

          <label class="field">
            <span class="field-label">HR Email</span>
            <input v-model="form.hr_email" type="email" required />
          </label>
        </div>

        <label class="field">
          <span class="field-label">Website</span>
          <input
            v-model="form.website"
            type="url"
            placeholder="https://example.com"
            required
          />
        </label>

        <label class="field">
          <span class="field-label">Description</span>
          <textarea
            v-model="form.description"
            rows="4"
            placeholder="What does your company do, and what kind of roles do you typically hire for?"
            required
          ></textarea>
        </label>

        <div v-if="error" class="error-banner" role="alert">
          {{ error }}
        </div>

        <div v-if="message" class="success-banner" role="status">
          {{ message }}
          <span class="redirect-note">Taking you to your dashboard…</span>
        </div>

        <button class="btn-primary" type="submit" :disabled="loading">
          <span v-if="loading" class="spinner" aria-hidden="true"></span>
          {{ loading ? "Creating" : "Create Company" }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page {
  --green: #2ec866;
  --green-dark: #1f9e4f;
  --green-tint: #e6faee;
  --black: #0d1021;
  --black-soft: #171a2e;
  --gray-100: #f6f7f9;
  --gray-200: #eceef1;
  --gray-400: #9aa0ab;
  --gray-600: #5b6270;
  --white: #ffffff;
  --red: #e5484d;
  --red-tint: #fdeceb;
  --radius: 10px;
  --shadow-hover: 0 8px 24px rgba(13, 16, 33, 0.1);
  --transition: 180ms ease;

  min-height: 100vh;
  padding: 48px 20px;
  background: var(--gray-100);
  background-image: radial-gradient(
    circle at 85% 0%,
    var(--green-tint),
    transparent 45%
  );
  font-family:
    "Inter",
    "Sora",
    "Space Grotesk",
    -apple-system,
    BlinkMacSystemFont,
    sans-serif;
  color: var(--black);
  display: flex;
  justify-content: center;
}

*:focus-visible {
  outline: 2px solid var(--green);
  outline-offset: 2px;
}

.card {
  width: 100%;
  max-width: 560px;
  background: var(--white);
  border-radius: var(--radius);
  box-shadow: var(--shadow-hover);
  padding: 32px 32px 36px;
}

.card-header {
  margin-bottom: 24px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.brand-mark {
  color: var(--green-dark);
  font-family: monospace;
  font-weight: 700;
  font-size: 16px;
}
.brand-name {
  font-weight: 700;
  font-size: 13px;
  color: var(--gray-600);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.card-header h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--black);
  text-align: left;
}
.subtitle {
  font-size: 13px;
  color: var(--gray-600);
  margin: 0;
  line-height: 1.5;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}
.field-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-600);
}

.field-row {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}
.field-row .field {
  flex: 1 1 200px;
}

input,
textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  color: var(--black);
  background: var(--gray-100);
  box-sizing: border-box;
  min-height: 44px;
  transition:
    border-color var(--transition),
    background var(--transition);
}
textarea {
  min-height: 100px;
  resize: vertical;
}
input::placeholder,
textarea::placeholder {
  color: var(--gray-400);
}
input:focus,
textarea:focus {
  border-color: var(--green);
  background: var(--white);
  outline: none;
}

.error-banner {
  background: var(--red-tint);
  color: var(--red);
  border: 1px solid #f5b5b7;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 13px;
}

.success-banner {
  background: var(--green-tint);
  color: var(--green-dark);
  border: 1px solid #b7ecc9;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.redirect-note {
  font-size: 12px;
  color: var(--green-dark);
  opacity: 0.8;
}

.btn-primary {
  width: 100%;
  background: var(--green);
  color: var(--black);
  border: none;
  border-radius: 8px;
  padding: 13px 16px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  min-height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition:
    background var(--transition),
    box-shadow var(--transition),
    transform var(--transition),
    opacity var(--transition);
}
.btn-primary:hover:not(:disabled) {
  background: var(--green-dark);
  box-shadow: var(--shadow-hover);
}
.btn-primary:active:not(:disabled) {
  transform: scale(0.98);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--black);
  border-right-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 480px) {
  .card {
    padding: 26px 20px 30px;
  }
  .field-row {
    flex-direction: column;
  }
}
</style>
