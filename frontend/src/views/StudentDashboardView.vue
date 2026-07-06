<!-- StudentPortal.vue -->
<script setup>
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import {
  browseJobs,
  getJobDetail,
  applyForJob,
  getMyApplications,
  getApplicationDetail,
  getMyInterviews,
  getInterviewDetail,
  downloadOfferLetter,
} from "./../services/student.service";

// ---------------- Tabs ----------------
const tabs = [
  { key: "jobs", label: "🔍 Browse Jobs" },
  { key: "applications", label: "📋 My Applications" },
  { key: "interviews", label: "🗓️ My Interviews" },
];
const activeTab = ref("jobs");
const router = useRouter();

// ---------------- Toast (lightweight feedback) ----------------
const toast = reactive({ show: false, message: "", type: "success" });
let toastTimer = null;
function notify(message, type = "success") {
  toast.message = message;
  toast.type = type;
  toast.show = true;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.show = false), 3000);
}

// =========================================================
// JOBS
// =========================================================
const jobFilters = reactive({ company: "", position: "", skill: "" });
const jobs = ref([]);
const jobsLoading = ref(false);
const jobsError = ref("");
const unauthorized = ref(false);
const unauthorizedMessage = ref("");

// job detail modal
const selectedJob = ref(null);
const jobDetailLoading = ref(false);
const applyingId = ref(null);

async function loadJobs() {
  jobsLoading.value = true;
  jobsError.value = "";
  unauthorized.value = false;
  unauthorizedMessage.value = "";
  try {
    const res = await browseJobs({
      company: jobFilters.company.trim(),
      position: jobFilters.position.trim(),
      skill: jobFilters.skill.trim(),
    });

    if (res?.message === "Unauthorized") {
      unauthorized.value = true;
      unauthorizedMessage.value =
        "Update Student Profile to access the dashboard.";
      jobs.value = [];
      return;
    }

    if (Array.isArray(res)) {
      jobs.value = res;
    } else if (Array.isArray(res?.jobs)) {
      jobs.value = res.jobs;
    } else if (res?.message) {
      jobsError.value = res.message;
      jobs.value = [];
    } else {
      jobs.value = [];
    }
  } catch (err) {
    jobsError.value = "Could not load job postings. Please try again.";
    jobs.value = [];
  } finally {
    jobsLoading.value = false;
  }
}

function resetJobFilters() {
  jobFilters.company = "";
  jobFilters.position = "";
  jobFilters.skill = "";
  loadJobs();
}
function updateStudentProfile() {
  console.log("here");
  router.push("/student/create-student");
}

async function openJobDetail(driveId) {
  jobDetailLoading.value = true;
  selectedJob.value = { loading: true };
  try {
    const res = await getJobDetail(driveId);
    selectedJob.value = res;
  } catch (err) {
    notify("Could not load job details.", "error");
    selectedJob.value = null;
  } finally {
    jobDetailLoading.value = false;
  }
}

function closeJobDetail() {
  selectedJob.value = null;
}

async function handleApply(driveId) {
  applyingId.value = driveId;
  try {
    const res = await applyForJob(driveId);
    if (res?.message && /already|error|fail/i.test(res.message)) {
      notify(res.message, "error");
    } else {
      notify("Application submitted successfully.");
      // reflect applied state locally without a full reload
      const job = jobs.value.find((j) => (j.id ?? j.drive_id) === driveId);
      if (job) job.already_applied = true;
      if (
        selectedJob.value &&
        (selectedJob.value.id ?? selectedJob.value.drive_id) === driveId
      ) {
        selectedJob.value.already_applied = true;
      }
    }
  } catch (err) {
    notify("Failed to submit application.", "error");
  } finally {
    applyingId.value = null;
  }
}

