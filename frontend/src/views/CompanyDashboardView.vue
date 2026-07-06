<script setup>
import { ref, reactive, onMounted } from "vue";
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

// ---------------- Top-level state ----------------
const loading = ref(true);

// Company profile / approval gating
const companyExists = ref(false);
const approvalStatus = ref(""); // "pending" | "approved" | "rejected" | "blacklisted" | ""
const message = ref("");

const dashboard = ref({});
const jobs = ref([]);

// ---------------- Toast ----------------
const toast = reactive({ show: false, message: "", type: "success" });
let toastTimer = null;
function notify(msg, type = "success") {
  toast.message = msg;
  toast.type = type;
  toast.show = true;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.show = false), 3000);
}

// ---------------- Applicants ----------------
const selectedJob = ref(null);
const applicants = ref([]);
const applicantsLoading = ref(false);

// Track which applicant/job row currently has an action in flight, so we
// can disable just that row's buttons instead of the whole page.
// NOTE: applicants only have `application_id` / `student_id` from the API
// (no bare `id` field) — always key/compare on application_id.
const busyApplicantId = ref(null);
const busyJobId = ref(null);

// Review modal (read-only profile view)
const showReview = ref(false);

// Reject modal
const showReject = ref(false);
const rejectReason = ref("");
const rejecting = ref(false);

// Interview modal
const showInterview = ref(false);
const interviewData = reactive({
  interview_date: "",
  interview_time: "",
  meeting_link: "",
});
const scheduling = ref(false);

// Shared "which applicant is this modal about" ref
const selectedApplicant = ref(null);

// =========================================================
// COMPANY APPROVAL + DASHBOARD
// =========================================================

// The exact shape of getDashboard()'s response when a company profile is
// pending/rejected isn't fully pinned down, so this checks a few
// reasonable signals defensively rather than assuming one field name.
function isApprovedResponse(data) {
  if (data?.status && typeof data.status === "string") {
    return data.status.toLowerCase() === "approved";
  }
  if (typeof data?.approved === "boolean") return data.approved;
  // Fallback: presence of the jobs summary implies an active, approved dashboard
  return data?.jobs !== undefined;
}

function isPendingResponse(data) {
  if (data?.status && typeof data.status === "string") {
    return ["pending", "under_review", "unapproved"].includes(
      data.status.toLowerCase(),
    );
  }
  if (typeof data?.approved === "boolean" && !data.approved) return true;
  return /pending|not.*approv|awaiting/i.test(data?.message || "");
}

function isMissingProfileResponse(data) {
  return /create.*company|no company|not.*found|register/i.test(
    data?.message || "",
  );
}

// The backend rejects blacklisted companies with a 403 containing a
// "blacklisted" message — catch it both on a normal data payload and on
// a thrown error response, since we don't know which shape the
// company.service wrapper surfaces it as.
function isBlacklistedResponse(data) {
  if (typeof data?.blacklisted === "boolean") return data.blacklisted;
  return /blacklist/i.test(data?.message || "");
}

async function loadDashboard() {
  loading.value = true;
  try {
    const data = await getDashboard();

    if (isBlacklistedResponse(data)) {
      companyExists.value = true;
      approvalStatus.value = "blacklisted";
      message.value =
        data.message ||
        "Your company has been blacklisted. You no longer have access to the dashboard.";
    } else if (isApprovedResponse(data)) {
      companyExists.value = true;
      approvalStatus.value = "approved";
      dashboard.value = data;
      await loadJobs();
    } else if (isMissingProfileResponse(data)) {
      companyExists.value = false;
      approvalStatus.value = "";
      message.value = data.message || "Please create your company profile.";
    } else if (isPendingResponse(data)) {
      companyExists.value = true;
      approvalStatus.value =
        data.status?.toLowerCase() === "rejected" ? "rejected" : "pending";
      message.value =
        data.message ||
        (approvalStatus.value === "rejected"
          ? "Your company profile was not approved."
          : "Your company profile is awaiting admin approval.");
    } else {
      // Unrecognized shape — treat conservatively as "no profile" so the
      // person isn't stuck on a blank dashboard.
      companyExists.value = false;
      message.value = data?.message || "Please create your company profile.";
    }
  } catch (err) {
    const errData = err?.response?.data;
    if (isBlacklistedResponse(errData)) {
      companyExists.value = true;
      approvalStatus.value = "blacklisted";
      message.value =
        errData.message ||
        "Your company has been blacklisted. You no longer have access to the dashboard.";
    } else {
      companyExists.value = false;
      message.value = "Please create your company profile.";
    }
  } finally {
    loading.value = false;
  }
}

