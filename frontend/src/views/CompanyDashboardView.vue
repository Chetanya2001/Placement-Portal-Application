<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import {
  getDashboard,
  getCompanyJobs,
  getApplicants,
  shortlistApplicant,
  rejectApplicant,
  selectApplicant,
  updateJobStatus,
  scheduleInterview,
} from "@/services/company.service";

const router = useRouter();

const user = JSON.parse(localStorage.getItem("user"));

const loading = ref(true);

const companyExists = ref(false);

const dashboard = ref({});

const jobs = ref([]);

const applicants = ref([]);

const selectedJob = ref(null);

const message = ref("");

const rejectReason = ref("");

const interviewData = ref({
  interview_date: "",
  interview_time: "",
  meeting_link: "",
});

const showReject = ref(false);

const showInterview = ref(false);

const selectedApplicant = ref(null);

// Load Dashboard

async function loadDashboard() {
  try {
    const data = await getDashboard();

    if (data.jobs !== undefined) {
      companyExists.value = true;

      dashboard.value = data;

      await loadJobs();
    } else {
      companyExists.value = false;

      message.value = data.message;
    }
  } catch (err) {
    message.value = "Please create company profile";
  } finally {
    loading.value = false;
  }
}

// Load Jobs

async function loadJobs() {
  const data = await getCompanyJobs();

  jobs.value = data.jobs || data;
}

// Create Drive

function createDrive() {
  router.push("/company/create-drive");
}

// View Applicants

async function viewApplicants(job) {
  selectedJob.value = job;

  const data = await getApplicants(job.id);

  applicants.value = data.applicants || data;
}

// Change Job Status

async function changeJobStatus(job) {
  let status = job.status === "active" ? "closed" : "active";

  await updateJobStatus(job.id, status);

  job.status = status;
}

// Shortlist

async function shortlist(app) {
  await shortlistApplicant(app.id);

  app.status = "shortlisted";
}

// Open Reject Modal

function openReject(app) {
  selectedApplicant.value = app;

  rejectReason.value = "";

  showReject.value = true;
}

// Reject

async function reject() {
  await rejectApplicant(selectedApplicant.value.id, rejectReason.value);

  selectedApplicant.value.status = "rejected";

  showReject.value = false;
}

// Select

async function select(app) {
  await selectApplicant(app.id);

  app.status = "selected";
}

// Open Interview

function openInterview(app) {
  selectedApplicant.value = app;

  showInterview.value = true;
}

// Schedule Interview

async function schedule() {
  await scheduleInterview(
    selectedApplicant.value.id,

    interviewData.value,
  );

  selectedApplicant.value.status = "interview scheduled";

  showInterview.value = false;
}

onMounted(loadDashboard);
</script>

<template>
  <div class="container mt-5">
    <h2>Company Dashboard</h2>

    <div class="mb-4">
      <p>
        <strong>Name:</strong>
        {{ user.name }}
      </p>

      <p>
        <strong>Email:</strong>
        {{ user.email }}
      </p>

      <p>
        <strong>Role:</strong>
        {{ user.role }}
      </p>
    </div>

    <div v-if="loading">Loading...</div>

    <div v-else>
      <div v-if="!companyExists" class="alert alert-warning">
        {{ message }}

        <RouterLink class="btn btn-primary ms-3" to="/company/register">
          Create Company
        </RouterLink>
      </div>

      <div v-else>
        <button class="btn btn-primary mb-4" @click="createDrive">
          + Create Drive
        </button>

        <!-- Dashboard Cards -->

        <div class="row g-3 mb-5">
          <div class="col-md-3">
            <div class="card p-3">
              <h5>Jobs</h5>

              <h2>
                {{ dashboard.jobs }}
              </h2>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card p-3">
              <h5>Applications</h5>

              <h2>
                {{ dashboard.applications }}
              </h2>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card p-3">
              <h5>Shortlisted</h5>

              <h2>
                {{ dashboard.shortlisted }}
              </h2>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card p-3">
              <h5>Selected</h5>

              <h2>
                {{ dashboard.selected }}
              </h2>
            </div>
          </div>
        </div>

        <!-- Jobs Table -->

        <h3>My Placement Drives</h3>

        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Title</th>

              <th>Location</th>

              <th>Salary</th>

              <th>Status</th>

              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="job in jobs" :key="job.id">
              <td>
                {{ job.job_title }}
              </td>

              <td>
                {{ job.location }}
              </td>

              <td>
                {{ job.salary_package }}
              </td>

              <td>
                <span class="badge bg-success" v-if="job.status === 'active'">
                  Active
                </span>

                <span class="badge bg-danger" v-else> Closed </span>
              </td>

              <td>
                <button
                  class="btn btn-info btn-sm"
                  @click="viewApplicants(job)"
                >
                  Applicants
                </button>

                <button
                  class="btn btn-warning btn-sm ms-2"
                  @click="changeJobStatus(job)"
                >
                  {{ job.status === "active" ? "Close" : "Activate" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Applicants -->

        <div v-if="selectedJob">
          <h3 class="mt-5">
            Applicants :
            {{ selectedJob.job_title }}
          </h3>

          <table class="table table-striped">
            <thead>
              <tr>
                <th>Name</th>

                <th>Email</th>

                <th>Status</th>

                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="app in applicants" :key="app.id">
                <td>
                  {{ app.student_name }}
                </td>

                <td>
                  {{ app.email }}
                </td>

                <td>
                  {{ app.status }}
                </td>

                <td>
                  <button
                    class="btn btn-success btn-sm"
                    @click="shortlist(app)"
                  >
                    Shortlist
                  </button>

                  <button
                    class="btn btn-danger btn-sm ms-2"
                    @click="openReject(app)"
                  >
                    Reject
                  </button>

                  <button
                    class="btn btn-info btn-sm ms-2"
                    @click="openInterview(app)"
                  >
                    Interview
                  </button>

                  <button
                    class="btn btn-primary btn-sm ms-2"
                    @click="select(app)"
                  >
                    Select
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Reject Modal -->

        <div v-if="showReject" class="card p-4 mt-3">
          <h4>Reject Applicant</h4>

          <textarea
            class="form-control"
            v-model="rejectReason"
            placeholder="Feedback"
          >
          </textarea>

          <button class="btn btn-danger mt-3" @click="reject">Reject</button>
        </div>

        <!-- Interview Modal -->

        <div v-if="showInterview" class="card p-4 mt-3">
          <h4>Schedule Interview</h4>

          <input
            type="date"
            class="form-control mb-2"
            v-model="interviewData.interview_date"
          />

          <input
            type="time"
            class="form-control mb-2"
            v-model="interviewData.interview_time"
          />

          <input
            class="form-control mb-2"
            placeholder="Meeting Link"
            v-model="interviewData.meeting_link"
          />

          <button class="btn btn-success" @click="schedule">Schedule</button>
        </div>
      </div>
    </div>
  </div>
</template>
