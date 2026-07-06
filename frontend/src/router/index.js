import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import StudentDashboardView from "@/views/StudentDashboardView.vue";
import AdminDashboardView from "@/views/AdminDashboardView.vue";
import CompanyDashboardView from "@/views/CompanyDashboardView.vue";
import CreateCompanyView from "@/views/CreateCompanyView.vue";
import CreateDriveView from "@/views/CreateDriveView.vue";
import CreateStudentView from "@/views/CreateStudentView.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },
  { path: "/student-dashboard", component: StudentDashboardView },
  { path: "/admin-dashboard", component: AdminDashboardView },
  { path: "/company-dashboard", component: CompanyDashboardView },
  { path: "/company/register", component: CreateCompanyView },
  { path: "/company/create-drive", component: CreateDriveView },
  { path: "/student/create-student", component: CreateStudentView },
];

const router = createRouter({ history: createWebHistory(), routes });

export default router;
