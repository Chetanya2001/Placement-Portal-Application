<script setup>
import { ref, onMounted, computed } from "vue";

import {
  getApplications,
  getCompanies,
  getDashboard,
  getDrives,
  getStudents,
  approveCompany,
  approveDrive,
  blacklistCompany,
  deleteDrive,
  studentDeactivate,
  searchCompany,
  searchStudent,
  rejectCompany,
  getApplicationDetail,
  getStudentProfile,
} from "../services/admin.service";
const user = JSON.parse(localStorage.getItem("user"));

const dashboard = ref({});
const companies = ref([]);
const drives = ref([]);
const applications = ref([]);
const selectedApplication = ref(null);
const selectedStudent = ref(null);
const searchText = ref("");
const searchedCompanies = ref([]);
const searchedStudents = ref([]);

// --- Added UX-only state (does not change any existing data/logic) ---
const isLoading = ref(true); // true on first load, drives the skeleton state
const loadError = ref(null); // populated if loadData() throws
const isSearching = ref(false); // spinner on the Search button
const actionInFlight = ref(null); // id currently processing, for per-row button spinners

// --- ADDED --- full students list (used by the "Students" stat-card modal)
const students = ref([]);

// --- ADDED --- state for the stat-card "list everything" modal
// type: 'students' | 'companies' | 'drives' | 'applications'
const activeListModal = ref(null);

// Handles either `blacklisted` or `is_blacklisted` coming back from the API,
// and shows that instead of the approval status once a company is blacklisted.
function companyStatus(company) {
  const isBlacklisted = company.blacklisted ?? company.is_blacklisted;
  if (isBlacklisted) return "Blacklisted";
  return company.approval_status;
}

function statusClass(company) {
  const isBlacklisted = company.blacklisted ?? company.is_blacklisted;
  if (isBlacklisted) return "status-blacklisted";
  if (company.approval_status === "approved") return "status-approved";
  if (company.approval_status === "rejected") return "status-rejected";
  return "status-pending";
}

// Generic status class helper for drive/application status strings
function genericStatusClass(status) {
  const s = (status || "").toString().toLowerCase();
  if (["approved", "selected", "open", "eligible", "active"].includes(s))
    return "status-approved";
  if (["rejected", "closed"].includes(s)) return "status-rejected";
  return "status-pending";
}

// --- ADDED --- opens the "list everything" modal for the clicked stat card
function openListModal(type) {
  activeListModal.value = type;
}

function closeListModal() {
  activeListModal.value = null;
}

const handleViewApplication = async (id) => {
  try {
    selectedApplication.value = await getApplicationDetail(id);
  } catch (err) {
    alert(err.message);
  }
};

const handleViewStudent = async (id) => {
  try {
    selectedStudent.value = await getStudentProfile(id);
  } catch (err) {
    alert(err.message);
  }
};
const loadData = async () => {
  isLoading.value = true;
  loadError.value = null;
  try {
    dashboard.value = await getDashboard();
    companies.value = await getCompanies();
    drives.value = await getDrives();
    applications.value = await getApplications();
    students.value = await getStudents(); // --- ADDED ---
  } catch (error) {
    console.log(error);
    loadError.value =
      error?.message || "Something went wrong while loading the dashboard.";
  } finally {
    isLoading.value = false;
  }
};

const handleSearch = async () => {
  if (!searchText.value.trim()) return;

  isSearching.value = true;
  try {
    searchedCompanies.value = await searchCompany(searchText.value);
    searchedStudents.value = await searchStudent(searchText.value);
  } finally {
    isSearching.value = false;
  }
};

const handleApproveCompany = async (id) => {
  actionInFlight.value = id;
  await approveCompany(id);
  await loadData();
  actionInFlight.value = null;
};

const handleRejectCompany = async (id) => {
  actionInFlight.value = id;
  await rejectCompany(id);
  await loadData();
  actionInFlight.value = null;
};

const handleBlacklistCompany = async (id) => {
  actionInFlight.value = id;
  await blacklistCompany(id);
  await loadData();
  actionInFlight.value = null;
};

const handleApproveDrive = async (id) => {
  actionInFlight.value = id;
  await approveDrive(id);
  await loadData();
  actionInFlight.value = null;
};

