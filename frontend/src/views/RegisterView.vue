<script setup>
import { ref } from "vue";
import { registerUser } from "@/services/auth.service";
const name = ref("");
const email = ref("");
const password = ref("");
const role = ref("Student"); // Default selected

// --- Added UX-only state (does not change any existing auth logic) ---
const isLoading = ref(false); // drives the button spinner / disabled state
const errorMessage = ref(""); // inline banner, shown alongside the existing alert()
const showPassword = ref(false); // eye-toggle for the password field

const register = async () => {
  errorMessage.value = "";
  isLoading.value = true;
  try {
    const result = await registerUser({
      name: name.value,
      email: email.value,
      password: password.value,
      role: role.value,
    });

    alert(result.message);
  } catch (error) {
    errorMessage.value = error.message;
    alert(error.message);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <span class="brand-mark">&lt;/&gt;</span>
        <span class="brand-name">Placement Portal</span>
      </div>

      <h2>Create account</h2>
      <p class="auth-sub">
        Register to apply for drives or post job opportunities.
      </p>

      <div v-if="errorMessage" class="error-banner" role="alert">
        {{ errorMessage }}
      </div>

      <form class="auth-form" @submit.prevent="register">
        <label class="field">
          <span class="field-label">Name</span>
          <input
            v-model="name"
            type="text"
            placeholder="Your full name"
            autocomplete="name"
            required
          />
        </label>

        <label class="field">
          <span class="field-label">Email</span>
          <input
            v-model="email"
            type="email"
            placeholder="you@company.com"
            autocomplete="email"
            required
          />
        </label>

        <label class="field">
          <span class="field-label">Password</span>
          <div class="password-wrap">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Create a password"
              autocomplete="new-password"
              required
            />
            <button
              type="button"
              class="toggle-visibility"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              @click="showPassword = !showPassword"
            >
              <svg
                v-if="!showPassword"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <circle
                  cx="12"
                  cy="12"
                  r="3"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
              <svg
                v-else
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M3 3l18 18M10.6 10.6a3 3 0 0 0 4.24 4.24M9.9 4.24A11.7 11.7 0 0 1 12 4c7 0 11 7 11 7a13.6 13.6 0 0 1-2.6 3.4M6.6 6.6A13.6 13.6 0 0 0 1 11.99s4 7 11 7a11.6 11.6 0 0 0 3.4-.5"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </button>
          </div>
        </label>

        <!-- Role Toggle -->
        <label class="field">
          <span class="field-label">I am a</span>
          <div
            class="toggle-container"
            role="radiogroup"
            aria-label="Account type"
          >
            <label
              class="toggle-option"
              :class="{ active: role === 'Student' }"
            >
              <input type="radio" value="Student" v-model="role" />
              Student
            </label>

            <label
              class="toggle-option"
              :class="{ active: role === 'Company' }"
            >
              <input type="radio" value="Company" v-model="role" />
              Company
            </label>
          </div>
        </label>

        <button class="btn-primary" type="submit" :disabled="isLoading">
          <span v-if="isLoading" class="spinner" aria-hidden="true"></span>
          {{ isLoading ? "Creating account" : "Register" }}
        </button>
      </form>

      <p class="auth-footer">
        Already have an account?
        <router-link to="/login">Login</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
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
  --shadow: 0 1px 2px rgba(13, 16, 33, 0.06), 0 4px 12px rgba(13, 16, 33, 0.06);
  --shadow-hover: 0 8px 24px rgba(13, 16, 33, 0.12);
  --transition: 180ms ease;

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--gray-100);
  background-image: radial-gradient(
    circle at 15% 15%,
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
}

*:focus-visible {
  outline: 2px solid var(--green);
  outline-offset: 2px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--white);
  border-radius: var(--radius);
  padding: 32px 28px;
  box-shadow: var(--shadow-hover);
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 22px;
}
.brand-mark {
  color: var(--green-dark);
  font-family: monospace;
  font-weight: 700;
  font-size: 16px;
}
.brand-name {
  font-weight: 700;
  font-size: 14px;
  color: var(--black);
  letter-spacing: -0.01em;
}

.auth-card h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--black);
}
.auth-sub {
  font-size: 13px;
  color: var(--gray-600);
  margin: 0 0 20px;
}

.error-banner {
  background: var(--red-tint);
  color: var(--red);
  border: 1px solid #f5b5b7;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
  margin-bottom: 16px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-600);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.field input[type="text"],
.field input[type="email"],
.field input[type="password"] {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
  color: var(--black);
  background: var(--gray-100);
  transition:
    border-color var(--transition),
    background var(--transition);
  min-height: 44px;
  box-sizing: border-box;
}
.field input::placeholder {
  color: var(--gray-400);
}
.field input:focus {
  border-color: var(--green);
  background: var(--white);
  outline: none;
}

.password-wrap {
  position: relative;
  display: flex;
}
.password-wrap input {
  padding-right: 42px;
}
.toggle-visibility {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--gray-400);
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  min-height: auto;
}
.toggle-visibility:hover {
  color: var(--black);
}

/* ---------------- Role toggle ---------------- */
.toggle-container {
  display: flex;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  overflow: hidden;
  background: var(--gray-100);
}
.toggle-option {
  flex: 1;
  text-align: center;
  padding: 11px 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-600);
  transition:
    background var(--transition),
    color var(--transition);
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.toggle-option input {
  display: none;
}
.toggle-option.active {
  background: var(--green);
  color: var(--black);
}
.toggle-option:hover:not(.active) {
  background: var(--gray-200);
  color: var(--black);
}

button {
  font-family: inherit;
}

.btn-primary {
  width: 100%;
  background: var(--green);
  color: var(--black);
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
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
  margin-top: 4px;
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

.auth-footer {
  text-align: center;
  font-size: 13px;
  color: var(--gray-600);
  margin: 20px 0 0;
}
.auth-footer a {
  color: var(--green-dark);
  font-weight: 600;
  text-decoration: none;
}
.auth-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 420px) {
  .auth-card {
    padding: 26px 20px;
  }
}
</style>
