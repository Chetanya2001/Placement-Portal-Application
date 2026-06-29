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
        router.push("/company/dashboard");
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
  <div class="container">
    <div class="card">
      <h2>Create Company Profile</h2>

      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label>Company Name</label>
          <input v-model="form.company_name" type="text" required />
        </div>

        <div class="form-group">
          <label>HR Name</label>
          <input v-model="form.hr_name" type="text" required />
        </div>

        <div class="form-group">
          <label>HR Email</label>
          <input v-model="form.hr_email" type="email" required />
        </div>

        <div class="form-group">
          <label>Website</label>
          <input
            v-model="form.website"
            type="url"
            placeholder="https://example.com"
            required
          />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" rows="4" required></textarea>
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? "Creating..." : "Create Company" }}
        </button>
      </form>

      <p class="success" v-if="message">{{ message }}</p>
      <p class="error" v-if="error">{{ error }}</p>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.card {
  width: 500px;
  background: #fff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 6px;
}

input,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #bbb;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 14px;
}

textarea {
  resize: vertical;
}

button {
  width: 100%;
  padding: 12px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
}

button:hover {
  background: #1d4ed8;
}

button:disabled {
  background: gray;
  cursor: not-allowed;
}

.success {
  color: green;
  text-align: center;
  margin-top: 15px;
}

.error {
  color: red;
  text-align: center;
  margin-top: 15px;
}
</style>