// =========================================================
// APPLICATIONS
// =========================================================
const applicationStatuses = [
  { value: "", label: "All" },
  { value: "applied", label: "Applied" },
  { value: "shortlisted", label: "Shortlisted" },
  { value: "interview scheduled", label: "Interview Scheduled" },
  { value: "selected", label: "Selected" },
  { value: "rejected", label: "Rejected" },
];
const applicationStatusFilter = ref("");
const applications = ref([]);
const applicationsLoading = ref(false);
const applicationsError = ref("");

const selectedApplication = ref(null);
const applicationDetailLoading = ref(false);
const offerDownloadingId = ref(null);

async function loadApplications() {
  applicationsLoading.value = true;
  applicationsError.value = "";
  try {
    const res = await getMyApplications(applicationStatusFilter.value);
    applications.value = Array.isArray(res)
      ? res
      : Array.isArray(res?.applications)
        ? res.applications
        : [];
    if (!Array.isArray(res) && res?.message && !res?.applications) {
      applicationsError.value = res.message;
    }
  } catch (err) {
    applicationsError.value = "Could not load your applications.";
    applications.value = [];
  } finally {
    applicationsLoading.value = false;
  }
}

async function openApplicationDetail(id) {
  applicationDetailLoading.value = true;
  selectedApplication.value = { loading: true };
  try {
    const res = await getApplicationDetail(id);
    selectedApplication.value = res;
  } catch (err) {
    notify("Could not load application details.", "error");
    selectedApplication.value = null;
  } finally {
    applicationDetailLoading.value = false;
  }
}

function closeApplicationDetail() {
  selectedApplication.value = null;
}

function statusClass(status) {
  const s = (status || "").toLowerCase();
  if (s === "selected") return "status-selected";
  if (s === "rejected") return "status-rejected";
  if (s === "interview scheduled") return "status-interview";
  if (s === "shortlisted") return "status-shortlisted";
  return "status-applied";
}

function canDownloadOffer(status) {
  const s = (status || "").toLowerCase();
  return s === "selected" || s === "placed";
}

async function handleDownloadOffer(applicationId) {
  console.log(applicationId);
  offerDownloadingId.value = applicationId;
  try {
    const res = await downloadOfferLetter(applicationId);
    if (res?.error) {
      notify(res.message || "Offer letter is not available yet.", "error");
    } else {
      notify("Offer letter downloaded.");
    }
  } catch (err) {
    notify("Failed to download offer letter.", "error");
  } finally {
    offerDownloadingId.value = null;
  }
}

watch(applicationStatusFilter, loadApplications);

// =========================================================
// INTERVIEWS
// =========================================================
const interviews = ref([]);
const interviewsLoading = ref(false);
const interviewsError = ref("");

const selectedInterview = ref(null);
const interviewDetailLoading = ref(false);

async function loadInterviews() {
  interviewsLoading.value = true;
  interviewsError.value = "";
  try {
    const res = await getMyInterviews();
    interviews.value = Array.isArray(res)
      ? res
      : Array.isArray(res?.interviews)
        ? res.interviews
        : [];
    if (!Array.isArray(res) && res?.message && !res?.interviews) {
      interviewsError.value = res.message;
    }
  } catch (err) {
    interviewsError.value = "Could not load your interviews.";
    interviews.value = [];
  } finally {
    interviewsLoading.value = false;
  }
}

async function openInterviewDetail(id) {
  interviewDetailLoading.value = true;
  selectedInterview.value = { loading: true };
  try {
    const res = await getInterviewDetail(id);
    selectedInterview.value = res;
  } catch (err) {
    notify("Could not load interview details.", "error");
    selectedInterview.value = null;
  } finally {
    interviewDetailLoading.value = false;
  }
}

function closeInterviewDetail() {
  selectedInterview.value = null;
}

function formatDateTime(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (isNaN(d.getTime())) return value;
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, { dateStyle: "medium" });
}

function formatSalary(value) {
  if (value === null || value === undefined || value === "") return "";
  return `${value} LPA`;
}

// ---------------- Tab switching loads data lazily ----------------
const loadedTabs = reactive({
  jobs: false,
  applications: false,
  interviews: false,
});