async function loadJobs() {
  try {
    const data = await getCompanyJobs();
    jobs.value = data.jobs || data || [];
  } catch (err) {
    notify("Could not load your placement drives.", "error");
  }
}

function createDrive() {
  router.push("/company/create-drive");
}

// =========================================================
// JOB STATUS
// =========================================================
async function changeJobStatus(job) {
  const nextStatus = job.status === "active" ? "closed" : "active";
  busyJobId.value = job.id;
  try {
    await updateJobStatus(job.id, nextStatus);
    job.status = nextStatus;
    notify(`Drive marked as ${nextStatus}.`);
  } catch (err) {
    notify("Could not update drive status.", "error");
  } finally {
    busyJobId.value = null;
  }
}

// =========================================================
// APPLICANTS
// =========================================================
async function viewApplicants(job) {
  selectedJob.value = job;
  applicants.value = [];
  applicantsLoading.value = true;
  try {
    const data = await getApplicants(job.id);
    applicants.value = data.applicants || data || [];
  } catch (err) {
    notify("Could not load applicants for this drive.", "error");
  } finally {
    applicantsLoading.value = false;
  }
}

function closeApplicants() {
  selectedJob.value = null;
  applicants.value = [];
}

function applicantStatus(app) {
  return (app.status || "applied").toLowerCase();
}

function statusClass(status) {
  const s = (status || "").toLowerCase();
  if (s === "selected") return "status-selected";
  if (s === "rejected") return "status-rejected";
  if (s === "interview scheduled") return "status-interview";
  if (s === "shortlisted") return "status-shortlisted";
  return "status-applied";
}

// Which actions make sense from the applicant's current status —
// keeps the table from offering actions that don't apply anymore
// (e.g. rejecting someone already selected).
function canShortlist(app) {
  return applicantStatus(app) === "applied";
}
function canReject(app) {
  return !["rejected", "selected"].includes(applicantStatus(app));
}
function canScheduleInterview(app) {
  return applicantStatus(app) === "shortlisted";
}
function canSelect(app) {
  return ["shortlisted", "interview scheduled"].includes(applicantStatus(app));
}
function hasNoFurtherAction(app) {
  return (
    !canShortlist(app) &&
    !canReject(app) &&
    !canScheduleInterview(app) &&
    !canSelect(app)
  );
}

// ---------------- Review ----------------
function openReview(app) {
  selectedApplicant.value = app;
  showReview.value = true;
}
function closeReview() {
  showReview.value = false;
  selectedApplicant.value = null;
}

// ---------------- Shortlist ----------------
async function shortlist(app) {
  // Backend returns `application_id`, not `id` — use that consistently.
  busyApplicantId.value = app.application_id;
  try {
    await shortlistApplicant(app.application_id);
    app.status = "shortlisted";
    notify(`${app.name || app.student_name || "Applicant"} shortlisted.`);
  } catch (err) {
    notify("Could not shortlist this applicant.", "error");
  } finally {
    busyApplicantId.value = null;
  }
}

// ---------------- Reject ----------------
function openReject(app) {
  selectedApplicant.value = app;
  rejectReason.value = "";
  showReject.value = true;
}

function closeReject() {
  showReject.value = false;
  selectedApplicant.value = null;
}

async function reject() {
  rejecting.value = true;
  try {
    await rejectApplicant(
      selectedApplicant.value.application_id,
      rejectReason.value,
    );
    selectedApplicant.value.status = "rejected";
    selectedApplicant.value.remarks = rejectReason.value;
    notify(
      `${selectedApplicant.value.name || selectedApplicant.value.student_name || "Applicant"} rejected.`,
    );
    showReject.value = false;
  } catch (err) {
    notify("Could not reject this applicant.", "error");
  } finally {
    rejecting.value = false;
  }
}

// ---------------- Select ----------------
async function select(app) {
  busyApplicantId.value = app.application_id;
  try {
    await selectApplicant(app.application_id);
    app.status = "selected";
    notify(`${app.name || app.student_name || "Applicant"} selected.`);
  } catch (err) {
    notify("Could not select this applicant.", "error");
  } finally {
    busyApplicantId.value = null;
  }
}