const handleDeleteDrive = async (id) => {
  actionInFlight.value = id;
  await deleteDrive(id);
  await loadData();
  actionInFlight.value = null;
};

const handleDeactivateStudent = async (id) => {
  actionInFlight.value = id;
  await studentDeactivate(id);
  await loadData();
  actionInFlight.value = null;
};

// Purely presentational: initials for the welcome avatar
const userInitials = computed(() => {
  if (!user?.name) return "A";
  return user.name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
});

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="dashboard">
    <!-- Top bar -->
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">&lt;/&gt;</span>
        <h1>Admin Dashboard</h1>
      </div>

      <div class="welcome-box">
        <div class="welcome-user">
          <span class="avatar">{{ userInitials }}</span>
          <div class="welcome-text">
            <span class="welcome-label">Welcome back</span>
            <strong>{{ user.name }}</strong>
          </div>
        </div>

        <div class="search-box">
          <svg
            class="search-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <circle
              cx="11"
              cy="11"
              r="7"
              stroke="currentColor"
              stroke-width="2"
            />
            <line
              x1="21"
              y1="21"
              x2="16.65"
              y2="16.65"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <input
            v-model="searchText"
            placeholder="Search student / company"
            aria-label="Search student or company"
            @keyup.enter="handleSearch"
          />
          <button
            class="btn-primary"
            :disabled="isSearching"
            @click="handleSearch"
          >
            <span v-if="isSearching" class="spinner" aria-hidden="true"></span>
            <span>{{ isSearching ? "Searching" : "Search" }}</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Error state -->
    <div v-if="loadError" class="error-banner" role="alert">
      <strong>Couldn't load the dashboard.</strong>
      <span>{{ loadError }}</span>
      <button class="btn-outline" @click="loadData">Try again</button>
    </div>
    <!-- Stat cards -->
    <div class="stats">
      <template v-if="isLoading">
        <div v-for="n in 4" :key="n" class="stat-card skeleton-card">
          <div class="skeleton-line short"></div>
          <div class="skeleton-line long"></div>
        </div>
      </template>
      <template v-else>
        <!-- --- ADDED: @click handlers + clickable class on each stat card --- -->
        <div
          class="stat-card clickable"
          role="button"
          tabindex="0"
          @click="openListModal('students')"
          @keyup.enter="openListModal('students')"
        >
          <h3>Students</h3>
          <p>{{ dashboard.students ?? 0 }}</p>
        </div>
        <div
          class="stat-card clickable"
          role="button"
          tabindex="0"
          @click="openListModal('companies')"
          @keyup.enter="openListModal('companies')"
        >
          <h3>Companies</h3>
          <p>{{ dashboard.companies ?? 0 }}</p>
        </div>
        <div
          class="stat-card accent clickable"
          role="button"
          tabindex="0"
          @click="openListModal('drives')"
          @keyup.enter="openListModal('drives')"
        >
          <h3>Drives</h3>
          <p>{{ dashboard.placement_drives ?? 0 }}</p>
        </div>
        <div
          class="stat-card clickable"
          role="button"
          tabindex="0"
          @click="openListModal('applications')"
          @keyup.enter="openListModal('applications')"
        >
          <h3>Applications</h3>
          <p>{{ dashboard.applications ?? 0 }}</p>
        </div>
      </template>
    </div>

    <!-- Registered Companies -->
    <section>
      <div class="section-header">
        <h2>Registered Companies</h2>
        <span class="count-chip">{{ companies.length }}</span>
      </div>

      <div class="table-wrap">
        <table v-if="isLoading">
          <thead>
            <tr>
              <th>Company</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="n in 3" :key="n">
              <td><div class="skeleton-line long"></div></td>
              <td><div class="skeleton-line short"></div></td>
              <td><div class="skeleton-line short"></div></td>
            </tr>
          </tbody>
        </table>

        <table v-else-if="companies.length">
          <thead>
            <tr>
              <th>Company</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in companies" :key="company.id">
              <td class="cell-primary">{{ company.company_name }}</td>
              <td>
                <span class="status-badge" :class="statusClass(company)">
                  {{ companyStatus(company) }}
                </span>
              </td>
              <td class="actions-cell">
                <button
                  class="approve"
                  :disabled="
                    (company.blacklisted ?? company.is_blacklisted) ||
                    actionInFlight === company.id
                  "
                  @click="handleApproveCompany(company.id)"
                >
                  <span
                    v-if="actionInFlight === company.id"
                    class="spinner"
                    aria-hidden="true"
                  ></span>
                  Approve
                </button>
                <button
                  class="reject"
                  :disabled="
                    (company.blacklisted ?? company.is_blacklisted) ||
                    actionInFlight === company.id
                  "
                  @click="handleRejectCompany(company.id)"
                >
                  Reject
                </button>
                <button
                  class="blacklist"
                  :disabled="
                    (company.blacklisted ?? company.is_blacklisted) ||
                    actionInFlight === company.id
                  "
                  @click="handleBlacklistCompany(company.id)"
                >
                  {{
                    (company.blacklisted ?? company.is_blacklisted)
                      ? "Blacklisted"
                      : "Blacklist"
                  }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-state">
          <p class="empty-title">No companies registered yet</p>
          <p class="empty-sub">
            Companies will appear here once they sign up for placements.
          </p>
        </div>
      </div>
    </section>

    <!-- Student Search Results -->
    <section v-if="searchedStudents.length">
      <div class="section-header">
        <h2>Student Search Results</h2>
        <span class="count-chip">{{ searchedStudents.length }}</span>
      </div>

      <div class="table-wrap" :class="{ compact: isCompactView }">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in searchedStudents" :key="student.id">
              <td class="cell-primary">{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.branch }}</td>
              <td>{{ student.cgpa }}</td>
              <td class="actions-cell">
                <button
                  class="blacklist"
                  :disabled="actionInFlight === student.id"
                  @click="handleDeactivateStudent(student.id)"
                >
                  <span
                    v-if="actionInFlight === student.id"
                    class="spinner"
                    aria-hidden="true"
                  ></span>
                  Deactivate
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Placement Drives -->
    <section>
      <div class="section-header">
        <h2>Placement Drives</h2>
        <span class="count-chip">{{ drives.length }}</span>
      </div>

      <div class="table-wrap" :class="{ compact: isCompactView }">
        <table v-if="isLoading">
          <thead>
            <tr>
              <th>Job Title</th>
              <th>Company</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="n in 3" :key="n">
              <td><div class="skeleton-line long"></div></td>
              <td><div class="skeleton-line long"></div></td>
              <td><div class="skeleton-line short"></div></td>
              <td><div class="skeleton-line short"></div></td>
            </tr>
          </tbody>
        </table>

        <table v-else-if="drives.length">
          <thead>
            <tr>
              <th>Job Title</th>
              <th>Company</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in drives" :key="drive.id">
              <td class="cell-primary">{{ drive.job_title }}</td>
              <td>{{ drive.company }}</td>
              <td>
                <span
                  class="status-badge"
                  :class="genericStatusClass(drive.status)"
                >
                  {{ drive.status }}
                </span>
              </td>
              <td class="actions-cell">
                <button
                  class="approve"
                  :disabled="actionInFlight === drive.id"
                  @click="handleApproveDrive(drive.id)"
                >
                  <span
                    v-if="actionInFlight === drive.id"
                    class="spinner"
                    aria-hidden="true"
                  ></span>
                  Approve
                </button>
                <button
                  class="reject"
                  :disabled="actionInFlight === drive.id"
                  @click="handleDeleteDrive(drive.id)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-state">
          <p class="empty-title">No placement drives yet</p>
          <p class="empty-sub">
            Approved drives from recruiters will show up here.
          </p>
        </div>
      </div>
    </section>

    <!-- Applications -->
    <section>
      <div class="section-header">
        <h2>Applications</h2>
        <span class="count-chip">{{ applications.length }}</span>
      </div>

      <div class="table-wrap" :class="{ compact: isCompactView }">
        <table v-if="isLoading">
          <thead>
            <tr>
              <th>Student</th>
              <th>Job</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="n in 3" :key="n">
              <td><div class="skeleton-line long"></div></td>
              <td><div class="skeleton-line long"></div></td>
              <td><div class="skeleton-line short"></div></td>
              <td><div class="skeleton-line short"></div></td>
            </tr>
          </tbody>
        </table>

        <table v-else-if="applications.length">
          <thead>
            <tr>
              <th>Student</th>
              <th>Job</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="application in applications" :key="application.id">
              <td class="cell-primary">{{ application.student }}</td>
              <td>{{ application.job_title }}</td>
              <td>
                <span
                  class="status-badge"
                  :class="genericStatusClass(application.status)"
                >
                  {{ application.status }}
                </span>
              </td>

              <td class="actions-cell">
                <button
                  class="approve"
                  @click="handleViewApplication(application.id)"
                >
                  View Application
                </button>

                <button
                  class="blacklist"
                  @click="handleViewStudent(application.student_id)"
                >
                  View Student
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-state">
          <p class="empty-title">No applications yet</p>
          <p class="empty-sub">
            Student applications to placement drives will appear here.
          </p>
        </div>
      </div>
    </section>

    <!-- Application detail modal -->
    <div
      v-if="selectedApplication"
      class="modal-overlay modal-overlay-top"
      @click.self="selectedApplication = null"
    >
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h2>Application Details</h2>
          <button
            class="modal-close"
            aria-label="Close"
            @click="selectedApplication = null"
          >
            &times;
          </button>
        </div>

        <div class="modal-body">
          <div class="detail-row">
            <span class="detail-label">Student</span>
            <span class="detail-value">{{ selectedApplication.student }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Email</span>
            <span class="detail-value">{{ selectedApplication.email }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Branch</span>
            <span class="detail-value">{{ selectedApplication.branch }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">CGPA</span>
            <span class="detail-value">{{ selectedApplication.cgpa }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Job</span>
            <span class="detail-value">{{
              selectedApplication.job_title
            }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Company</span>
            <span class="detail-value">{{ selectedApplication.company }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Location</span>
            <span class="detail-value">{{ selectedApplication.location }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Salary</span>
            <span class="detail-value">{{ selectedApplication.salary }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status</span>
            <span
              class="status-badge"
              :class="genericStatusClass(selectedApplication.status)"
            >
              {{ selectedApplication.status }}
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Remarks</span>
            <span class="detail-value">{{ selectedApplication.remarks }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-outline" @click="selectedApplication = null">
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Student profile modal -->
    <div
      v-if="selectedStudent"
      class="modal-overlay modal-overlay-top"
      @click.self="selectedStudent = null"
    >
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h2>Student Profile</h2>
          <button
            class="modal-close"
            aria-label="Close"
            @click="selectedStudent = null"
          >
            &times;
          </button>
        </div>

        <div class="modal-body">
          <div class="detail-row">
            <span class="detail-label">Name</span>
            <span class="detail-value">{{ selectedStudent.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Email</span>
            <span class="detail-value">{{ selectedStudent.email }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Branch</span>
            <span class="detail-value">{{ selectedStudent.branch }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">CGPA</span>
            <span class="detail-value">{{ selectedStudent.cgpa }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Year</span>
            <span class="detail-value">{{ selectedStudent.year }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Phone</span>
            <span class="detail-value">{{ selectedStudent.phone }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Skills</span>
            <span class="detail-value">{{ selectedStudent.skills }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Resume</span>
            <span class="detail-value">{{ selectedStudent.resume }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-outline" @click="selectedStudent = null">
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- --- ADDED: Students list modal (every student, opened from the Students stat card) --- -->
    <div
      v-if="activeListModal === 'students'"
      class="modal-overlay"
      @click.self="closeListModal"
    >
      <div class="modal modal-lg" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h2>All Students</h2>
          <button
            class="modal-close"
            aria-label="Close"
            @click="closeListModal"
          >
            &times;
          </button>
        </div>

        <div class="modal-body">
          <div class="table-wrap">
            <table v-if="students.length">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Branch</th>
                  <th>CGPA</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in students" :key="student.id">
                  <td class="cell-primary">{{ student.name }}</td>
                  <td>{{ student.email }}</td>
                  <td>{{ student.branch }}</td>
                  <td>{{ student.cgpa }}</td>
                  <td class="actions-cell">
                    <button
                      class="approve"
                      @click="handleViewStudent(student.id)"
                    >
                      View
                    </button>
                    <button
                      class="blacklist"
                      :disabled="actionInFlight === student.id"
                      @click="handleDeactivateStudent(student.id)"
                    >
                      <span
                        v-if="actionInFlight === student.id"
                        class="spinner"
                        aria-hidden="true"
                      ></span>
                      Deactivate
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="empty-state">
              <p class="empty-title">No students found</p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-outline" @click="closeListModal">Close</button>
        </div>
      </div>
    </div>

    <!-- --- ADDED: Companies list modal (every company, opened from the Companies stat card) --- -->
    <div
      v-if="activeListModal === 'companies'"
      class="modal-overlay"
      @click.self="closeListModal"
    >
      <div class="modal modal-lg" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h2>All Companies</h2>
          <button
            class="modal-close"
            aria-label="Close"
            @click="closeListModal"
          >
            &times;
          </button>
        </div>

        <div class="modal-body">
          <div class="table-wrap">
            <table v-if="companies.length">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="company in companies" :key="company.id">
                  <td class="cell-primary">{{ company.company_name }}</td>
                  <td>
                    <span class="status-badge" :class="statusClass(company)">
                      {{ companyStatus(company) }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button
                      class="approve"
                      :disabled="
                        (company.blacklisted ?? company.is_blacklisted) ||
                        actionInFlight === company.id
                      "
                      @click="handleApproveCompany(company.id)"
                    >
                      <span
                        v-if="actionInFlight === company.id"
                        class="spinner"
                        aria-hidden="true"
                      ></span>
                      Approve
                    </button>
                    <button
                      class="reject"
                      :disabled="
                        (company.blacklisted ?? company.is_blacklisted) ||
                        actionInFlight === company.id
                      "
                      @click="handleRejectCompany(company.id)"
                    >
                      Reject
                    </button>
                    <button
                      class="blacklist"
                      :disabled="
                        (company.blacklisted ?? company.is_blacklisted) ||
                        actionInFlight === company.id
                      "
                      @click="handleBlacklistCompany(company.id)"
                    >
                      {{
                        (company.blacklisted ?? company.is_blacklisted)
                          ? "Blacklisted"
                          : "Blacklist"
                      }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="empty-state">
              <p class="empty-title">No companies found</p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-outline" @click="closeListModal">Close</button>
        </div>
      </div>
    </div>

    <!-- --- ADDED: Drives list modal (every drive, opened from the Drives stat card) --- -->
    <div
      v-if="activeListModal === 'drives'"
      class="modal-overlay"
      @click.self="closeListModal"
    >
      <div class="modal modal-lg" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h2>All Placement Drives</h2>
          <button
            class="modal-close"
            aria-label="Close"
            @click="closeListModal"
          >
            &times;
          </button>
        </div>

        <div class="modal-body">
          <div class="table-wrap">
            <table v-if="drives.length">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td class="cell-primary">{{ drive.job_title }}</td>
                  <td>{{ drive.company }}</td>
                  <td>
                    <span
                      class="status-badge"
                      :class="genericStatusClass(drive.status)"
                    >
                      {{ drive.status }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button
                      class="approve"
                      :disabled="actionInFlight === drive.id"
                      @click="handleApproveDrive(drive.id)"
                    >
                      <span
                        v-if="actionInFlight === drive.id"
                        class="spinner"
                        aria-hidden="true"
                      ></span>
                      Approve
                    </button>
                    <button
                      class="reject"
                      :disabled="actionInFlight === drive.id"
                      @click="handleDeleteDrive(drive.id)"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="empty-state">
              <p class="empty-title">No placement drives found</p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-outline" @click="closeListModal">Close</button>
        </div>
      </div>
    </div>

    <!-- --- ADDED: Applications list modal (every application, opened from the Applications stat card) --- -->
    <div
      v-if="activeListModal === 'applications'"
      class="modal-overlay"
      @click.self="closeListModal"
    >
      <div class="modal modal-lg" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h2>All Applications</h2>
          <button
            class="modal-close"
            aria-label="Close"
            @click="closeListModal"
          >
            &times;
          </button>
        </div>

        <div class="modal-body">
          <div class="table-wrap">
            <table v-if="applications.length">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Job</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="application in applications" :key="application.id">
                  <td class="cell-primary">{{ application.student }}</td>
                  <td>{{ application.job_title }}</td>
                  <td>
                    <span
                      class="status-badge"
                      :class="genericStatusClass(application.status)"
                    >
                      {{ application.status }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button
                      class="approve"
                      @click="handleViewApplication(application.id)"
                    >
                      View Application
                    </button>
                    <button
                      class="blacklist"
                      @click="handleViewStudent(application.student_id)"
                    >
                      View Student
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="empty-state">
              <p class="empty-title">No applications found</p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-outline" @click="closeListModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ---------------------------------------------------------------
   Design tokens — HackerRank-inspired: green / deep black / white
   --------------------------------------------------------------- */
.dashboard {
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
  --shadow-hover:
    0 2px 4px rgba(13, 16, 33, 0.08), 0 8px 20px rgba(13, 16, 33, 0.1);
  --transition: 180ms ease;

  width: 92%;
  max-width: 1280px;
  margin: 28px auto 60px;
  font-family:
    "Inter",
    "Sora",
    "Space Grotesk",
    -apple-system,
    BlinkMacSystemFont,
    sans-serif;
  color: var(--black);
  background: var(--white);
}

*:focus-visible {
  outline: 2px solid var(--green);
  outline-offset: 2px;
}

/* ---------------- Top bar ---------------- */
.topbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: var(--black);
  color: var(--white);
  padding: 20px 24px;
  border-radius: var(--radius);
  margin-bottom: 24px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-mark {
  color: var(--green);
  font-weight: 700;
  font-family: monospace;
  font-size: 18px;
}
.brand h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.01em;
}
.welcome-box {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.welcome-user {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--green);
  color: var(--black);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  flex-shrink: 0;
}
.welcome-text {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}
.welcome-label {
  font-size: 11px;
  color: var(--gray-400);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.welcome-text strong {
  font-size: 14px;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--black-soft);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 6px 10px;
}
.search-icon {
  color: var(--gray-400);
  flex-shrink: 0;
}
.search-box input {
  background: transparent;
  border: none;
  color: var(--white);
  padding: 6px 4px;
  width: 220px;
  font-size: 14px;
}
.search-box input::placeholder {
  color: var(--gray-400);
}
.search-box input:focus {
  outline: none;
}

/* ---------------- Buttons ---------------- */
button {
  border: none;
  padding: 8px 14px;
  cursor: pointer;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  transition:
    transform var(--transition),
    box-shadow var(--transition),
    background var(--transition),
    opacity var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 44px;
}
button:active {
  transform: scale(0.97);
}
button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}
.btn-primary {
  background: var(--green);
  color: var(--black);
  min-height: auto;
  padding: 10px 18px;
}
.btn-primary:hover:not(:disabled) {
  background: var(--green-dark);
  box-shadow: var(--shadow-hover);
}
.btn-outline {
  background: transparent;
  border: 1px solid var(--gray-200);
  color: var(--black);
  min-height: auto;
  padding: 8px 16px;
}
.btn-outline:hover {
  border-color: var(--black);
}
.approve {
  background: var(--green);
  color: var(--black);
}
.approve:hover:not(:disabled) {
  background: var(--green-dark);
  box-shadow: var(--shadow-hover);
}
.reject {
  background: var(--white);
  color: var(--red);
  border: 1px solid var(--red-tint);
}
.reject:hover:not(:disabled) {
  background: var(--red-tint);
}
.blacklist {
  background: var(--black);
  color: var(--white);
}
.blacklist:hover:not(:disabled) {
  background: var(--black-soft);
  box-shadow: var(--shadow-hover);
}
.actions-cell {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ---------------- Spinner ---------------- */
.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
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

/* ---------------- Error banner ---------------- */
.error-banner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  background: var(--red-tint);
  color: var(--black);
  border: 1px solid #f5b5b7;
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 20px;
  font-size: 14px;
}
.error-banner strong {
  color: var(--red);
}

/* ---------------- Stat cards ---------------- */
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}
.stat-card {
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  padding: 18px;
  background: var(--white);
  transition:
    box-shadow var(--transition),
    transform var(--transition);
}
.stat-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}
/* --- ADDED: visual affordance for clickable stat cards --- */
.stat-card.clickable {
  cursor: pointer;
}
.stat-card.accent {
  border-color: var(--green);
  background: var(--green-tint);
}
.stat-card h3 {
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-600);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0;
}
.stat-card p {
  font-size: 28px;
  font-weight: 700;
  margin: 8px 0 0;
  color: var(--black);
}

/* ---------------- Sections ---------------- */
section {
  margin-bottom: 36px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.section-header h2 {
  font-size: 16px;
  font-weight: 700;
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

/* ---------------- Tables ---------------- */
.table-wrap {
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 560px;
}
table th,
table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid var(--gray-200);
  font-size: 14px;
}
table th {
  background: var(--gray-100);
  color: var(--gray-600);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 600;
}
table tbody tr {
  transition: background var(--transition);
}
table tbody tr:hover {
  background: var(--gray-100);
}
table tbody tr:last-child td {
  border-bottom: none;
}
.cell-primary {
  font-weight: 600;
}
.table-wrap.compact table th,
.table-wrap.compact table td {
  padding: 8px 14px;
  font-size: 13px;
}

/* ---------------- Status badges ---------------- */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: capitalize;
}
.status-approved {
  background: var(--green-tint);
  color: var(--green-dark);
}
.status-pending {
  background: #f4f1e6;
  color: #9a7b1f;
}
.status-rejected {
  background: var(--red-tint);
  color: var(--red);
}
.status-blacklisted {
  background: var(--black);
  color: var(--white);
}

/* ---------------- Empty state ---------------- */
.empty-state {
  padding: 48px 24px;
  text-align: center;
}
.empty-title {
  font-weight: 700;
  font-size: 15px;
  margin: 0 0 6px;
}
.empty-sub {
  font-size: 13px;
  color: var(--gray-600);
  margin: 0;
}

/* ---------------- Skeleton loading ---------------- */
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
.skeleton-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  z-index: 50;
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
  border-radius: var(--radius);
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: var(--shadow-hover);
}
/* --- ADDED: wider modal variant for the record-list modals --- */
.modal.modal-lg {
  max-width: 900px;
}
/* --- ADDED: ensures the Application/Student detail modal always renders
   above the record-list modals (e.g. when "View Application" is clicked
   from inside the "All Applications" list modal) regardless of DOM order --- */
.modal-overlay.modal-overlay-top {
  z-index: 60;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 22px;
  border-bottom: 1px solid var(--gray-200);
  position: sticky;
  top: 0;
  background: var(--white);
}
.modal-header h2 {
  font-size: 16px;
  margin: 0;
}
.modal-close {
  background: transparent;
  color: var(--gray-600);
  font-size: 20px;
  line-height: 1;
  padding: 4px 8px;
  min-height: auto;
}
.modal-close:hover {
  color: var(--black);
}
.modal-body {
  padding: 20px 22px;
}
.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid var(--gray-100);
  font-size: 14px;
}
.detail-row:last-child {
  border-bottom: none;
}
.detail-label {
  color: var(--gray-600);
  font-weight: 600;
  flex-shrink: 0;
}
.detail-value {
  text-align: right;
  word-break: break-word;
}
.modal-footer {
  padding: 16px 22px;
  border-top: 1px solid var(--gray-200);
  display: flex;
  justify-content: flex-end;
}

/* ---------------- Responsive ---------------- */
@media (max-width: 860px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .search-box input {
    width: 150px;
  }
}
@media (max-width: 560px) {
  .stats {
    grid-template-columns: 1fr;
  }
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
  .welcome-box {
    width: 100%;
    justify-content: space-between;
  }
  .view-toggle {
    justify-content: flex-start;
  }
  .actions-cell {
    flex-direction: column;
    align-items: stretch;
  }
  .actions-cell button {
    width: 100%;
    justify-content: center;
  }
}
</style>
