<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { createJob } from "@/services/company.service";

const router = useRouter();

const job = ref({
  job_title: "",
  job_description: "",
  location: "",
  salary_package: "",
  eligibility_branch: "",
  min_cgpa: "",
  eligible_year: "",
  application_deadline: "",
  drive_date: "",
});

const loading = ref(false);
const message = ref("");

async function submitDrive() {
  loading.value = true;
  message.value = "";

  try {
    const response = await createJob(job.value);

    if (response.message) {
      alert("Placement Drive Created Successfully");
      router.push("/company-dashboard");
    } else {
      message.value = response.error || "Something went wrong";
    }
  } catch (err) {
    message.value = "Server Error";
  }

  loading.value = false;
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
        <h2>Create Placement Drive</h2>
        <p class="subtitle">
          Fill in the role details so eligible students can find and apply to
          it.
        </p>
      </div>

      <form class="drive-form" @submit.prevent="submitDrive">
        <!-- Role basics -->
        <fieldset class="group">
          <legend>Role details</legend>

          <label class="field">
            <span class="field-label">Job Title</span>
            <input
              v-model="job.job_title"
              type="text"
              placeholder="e.g. Software Engineer"
              required
            />
          </label>

          <label class="field">
            <span class="field-label">Job Description</span>
            <textarea
              v-model="job.job_description"
              rows="5"
              placeholder="Responsibilities, tech stack, what a typical day looks like..."
            ></textarea>
          </label>

          <div class="field-row">
            <label class="field">
              <span class="field-label">Location</span>
              <input
                v-model="job.location"
                type="text"
                placeholder="e.g. Bengaluru / Remote"
              />
            </label>

            <label class="field">
              <span class="field-label">Salary Package (LPA)</span>
              <input
                type="number"
                step="0.1"
                placeholder="e.g. 8.5"
                v-model="job.salary_package"
              />
            </label>
          </div>
        </fieldset>

        <!-- Eligibility -->
        <fieldset class="group">
          <legend>Eligibility</legend>

          <label class="field">
            <span class="field-label">Eligible Branches</span>
            <input
              placeholder="CSE, ECE, ME"
              v-model="job.eligibility_branch"
            />
            <span class="field-hint">Comma-separated, e.g. CSE,ECE,ME</span>
          </label>

          <div class="field-row">
            <label class="field">
              <span class="field-label">Minimum CGPA</span>
              <input
                type="number"
                step="0.1"
                placeholder="e.g. 7.0"
                v-model="job.min_cgpa"
              />
            </label>

            <label class="field">
              <span class="field-label">Eligible Year</span>
              <input
                type="number"
                placeholder="e.g. 2026"
                v-model="job.eligible_year"
              />
            </label>
          </div>
        </fieldset>

        <!-- Dates -->
        <fieldset class="group">
          <legend>Timeline</legend>

          <div class="field-row">
            <label class="field">
              <span class="field-label">Application Deadline</span>
              <input type="date" v-model="job.application_deadline" />
            </label>

            <label class="field">
              <span class="field-label">Drive Date</span>
              <input type="date" v-model="job.drive_date" />
            </label>
          </div>
        </fieldset>

        <div v-if="message" class="error-banner" role="alert">
          {{ message }}
        </div>

        <button class="btn-primary" type="submit" :disabled="loading">
          <span v-if="loading" class="spinner" aria-hidden="true"></span>
          {{ loading ? "Creating" : "Create Drive" }}
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
  max-width: 640px;
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
}
.subtitle {
  font-size: 13px;
  color: var(--gray-600);
  margin: 0;
  line-height: 1.5;
}

.drive-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.group {
  border: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.group legend {
  font-size: 12px;
  font-weight: 700;
  color: var(--green-dark);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--gray-200);
  padding-bottom: 8px;
  width: 100%;
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
.field-hint {
  font-size: 11px;
  color: var(--gray-400);
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
  min-height: 110px;
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

@media (max-width: 520px) {
  .card {
    padding: 26px 20px 30px;
  }
  .field-row {
    flex-direction: column;
  }
}
</style>
