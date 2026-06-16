<script setup>
import { ref, onMounted } from "vue";
import {
  getApplications,
  getCompanies,
  getDashboard,
  getDrives,
  approveCompany,
  approveDrive,
  blacklistCompany,
  deleteDrive,
  studentDeactivate,
  searchCompany,
  searchStudent,
  rejectCompany,
} from "../services/admin.service";
const user = JSON.parse(localStorage.getItem("user"));
const dashboard = ref({});
const companies = ref([]);
const drives = ref([]);
const applications = ref([]);
const searchText = ref("");
const searchedCompanies = ref([]);
const searchedStudents = ref([]);

const loadData = async () => {
  try {
    dashboard.value = await getDashboard();
    companies.value = await getCompanies();
    drives.value = await getDrives();
    applications.value = await getApplications();
  } catch (error) {
    console.log(error);
  }
};

const handleSearch = async () => {
  if (!searchText.value.trim()) return;

  searchedCompanies.value = await searchCompany(searchText.value);
  searchedStudents.value = await searchStudent(searchText.value);
};

const handleApproveCompany = async (id) => {
  await approveCompany(id);
  loadData();
};

const handleRejectCompany = async (id) => {
  await rejectCompany(id);
  loadData();
};

const handleBlacklistCompany = async (id) => {
  await blacklistCompany(id);
  loadData();
};

const handleApproveDrive = async (id) => {
  await approveDrive(id);
  loadData();
};

const handleDeleteDrive = async (id) => {
  await deleteDrive(id);
  loadData();
};

const handleDeactivateStudent = async (id) => {
  await studentDeactivate(id);
  loadData();
};

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="dashboard">
    <h1>Admin Dashboard</h1>
    <div class="welcome-box">
      <div>
        <strong>Welcome {{ user.name }}</strong>
      </div>
      <div class="search-box">
        <input v-model="searchText" placeholder="Search student/company" />
        <button @click="handleSearch">Search</button>
      </div>
    </div>
    <div class="stats">
      <div class="stat-card">
        <h3>Students</h3>
        <p>{{ dashboard.students }}</p>
      </div>
      <div class="stat-card">
        <h3>Companies</h3>
        <p>{{ dashboard.companies }}</p>
      </div>
      <div class="stat-card">
        <h3>Drives</h3>
        <p>{{ dashboard.placement_drives }}</p>
      </div>
      <div class="stat-card">
        <h3>Applications</h3>
        <p>{{ dashboard.applications }}</p>
      </div>
    </div>
    <section>
      <h2>Registered Companies</h2>
      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="company in companies" :key="company.id">
            <td>{{ company.company_name }}</td>
            <td>{{ company.approval_status }}</td>
            <td>
              <button class="approve" @click="handleApproveCompany(company.id)">
                Approve
              </button>
              <button class="reject" @click="handleRejectCompany(company.id)">
                Reject
              </button>
              <button
                class="blacklist"
                @click="handleBlacklistCompany(company.id)"
              >
                Blacklist
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
    <section v-if="searchedStudents.length">
      <h2>Student Search Results</h2>
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
            <td>{{ student.name }}</td>
            <td>{{ student.email }}</td>
            <td>{{ student.branch }}</td>
            <td>{{ student.cgpa }}</td>
            <td>
              <button
                class="blacklist"
                @click="handleDeactivateStudent(student.id)"
              >
                Deactivate
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Placement Drives</h2>
      <table>
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
            <td>{{ drive.job_title }}</td>
            <td>{{ drive.company }}</td>
            <td>{{ drive.status }}</td>
            <td>
              <button class="approve" @click="handleApproveDrive(drive.id)">
                Approve
              </button>
              <button class="reject" @click="handleDeleteDrive(drive.id)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Applications</h2>
      <table>
        <thead>
          <tr>
            <th>Student</th>
            <th>Job</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="application in applications" :key="application.id">
            <td>{{ application.student }}</td>
            <td>{{ application.job_title }}</td>
            <td>{{ application.status }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
<style scoped>
.dashboard {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  font-family: Arial, sans-serif;
}
h1 {
  text-align: center;
  margin-bottom: 25px;
}
.welcome-box {
  border: 1px solid #ccc;
  padding: 15px;
  margin-bottom: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-box {
  display: flex;
  gap: 10px;
}
.search-box input {
  padding: 8px;
  width: 250px;
}
.search-box button {
  padding: 8px 15px;
}
.stats {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}
.stat-card {
  flex: 1;
  border: 1px solid #ccc;
  padding: 15px;
  text-align: center;
}
.stat-card p {
  font-size: 24px;
  margin-top: 10px;
}
section {
  margin-bottom: 35px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
table th,
table td {
  border: 1px solid #ddd;
  padding: 10px;
}
table th {
  background: #f3f3f3;
}
button {
  border: none;
  padding: 6px 10px;
  margin-right: 5px;
  cursor: pointer;
  border-radius: 4px;
}
.approve {
  background: #28a745;
  color: white;
}
.reject {
  background: #dc3545;
  color: white;
}
.blacklist {
  background: #ff9800;
  color: white;
}
</style>
