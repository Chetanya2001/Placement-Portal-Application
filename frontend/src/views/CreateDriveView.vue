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
  <div class="container mt-5">
    <div class="card shadow p-4">
      <h2 class="mb-4">Create Placement Drive</h2>

      <div class="mb-3">
        <label>Job Title</label>
        <input v-model="job.job_title" class="form-control" />
      </div>

      <div class="mb-3">
        <label>Job Description</label>
        <textarea
          v-model="job.job_description"
          rows="5"
          class="form-control"
        ></textarea>
      </div>

      <div class="mb-3">
        <label>Location</label>
        <input v-model="job.location" class="form-control" />
      </div>

      <div class="mb-3">
        <label>Salary Package (LPA)</label>
        <input
          type="number"
          step="0.1"
          class="form-control"
          v-model="job.salary_package"
        />
      </div>

      <div class="mb-3">
        <label>Eligible Branches</label>
        <input
          class="form-control"
          placeholder="CSE,ECE,ME"
          v-model="job.eligibility_branch"
        />
      </div>

      <div class="mb-3">
        <label>Minimum CGPA</label>
        <input
          type="number"
          step="0.1"
          class="form-control"
          v-model="job.min_cgpa"
        />
      </div>

      <div class="mb-3">
        <label>Eligible Year</label>
        <input type="number" class="form-control" v-model="job.eligible_year" />
      </div>

      <div class="mb-3">
        <label>Application Deadline</label>
        <input
          type="date"
          class="form-control"
          v-model="job.application_deadline"
        />
      </div>

      <div class="mb-3">
        <label>Drive Date</label>
        <input type="date" class="form-control" v-model="job.drive_date" />
      </div>

      <div v-if="message" class="alert alert-danger">
        {{ message }}
      </div>

      <button class="btn btn-success" @click="submitDrive" :disabled="loading">
        {{ loading ? "Creating..." : "Create Drive" }}
      </button>
    </div>
  </div>
</template>
s