watch(activeTab, (tab) => {
  if (tab === "jobs" && !loadedTabs.jobs) {
    loadedTabs.jobs = true;
    loadJobs();
  }
  if (tab === "applications" && !loadedTabs.applications) {
    loadedTabs.applications = true;
    loadApplications();
  }
  if (tab === "interviews" && !loadedTabs.interviews) {
    loadedTabs.interviews = true;
    loadInterviews();
  }
});

onMounted(() => {
  loadedTabs.jobs = true;
  loadJobs();
});
</script>

<template>
  <!-- Show this when student profile does not exist -->
  <div v-if="unauthorized" class="register-gate">
    <div class="register-card">
      <div class="brand">
        <span class="brand-mark">&lt;/&gt;</span>
        <span class="brand-name">Placement Portal</span>
      </div>
      <h2>Update Student Profile</h2>
      <p>{{ unauthorizedMessage }}</p>

      <button class="btn-primary" @click="updateStudentProfile">
        Update Student Profile
      </button>
    </div>
  </div>
  <template v-else>
    <div class="container">
      <div class="header">
        <div>
          <h1>Placement Portal</h1>
          <p class="subtitle">
            Search jobs, track applications, and manage interviews — all in one
            place.
          </p>
        </div>
      </div>
      <!-- Tab Nav -->
      <div class="tab-nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- ================= JOBS TAB ================= -->
      <section v-if="activeTab === 'jobs'" class="tab-panel">
        <div class="filter-bar">
          <input
            v-model="jobFilters.company"
            placeholder="Company"
            @keyup.enter="loadJobs"
          />
          <input
            v-model="jobFilters.position"
            placeholder="Position"
            @keyup.enter="loadJobs"
          />
          <input
            v-model="jobFilters.skill"
            placeholder="Skill"
            @keyup.enter="loadJobs"
          />
          <button class="btn-primary" @click="loadJobs">Search</button>
          <button class="btn-ghost" @click="resetJobFilters">Reset</button>
        </div>

        <div v-if="jobsLoading" class="list-grid">
          <div v-for="n in 4" :key="n" class="list-card skeleton-card">
            <div class="skeleton-line long"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line long"></div>
          </div>
        </div>
        <div v-else-if="jobsError" class="state-msg error">{{ jobsError }}</div>
        <div v-else-if="jobs.length === 0" class="empty-state">
          <p class="empty-title">No job postings match your search</p>
          <p class="empty-sub">Try clearing filters or checking back later.</p>
        </div>

        <div v-else class="list-grid">
          <div
            v-for="job in jobs"
            :key="job.id ?? job.drive_id"
            class="list-card"
          >
            <div class="list-card-top">
              <div>
                <div class="list-title">
                  {{ job.job_title || job.position || job.role }}
                </div>
                <div class="list-subtitle">
                  {{ job.company_name || job.company }}
                </div>
              </div>
              <span v-if="job.salary ?? job.package ?? job.ctc" class="chip">
                {{ formatSalary(job.salary) || job.package || job.ctc }}
              </span>
            </div>

            <div class="meta-row">
              <span v-if="job.location">📍 {{ job.location }}</span>
              <span v-if="job.eligibility_branch"
                >🎓 {{ job.eligibility_branch }}</span
              >
              <span v-if="job.eligible_year">🗓️ {{ job.eligible_year }}</span>
              <span v-if="job.min_cgpa != null"
                >📊 Min CGPA {{ job.min_cgpa }}</span
              >
            </div>

            <div v-if="job.deadline" class="deadline-note">
              Apply by {{ formatDate(job.deadline) }}
            </div>

            <div v-if="job.skills" class="skills-box small">
              <span
                v-for="skill in String(job.skills).split(',')"
                :key="skill"
                class="skill-tag"
              >
                {{ skill.trim() }}
              </span>
            </div>

            <div class="list-card-actions">
              <button
                class="btn-ghost"
                @click="openJobDetail(job.id ?? job.drive_id)"
              >
                View Details
              </button>
              <button
                class="btn-primary"
                :disabled="
                  job.already_applied || applyingId === (job.id ?? job.drive_id)
                "
                @click="handleApply(job.id ?? job.drive_id)"
              >
                <span
                  v-if="applyingId === (job.id ?? job.drive_id)"
                  class="spinner"
                  aria-hidden="true"
                ></span>
                {{
                  job.already_applied
                    ? "Applied"
                    : applyingId === (job.id ?? job.drive_id)
                      ? ""
                      : "Apply"
                }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= APPLICATIONS TAB ================= -->
      <section v-if="activeTab === 'applications'" class="tab-panel">
        <div class="filter-bar">
          <select v-model="applicationStatusFilter">
            <option
              v-for="s in applicationStatuses"
              :key="s.value"
              :value="s.value"
            >
              {{ s.label }}
            </option>
          </select>
          <button class="btn-ghost" @click="loadApplications">Refresh</button>
        </div>

        <div v-if="applicationsLoading" class="list-grid">
          <div v-for="n in 4" :key="n" class="list-card skeleton-card">
            <div class="skeleton-line long"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line long"></div>
          </div>
        </div>
        <div v-else-if="applicationsError" class="state-msg error">
          {{ applicationsError }}
        </div>
        <div v-else-if="applications.length === 0" class="empty-state">
          <p class="empty-title">You haven't applied to any jobs yet</p>
          <p class="empty-sub">
            Browse open drives and apply — your applications will show up here.
          </p>
        </div>

        <div v-else class="list-grid">
          <div
            v-for="app in applications"
            :key="app.application_id || app.id"
            class="list-card"
          >
            <div class="list-card-top">
              <div>
                <div class="list-title">
                  {{ app.job_title || app.position || app.role }}
                </div>
                <div class="list-subtitle">
                  {{ app.company_name || app.company }}
                </div>
              </div>
              <span class="badge-status" :class="statusClass(app.status)">
                {{ app.status }}
              </span>
            </div>

            <div class="meta-row">
              <span v-if="app.location">📍 {{ app.location }}</span>
              <span v-if="app.salary">💰 {{ app.salary }} LPA</span>
              <span v-if="app.applied_at">
                📅 {{ formatDate(app.applied_at) }}
              </span>
            </div>

            <div class="list-card-actions">
              <button
                class="btn-ghost"
                @click="openApplicationDetail(app.application_id)"
              >
                View Details
              </button>
              <button
                v-if="canDownloadOffer(app.status)"
                class="btn-primary"
                :disabled="offerDownloadingId === app.application_id"
                @click="handleDownloadOffer(app.application_id)"
              >
                <span
                  v-if="offerDownloadingId === app.application_id"
                  class="spinner"
                  aria-hidden="true"
                ></span>
                {{
                  offerDownloadingId === app.application_id
                    ? ""
                    : "📄 Offer Letter"
                }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= INTERVIEWS TAB ================= -->
      <section v-if="activeTab === 'interviews'" class="tab-panel">
        <div class="filter-bar">
          <button class="btn-ghost" @click="loadInterviews">Refresh</button>
        </div>

        <div v-if="interviewsLoading" class="list-grid">
          <div v-for="n in 4" :key="n" class="list-card skeleton-card">
            <div class="skeleton-line long"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line long"></div>
          </div>
        </div>
        <div v-else-if="interviewsError" class="state-msg error">
          {{ interviewsError }}
        </div>
        <div v-else-if="interviews.length === 0" class="empty-state">
          <p class="empty-title">No interviews scheduled yet</p>
          <p class="empty-sub">
            Once a company schedules an interview, it'll appear here.
          </p>
        </div>

        <div v-else class="list-grid">
          <div
            v-for="iv in interviews"
            :key="iv.interview_id"
            class="list-card"
            @click="openInterviewDetail(iv.interview_id)"
          >
            <div class="list-card-top">
              <div>
                <div class="list-title">
                  {{ iv.job_title }}
                </div>

                <div class="list-subtitle">
                  {{ iv.company_name }}
                </div>
              </div>

              <span class="chip">
                {{ iv.mode }}
              </span>
            </div>

            <div class="meta-row">
              <span>📅 {{ formatDateTime(iv.interview_date) }}</span>
            </div>

            <div class="meta-row">
              <span>📌 {{ iv.status }}</span>
            </div>

            <div v-if="iv.meeting_link" class="meta-row">
              <p>{{ iv.meeting_link }}</p>
            </div>

            <div v-if="iv.feedback" class="feedback-box">
              <strong>Feedback:</strong> {{ iv.feedback }}
            </div>
          </div>
        </div>
      </section>

      <!-- ================= JOB DETAIL MODAL ================= -->
      <div
        v-if="selectedJob"
        class="modal-overlay"
        @click.self="closeJobDetail"
      >
        <div class="modal">
          <button
            class="modal-close"
            @click="closeJobDetail"
            aria-label="Close"
          >
            ✕
          </button>
          <div
            v-if="jobDetailLoading || selectedJob.loading"
            class="detail-skeleton"
          >
            <div class="skeleton-line long"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line long"></div>
            <div class="skeleton-line long"></div>
          </div>
          <template v-else>
            <h2>
              {{
                selectedJob.job_title ||
                selectedJob.position ||
                selectedJob.role
              }}
            </h2>
            <p class="subtitle">
              {{ selectedJob.company_name || selectedJob.company }}
            </p>

            <div class="detail-grid">
              <div
                v-if="
                  selectedJob.salary ?? selectedJob.package ?? selectedJob.ctc
                "
                class="detail-row"
              >
                <span class="detail-label">Salary</span>
                <span>{{
                  formatSalary(selectedJob.salary) ||
                  selectedJob.package ||
                  selectedJob.ctc
                }}</span>
              </div>
              <div v-if="selectedJob.location" class="detail-row">
                <span class="detail-label">Location</span>
                <span>{{ selectedJob.location }}</span>
              </div>
              <div
                v-if="selectedJob.eligibility_branch || selectedJob.eligibility"
                class="detail-row"
              >
                <span class="detail-label">Eligible Branch</span>
                <span>{{
                  selectedJob.eligibility_branch || selectedJob.eligibility
                }}</span>
              </div>
              <div v-if="selectedJob.eligible_year" class="detail-row">
                <span class="detail-label">Eligible Year</span>
                <span>{{ selectedJob.eligible_year }}</span>
              </div>
              <div v-if="selectedJob.min_cgpa != null" class="detail-row">
                <span class="detail-label">Min CGPA</span>
                <span>{{ selectedJob.min_cgpa }}</span>
              </div>
              <div v-if="selectedJob.drive_date" class="detail-row">
                <span class="detail-label">Drive Date</span>
                <span>{{ formatDate(selectedJob.drive_date) }}</span>
              </div>
              <div v-if="selectedJob.deadline" class="detail-row">
                <span class="detail-label">Deadline</span>
                <span>{{ formatDate(selectedJob.deadline) }}</span>
              </div>
            </div>

            <div v-if="selectedJob.skills" class="skills-box">
              <span
                v-for="skill in String(selectedJob.skills).split(',')"
                :key="skill"
                class="skill-tag"
              >
                {{ skill.trim() }}
              </span>
            </div>

            <p v-if="selectedJob.description" class="description">
              {{ selectedJob.description }}
            </p>

            <button
              class="btn-primary full-width"
              :disabled="
                selectedJob.already_applied ||
                applyingId === (selectedJob.id ?? selectedJob.drive_id)
              "
              @click="handleApply(selectedJob.id ?? selectedJob.drive_id)"
            >
              <span
                v-if="applyingId === (selectedJob.id ?? selectedJob.drive_id)"
                class="spinner spinner-dark"
                aria-hidden="true"
              ></span>
              {{
                selectedJob.already_applied
                  ? "Applied"
                  : applyingId === (selectedJob.id ?? selectedJob.drive_id)
                    ? ""
                    : "Apply Now"
              }}
            </button>
          </template>
        </div>
      </div>

      <!-- ================= APPLICATION DETAIL MODAL ================= -->
      <div
        v-if="selectedApplication"
        class="modal-overlay"
        @click.self="closeApplicationDetail"
      >
        <div class="modal">
          <button
            class="modal-close"
            @click="closeApplicationDetail"
            aria-label="Close"
          >
            ✕
          </button>
          <div
            v-if="applicationDetailLoading || selectedApplication.loading"
            class="detail-skeleton"
          >
            <div class="skeleton-line long"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line long"></div>
          </div>
          <template v-else>
            <h2>{{ selectedApplication.job_title }}</h2>

            <p class="subtitle">
              {{ selectedApplication.company_name }}
            </p>

            <div class="detail-grid">
              <div class="detail-row">
                <span class="detail-label">Status</span>
                <span
                  class="badge-status"
                  :class="statusClass(selectedApplication.status)"
                >
                  {{ selectedApplication.status }}
                </span>
              </div>

              <div class="detail-row">
                <span class="detail-label">Location</span>
                <span>{{ selectedApplication.location }}</span>
              </div>

              <div class="detail-row">
                <span class="detail-label">Salary</span>
                <span>{{ selectedApplication.salary }} LPA</span>
              </div>

              <div class="detail-row">
                <span class="detail-label">Applied On</span>
                <span>{{
                  formatDateTime(selectedApplication.applied_at)
                }}</span>
              </div>
            </div>

            <div class="description">
              <strong>Job Description</strong>
              <p>{{ selectedApplication.job_description }}</p>
            </div>

            <div v-if="selectedApplication.remarks" class="feedback-box">
              <strong>Remarks:</strong>
              {{ selectedApplication.remarks }}
            </div>

            <button
              v-if="canDownloadOffer(selectedApplication.status)"
              class="btn-primary full-width"
              :disabled="
                offerDownloadingId === selectedApplication.application_id
              "
              @click="handleDownloadOffer(selectedApplication.application_id)"
            >
              <span
                v-if="offerDownloadingId === selectedApplication.application_id"
                class="spinner spinner-dark"
                aria-hidden="true"
              ></span>
              {{
                offerDownloadingId === selectedApplication.application_id
                  ? ""
                  : "📄 Download Offer Letter"
              }}
            </button>
          </template>
        </div>
      </div>

      <!-- ================= INTERVIEW DETAIL MODAL ================= -->
      <div
        v-if="selectedInterview"
        class="modal-overlay"
        @click.self="closeInterviewDetail"
      >
        <div class="modal">
          <button
            class="modal-close"
            @click="closeInterviewDetail"
            aria-label="Close"
          >
            ✕
          </button>
          <div
            v-if="interviewDetailLoading || selectedInterview.loading"
            class="detail-skeleton"
          >
            <div class="skeleton-line long"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line long"></div>
          </div>
          <template v-else>
            <h2>
              {{ selectedInterview.company || selectedInterview.position }}
            </h2>
            <p class="subtitle">
              {{
                formatDateTime(
                  selectedInterview.scheduled_at || selectedInterview.date,
                )
              }}
            </p>

            <div class="detail-grid">
              <div v-if="selectedInterview.round" class="detail-row">
                <span class="detail-label">Round</span>
                <span>{{ selectedInterview.round }}</span>
              </div>
              <div v-if="selectedInterview.mode" class="detail-row">
                <span class="detail-label">Mode</span>
                <span>{{ selectedInterview.mode }}</span>
              </div>
              <div v-if="selectedInterview.interviewer" class="detail-row">
                <span class="detail-label">Interviewer</span>
                <span>{{ selectedInterview.interviewer }}</span>
              </div>
              <div v-if="selectedInterview.status" class="detail-row">
                <span class="detail-label">Status</span>
                <span>{{ selectedInterview.status }}</span>
              </div>
            </div>

            <div v-if="selectedInterview.feedback" class="feedback-box">
              <strong>Feedback:</strong> {{ selectedInterview.feedback }}
            </div>
            <div v-else class="empty">No feedback shared yet.</div>
          </template>
        </div>
      </div>

      <!-- ================= TOAST ================= -->
      <transition name="fade">
        <div v-if="toast.show" class="toast" :class="toast.type">
          {{ toast.message }}
        </div>
      </transition>
    </div>
  </template>
</template>

<style scoped>
.container {
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
  --shadow-hover: 0 4px 16px rgba(13, 16, 33, 0.1);
  --transition: 180ms ease;

  max-width: 1040px;
  margin: 40px auto;
  padding: 0 20px 60px;
  font-family:
    "Inter",
    "Sora",
    "Space Grotesk",
    -apple-system,
    BlinkMacSystemFont,
    sans-serif;
  color: var(--black);
}

*:focus-visible {
  outline: 2px solid var(--green);
  outline-offset: 2px;
}

/* ---------------- Register gate ---------------- */
.register-gate {
  display: flex;
  justify-content: center;
  margin: 60px 20px;
  font-family:
    "Inter",
    "Sora",
    "Space Grotesk",
    -apple-system,
    BlinkMacSystemFont,
    sans-serif;
}

.register-card {
  width: 100%;
  max-width: 480px;
  background: #fff8e6;
  border: 1px solid #f4d78a;
  border-radius: 10px;
  padding: 32px;
  text-align: center;
}

.register-card .brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}
.register-card .brand-mark {
  color: #1f9e4f;
  font-family: monospace;
  font-weight: 700;
}
.register-card .brand-name {
  font-weight: 700;
  font-size: 13px;
  color: #92400e;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.register-card h2 {
  margin-bottom: 10px;
  color: #92400e;
}

.register-card p {
  color: #92400e;
  margin-bottom: 20px;
}

.header {
  margin-bottom: 20px;
}

h1 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--black);
}