// ---------------- Interview ----------------
function openInterview(app) {
  selectedApplicant.value = app;
  interviewData.interview_date = "";
  interviewData.interview_time = "";
  interviewData.meeting_link = "";
  showInterview.value = true;
}

function closeInterview() {
  showInterview.value = false;
  selectedApplicant.value = null;
}

async function schedule() {
  if (!interviewData.interview_date || !interviewData.interview_time) {
    notify("Please pick a date and time for the interview.", "error");
    return;
  }
  if (interviewData.mode === "online" && !interviewData.meeting_link) {
    notify("Please add a meeting link for the online interview.", "error");
    return;
  }

  scheduling.value = true;
  try {
    const combinedDateTime = `${interviewData.interview_date}T${interviewData.interview_time}`;

    await scheduleInterview(selectedApplicant.value.application_id, {
      interview_date: combinedDateTime,
      mode: interviewData.mode,
      meeting_link:
        interviewData.mode === "online" ? interviewData.meeting_link : "",
    });

    selectedApplicant.value.status = "interview scheduled";
    notify(
      `Interview scheduled with ${
        selectedApplicant.value.name ||
        selectedApplicant.value.student_name ||
        "applicant"
      }.`,
    );
    showInterview.value = false;
  } catch (err) {
    notify("Could not schedule the interview.", "error");
  } finally {
    scheduling.value = false;
  }
}
// ---------------- Formatting helpers ----------------
function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, { dateStyle: "medium" });
}

function formatSalary(value) {
  if (value === null || value === undefined || value === "") return "—";
  return `${value} LPA`;
}

onMounted(loadDashboard);
</script>

