<!-- StudentRegisterProfile.vue -->
<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import { registerStudent } from "./../services/student.service";

const router = useRouter();

const user = JSON.parse(localStorage.getItem("user"));

const form = ref({
  user_id: user.id,
  branch: "",
  cgpa: "",
  year: "",
  phone: "",
  skills: "",
  resume: "",
});

const loading = ref(false);
const message = ref("");
const error = ref("");

async function submitForm() {
  loading.value = true;
  message.value = "";
  error.value = "";

  try {
    const res = await registerStudent(form.value);

    if (res.message) {
      message.value = res.message;

      setTimeout(() => {
        router.push("/student-dashboard");
      }, 1500);
    }
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to create student profile.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="container">
    <div class="card">
      <h2>Complete Your Profile</h2>

      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label>Branch</label>
          <input
            v-model="form.branch"
            type="text"
            placeholder="e.g. Computer Science"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>CGPA</label>
            <input
              v-model="form.cgpa"
              type="number"
              step="0.01"
              min="0"
              max="10"
              placeholder="e.g. 8.5"
              required
            />
          </div>

          <div class="form-group">
            <label>Graduation Year</label>
            <input
              v-model="form.year"
              type="number"
              placeholder="e.g. 2025"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label>Phone Number</label>
          <input
            v-model="form.phone"
            type="tel"
            placeholder="e.g. 9876543210"
            required
          />
        </div>

        <div class="form-group">
          <label>Skills</label>
          <textarea
            v-model="form.skills"
            rows="3"
            placeholder="e.g. Python, React, SQL, Machine Learning"
            required
          ></textarea>
        </div>

        <div class="form-group">
          <label>Resume Link</label>
          <input
            v-model="form.resume"
            type="url"
            placeholder="https://drive.google.com/your-resume"
          />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? "Saving..." : "Save Profile" }}
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
  width: 520px;
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
  width: 100%;
}

/* Side-by-side CGPA and Year */
.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
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
  margin-top: 4px;
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