h2 {
  font-size: 17px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--black);
}

.subtitle {
  color: var(--gray-600);
  font-size: 14px;
  margin: 0;
}

/* ---------------- Tabs ---------------- */
.tab-nav {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.tab-btn {
  background: none;
  border: none;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-600);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition:
    color var(--transition),
    border-color var(--transition);
  min-height: 44px;
}

.tab-btn:hover {
  color: var(--green-dark);
}

.tab-btn.active {
  color: var(--green-dark);
  border-bottom-color: var(--green);
}

/* ---------------- Filter bar ---------------- */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-bar input,
.filter-bar select {
  padding: 10px 12px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 13px;
  min-width: 150px;
  background: var(--gray-100);
  min-height: 44px;
  box-sizing: border-box;
  transition:
    border-color var(--transition),
    background var(--transition);
  font-family: inherit;
}
.filter-bar input:focus,
.filter-bar select:focus {
  border-color: var(--green);
  background: var(--white);
  outline: none;
}

/* ---------------- Buttons ---------------- */
button {
  font-family: inherit;
}

.btn-primary {
  padding: 10px 16px;
  background: var(--green);
  color: var(--black);
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition:
    background var(--transition),
    box-shadow var(--transition),
    transform var(--transition);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-primary:hover:not(:disabled) {
  background: var(--green-dark);
  box-shadow: var(--shadow-hover);
}
.btn-primary:active:not(:disabled) {
  transform: scale(0.97);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary.full-width {
  width: 100%;
  margin-top: 16px;
  padding: 12px;
}

.btn-ghost {
  padding: 10px 16px;
  background: var(--white);
  color: var(--black);
  border: 1.5px solid var(--gray-200);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition:
    border-color var(--transition),
    background var(--transition);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-ghost:hover {
  border-color: var(--green);
  background: var(--green-tint);
}

/* ---------------- Spinner ---------------- */
.spinner {
  width: 12px;
  height: 12px;
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

/* ---------------- States ---------------- */
.state-msg {
  text-align: center;
  color: var(--gray-600);
  font-size: 14px;
  padding: 40px 0;
}

.state-msg.error {
  color: var(--red);
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  border: 1px dashed var(--gray-200);
  border-radius: var(--radius);
}
.empty-title {
  font-weight: 700;
  font-size: 14px;
  margin: 0 0 6px;
  color: var(--black);
}
.empty-sub {
  font-size: 13px;
  color: var(--gray-600);
  margin: 0;
}

/* ---------------- List grid / cards ---------------- */
.list-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.list-card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition:
    box-shadow var(--transition),
    transform var(--transition);
}
.list-card:hover {
  box-shadow: var(--shadow-hover);
}

.list-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.list-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--black);
}

.list-subtitle {
  font-size: 13px;
  color: var(--gray-600);
  margin-top: 2px;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: var(--gray-600);
}

.deadline-note {
  font-size: 12px;
  font-weight: 600;
  color: #a3690f;
}

.chip {
  background: var(--gray-100);
  color: var(--gray-600);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.list-card-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.list-card-actions button {
  flex: 1;
}

/* ---------------- Skills ---------------- */
.skills-box {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skills-box.small .skill-tag {
  font-size: 11px;
  padding: 3px 10px;
}

.skill-tag {
  background: var(--green-tint);
  color: var(--green-dark);
  border: 1px solid #b7ecc9;
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 500;
}

/* ---------------- Status badges ---------------- */
.badge-status {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  text-transform: capitalize;
}

.status-applied {
  background: var(--gray-100);
  color: var(--gray-600);
}

.status-shortlisted {
  background: #fef6e0;
  color: #a3690f;
}

.status-interview {
  background: #f0eafd;
  color: #7c3aed;
}

.status-selected {
  background: var(--green-tint);
  color: var(--green-dark);
}

.status-rejected {
  background: var(--red-tint);
  color: var(--red);
}

/* ---------------- Feedback ---------------- */
.feedback-box {
  background: var(--gray-100);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
  color: var(--black);
}

.empty {
  color: var(--gray-400);
  font-size: 14px;
}

/* ---------------- Skeletons ---------------- */
.skeleton-card {
  gap: 10px;
}
.skeleton-line {
  height: 12px;
  border-radius: 4px;
  background: linear-gradient(
    90deg,
    var(--gray-100) 25%,
    var(--gray-200) 37%,
    var(--gray-100) 63%
  );
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}
.skeleton-line.short {
  width: 60px;
}
.skeleton-line.long {
  width: 70%;
}
.detail-skeleton {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 10px 0;
}
@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

/* ---------------- Modal ---------------- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(13, 16, 33, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
  animation: fadeIn 180ms ease;
}
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal {
  background: var(--white);
  border-radius: 12px;
  padding: 28px;
  max-width: 520px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
  box-shadow: var(--shadow-hover);
}

.modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  background: none;
  border: none;
  font-size: 16px;
  color: var(--gray-400);
  cursor: pointer;
  min-height: auto;
  padding: 4px 8px;
}

.modal-close:hover {
  color: var(--black);
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 16px 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  border-bottom: 1px solid var(--gray-100);
  padding-bottom: 8px;
}

.detail-label {
  color: var(--gray-600);
  font-weight: 600;
}

.description {
  font-size: 14px;
  color: var(--black);
  line-height: 1.5;
  margin-top: 10px;
}

/* ---------------- Toast ---------------- */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--white);
  z-index: 200;
  box-shadow: var(--shadow-hover);
}

.toast.success {
  background: var(--green-dark);
}

.toast.error {
  background: var(--red);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ---------------- Responsive ---------------- */
@media (max-width: 640px) {
  .list-grid {
    grid-template-columns: 1fr;
  }

  .filter-bar input,
  .filter-bar select {
    flex: 1;
    min-width: 120px;
  }
}
</style>