<template>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div>
        <h1>Company Dashboard</h1>
        <p class="subtitle">{{ user?.name }} · {{ user?.email }}</p>
      </div>
      <button
        v-if="approvalStatus === 'approved'"
        class="btn-primary"
        @click="createDrive"
      >
        + Create Drive
      </button>
    </div>

    <!-- Loading skeleton instead of a bare text line -->
    <div v-if="loading" class="skeleton-stats">
      <div v-for="n in 4" :key="n" class="stat-card skeleton-card">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
      </div>
    </div>

    <template v-else>
      <!-- No company profile yet -->
      <div v-if="!companyExists" class="notice notice-warning">
        <p>{{ message }}</p>
        <RouterLink class="btn-primary" to="/company/register">
          Create Company Profile
        </RouterLink>
      </div>

      <!-- Blacklisted: no further actions available -->
      <div
        v-else-if="approvalStatus === 'blacklisted'"
        class="notice notice-blacklisted"
      >
        <strong>Account Blacklisted</strong>
        <p>{{ message }}</p>
        <p>
          You can no longer post drives, view applicants, or manage
          applications.
        </p>
      </div>

      <!-- Profile exists but not yet approved / was rejected -->
      <div
        v-else-if="approvalStatus !== 'approved'"
        class="notice"
        :class="approvalStatus === 'rejected' ? 'notice-danger' : 'notice-info'"
      >
        <strong>{{
          approvalStatus === "rejected"
            ? "Profile not approved"
            : "Approval pending"
        }}</strong>
        <p>{{ message }}</p>
        <p v-if="approvalStatus === 'pending'">
          You'll be able to post jobs and manage applicants once an admin
          approves your company profile.
        </p>
      </div>

      <!-- Approved: full dashboard -->
      <template v-else>
        <!-- Summary cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Jobs</div>
            <div class="stat-value">{{ dashboard.jobs ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Applications</div>
            <div class="stat-value">{{ dashboard.applications ?? 0 }}</div>
          </div>
          <div class="stat-card accent">
            <div class="stat-label">Shortlisted</div>
            <div class="stat-value">{{ dashboard.shortlisted ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Selected</div>
            <div class="stat-value">{{ dashboard.selected ?? 0 }}</div>
          </div>
        </div>

        <!-- Jobs -->
        <section class="panel">
          <div class="panel-header">
            <h2>My Placement Drives</h2>
            <span class="count-chip">{{ jobs.length }}</span>
          </div>

          <div v-if="jobs.length === 0" class="empty-state">
            <p class="empty-title">No placement drives yet</p>
            <p class="empty-sub">
              Create your first drive to start receiving applications.
            </p>
          </div>

          <div v-else class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Location</th>
                  <th>Salary</th>
                  <th>Experience</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="job in jobs" :key="job.id">
                  <td class="cell-title">{{ job.job_title }}</td>
                  <td>{{ job.location || "—" }}</td>
                  <td>{{ formatSalary(job.salary_package ?? job.salary) }}</td>
                  <td>
                    {{ job.experience || job.experience_required || "—" }}
                  </td>
                  <td>
                    <span
                      class="badge-status"
                      :class="
                        job.status === 'active'
                          ? 'status-selected'
                          : 'status-rejected'
                      "
                    >
                      {{ job.status === "active" ? "Active" : "Closed" }}
                    </span>
                  </td>
                  <td class="cell-actions">
                    <button
                      class="btn-ghost small"
                      @click="viewApplicants(job)"
                    >
                      Applicants
                    </button>
                    <button
                      class="btn-ghost small"
                      :disabled="busyJobId === job.id"
                      @click="changeJobStatus(job)"
                    >
                      <span
                        v-if="busyJobId === job.id"
                        class="spinner"
                        aria-hidden="true"
                      ></span>
                      {{
                        busyJobId === job.id
                          ? ""
                          : job.status === "active"
                            ? "Close"
                            : "Activate"
                      }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Applicants modal -->
        <div
          v-if="selectedJob"
          class="modal-overlay"
          @click.self="closeApplicants"
        >
          <div class="modal modal-wide">
            <button
              class="modal-close"
              @click="closeApplicants"
              aria-label="Close"
            >
              ✕
            </button>
            <h2>Applicants</h2>
            <p class="subtitle">{{ selectedJob.job_title }}</p>

            <div v-if="applicantsLoading" class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Remarks</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="n in 3" :key="n">
                    <td><div class="skeleton-line long"></div></td>
                    <td><div class="skeleton-line long"></div></td>
                    <td><div class="skeleton-line short"></div></td>
                    <td><div class="skeleton-line short"></div></td>
                    <td><div class="skeleton-line short"></div></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else-if="applicants.length === 0" class="empty-state">
              <p class="empty-title">No applicants yet</p>
              <p class="empty-sub">
                Students who apply to this drive will show up here.
              </p>
            </div>

            <div v-else class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Remarks</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in applicants" :key="app.application_id">
                    <td class="cell-title">
                      {{ app.name || app.student_name }}
                    </td>
                    <td>{{ app.email }}</td>
                    <td>
                      <span
                        class="badge-status"
                        :class="statusClass(app.status)"
                      >
                        {{ app.status || "Applied" }}
                      </span>
                    </td>
                    <td>{{ app.remarks || "—" }}</td>
                    <td class="cell-actions">
                      <button class="btn-ghost small" @click="openReview(app)">
                        Review
                      </button>

                      <button
                        v-if="canShortlist(app)"
                        class="btn-primary small"
                        :disabled="busyApplicantId === app.application_id"
                        @click="shortlist(app)"
                      >
                        <span
                          v-if="busyApplicantId === app.application_id"
                          class="spinner spinner-dark"
                          aria-hidden="true"
                        ></span>
                        {{
                          busyApplicantId === app.application_id
                            ? ""
                            : "Shortlist"
                        }}
                      </button>

                      <button
                        v-if="canReject(app)"
                        class="btn-danger small"
                        @click="openReject(app)"
                      >
                        Reject
                      </button>

                      <button
                        v-if="canScheduleInterview(app)"
                        class="btn-ghost small"
                        @click="openInterview(app)"
                      >
                        Interview
                      </button>

                      <button
                        v-if="canSelect(app)"
                        class="btn-primary small"
                        :disabled="busyApplicantId === app.application_id"
                        @click="select(app)"
                      >
                        <span
                          v-if="busyApplicantId === app.application_id"
                          class="spinner spinner-dark"
                          aria-hidden="true"
                        ></span>
                        {{
                          busyApplicantId === app.application_id ? "" : "Select"
                        }}
                      </button>

                      <span v-if="hasNoFurtherAction(app)" class="empty-note">
                        No further action
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Review modal (read-only applicant profile) -->
        <div v-if="showReview" class="modal-overlay" @click.self="closeReview">
          <div class="modal">
            <button class="modal-close" @click="closeReview" aria-label="Close">
              ✕
            </button>
            <h2>
              {{ selectedApplicant?.name || selectedApplicant?.student_name }}
            </h2>
            <p class="subtitle">{{ selectedApplicant?.email }}</p>

            <div class="detail-grid">
              <div class="detail-row">
                <span class="detail-label">Status</span>
                <span
                  class="badge-status"
                  :class="statusClass(selectedApplicant?.status)"
                >
                  {{ selectedApplicant?.status || "Applied" }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Branch</span>
                <span>{{ selectedApplicant?.branch || "—" }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">CGPA</span>
                <span>{{ selectedApplicant?.cgpa ?? "—" }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Skills</span>
                <span>{{ selectedApplicant?.skills || "—" }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Resume</span>
                <span>
                  <a
                    v-if="selectedApplicant?.resume"
                    :href="selectedApplicant.resume"
                    target="_blank"
                    rel="noopener"
                    class="link"
                  >
                    View Resume
                  </a>
                  <template v-else>—</template>
                </span>
              </div>
            </div>

            <p v-if="selectedApplicant?.remarks" class="description">
              <strong>Remarks:</strong> {{ selectedApplicant.remarks }}
            </p>

            <button class="btn-ghost full-width" @click="closeReview">
              Close
            </button>
          </div>
        </div>

        <!-- Reject modal -->
        <div v-if="showReject" class="modal-overlay" @click.self="closeReject">
          <div class="modal">
            <button class="modal-close" @click="closeReject" aria-label="Close">
              ✕
            </button>
            <h2>
              Reject
              {{ selectedApplicant?.name || selectedApplicant?.student_name }}
            </h2>

            <textarea
              class="textarea"
              v-model="rejectReason"
              placeholder="Feedback for the applicant (optional)"
              rows="4"
            ></textarea>

            <div class="modal-actions">
              <button class="btn-danger" :disabled="rejecting" @click="reject">
                <span
                  v-if="rejecting"
                  class="spinner"
                  aria-hidden="true"
                ></span>
                {{ rejecting ? "Rejecting" : "Reject" }}
              </button>
              <button class="btn-ghost" @click="closeReject">Cancel</button>
            </div>
          </div>
        </div>

        <!-- Interview modal -->
        <div
          v-if="showInterview"
          class="modal-overlay"
          @click.self="closeInterview"
        >
          <div class="modal">
            <button
              class="modal-close"
              @click="closeInterview"
              aria-label="Close"
            >
              ✕
            </button>
            <h2>Schedule Interview</h2>
            <p class="subtitle">
              {{ selectedApplicant?.name || selectedApplicant?.student_name }}
            </p>

            <div class="form-field">
              <label>Date</label>
              <input type="date" v-model="interviewData.interview_date" />
            </div>
            <div class="form-field">
              <label>Time</label>
              <input type="time" v-model="interviewData.interview_time" />
            </div>
            <div class="form-field">
              <label>Mode</label>
              <select v-model="interviewData.mode" class="textarea">
                <option value="online">Online</option>
                <option value="offline">Offline</option>
              </select>
            </div>
            <div class="form-field" v-if="interviewData.mode === 'online'">
              <label>Meeting Link</label>
              <input
                type="text"
                placeholder="https://..."
                v-model="interviewData.meeting_link"
              />
            </div>

            <div class="modal-actions">
              <button
                class="btn-primary"
                :disabled="scheduling"
                @click="schedule"
              >
                <span
                  v-if="scheduling"
                  class="spinner spinner-dark"
                  aria-hidden="true"
                ></span>
                {{ scheduling ? "Scheduling" : "Schedule" }}
              </button>
              <button class="btn-ghost" @click="closeInterview">Cancel</button>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast.show" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </transition>
  </div>
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

  max-width: 1080px;
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 28px;
  flex-wrap: wrap;
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

/* ---------------- Buttons ---------------- */
button,
.btn-primary,
.btn-ghost,
.btn-danger {
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
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 44px;
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

.btn-primary.small {
  padding: 6px 12px;
  font-size: 12px;
  min-height: 34px;
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
  gap: 6px;
}

.btn-ghost:hover:not(:disabled) {
  border-color: var(--green);
  background: var(--green-tint);
}

.btn-ghost:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-ghost.small {
  padding: 6px 12px;
  font-size: 12px;
  min-height: 34px;
}

.btn-ghost.full-width {
  width: 100%;
  margin-top: 16px;
  padding: 12px;
}

.btn-danger {
  padding: 10px 16px;
  background: var(--white);
  color: var(--red);
  border: 1.5px solid var(--red-tint);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 44px;
}

.btn-danger:hover:not(:disabled) {
  background: var(--red-tint);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger.small {
  padding: 6px 12px;
  font-size: 12px;
  min-height: 34px;
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
.spinner-dark {
  border-color: var(--black);
  border-right-color: transparent;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ---------------- Notices ---------------- */
.notice {
  border-radius: var(--radius);
  padding: 18px 20px;
  font-size: 14px;
  line-height: 1.5;
}

.notice p {
  margin: 6px 0 0;
}

.notice .btn-primary {
  margin-top: 12px;
}

.notice-warning {
  background: #fff8e6;
  border: 1px solid #f4d78a;
  color: #92400e;
}

.notice-info {
  background: var(--green-tint);
  border: 1px solid #b7ecc9;
  color: var(--green-dark);
}

.notice-danger {
  background: var(--red-tint);
  border: 1px solid #f5b5b7;
  color: #991b1b;
}

.notice-blacklisted {
  background: var(--black);
  border: 1px solid var(--black);
  color: var(--white);
}

.notice-blacklisted strong {
  color: #f87171;
}

/* ---------------- Stats ---------------- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 32px;
}

.skeleton-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  padding: 18px;
  transition:
    box-shadow var(--transition),
    transform var(--transition);
}
.stat-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}
.stat-card.accent {
  border-color: var(--green);
  background: var(--green-tint);
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-600);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--black);
}

.skeleton-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ---------------- Panels ---------------- */
.panel {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 24px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.panel-header h2 {
  margin: 0;
}
.count-chip {
  background: var(--gray-100);
  color: var(--gray-600);
  font-size: 12px;
  font-weight: 600;
  padding: 2px 9px;
  border-radius: 999px;
}

/* ---------------- Empty state ---------------- */
.empty-state {
  text-align: center;
  padding: 48px 24px;
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

.empty-note {
  color: var(--gray-400);
  font-size: 12px;
  align-self: center;
}

/* ---------------- Skeleton shimmer ---------------- */
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
  width: 140px;
}
@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

/* ---------------- Table ---------------- */
.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 640px;
}

.data-table th {
  text-align: left;
  padding: 10px 12px;
  color: var(--gray-600);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  border-bottom: 1px solid var(--gray-200);
  white-space: nowrap;
  background: var(--gray-100);
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid var(--gray-100);
  vertical-align: middle;
}

.data-table tbody tr {
  transition: background var(--transition);
}
.data-table tbody tr:hover {
  background: var(--gray-100);
}
.data-table tbody tr:last-child td {
  border-bottom: none;
}

.cell-title {
  font-weight: 600;
  color: var(--black);
}

.cell-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

/* ---------------- Status badges ---------------- */
.badge-status {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  text-transform: capitalize;
  display: inline-block;
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

.modal-wide {
  max-width: 820px;
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

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 18px;
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
  align-items: center;
  font-size: 14px;
  border-bottom: 1px solid var(--gray-100);
  padding-bottom: 8px;
}

.detail-label {
  color: var(--gray-600);
  font-weight: 600;
}

.link {
  color: var(--green-dark);
  font-weight: 600;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.description {
  font-size: 14px;
  color: var(--black);
  line-height: 1.5;
  margin-top: 10px;
}

/* ---------------- Form fields ---------------- */
.form-field {
  margin-bottom: 12px;
}

.form-field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-600);
  margin-bottom: 6px;
}

.form-field input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 13px;
  box-sizing: border-box;
  background: var(--gray-100);
  transition:
    border-color var(--transition),
    background var(--transition);
}
.form-field input:focus {
  border-color: var(--green);
  background: var(--white);
  outline: none;
}

.textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  box-sizing: border-box;
  resize: vertical;
  background: var(--gray-100);
  transition:
    border-color var(--transition),
    background var(--transition);
}
.textarea:focus {
  border-color: var(--green);
  background: var(--white);
  outline: none;
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
@media (max-width: 720px) {
  .stats-grid,
  .skeleton-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-grid,
  .skeleton-stats {
    grid-template-columns: 1fr;
  }
  .cell-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .cell-actions button {
    width: 100%;
  }
}
</style>
