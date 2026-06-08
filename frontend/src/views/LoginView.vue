<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { loginUser } from "../services/auth.service";

const router = useRouter();

const email = ref("");
const password = ref("");

const login = async () => {
  try {
    const data = await loginUser({
      email: email.value,
      password: password.value,
    });

    localStorage.setItem("token", data.token);
    localStorage.setItem("user", JSON.stringify(data.user));

    switch (data.user.role.toLowerCase()) {
      case "admin":
        router.push("/admin-dashboard");
        break;

      case "company":
        router.push("/company-dashboard");
        break;

      case "student":
        router.push("/student-dashboard");
        break;

      default:
        router.push("/login");
    }
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
};
</script>

<template>
  <div class="container">
    <h2>Login</h2>
    <input v-model="email" type="email" placeholder="email" />
    <input v-model="password" type="password" placeholder="password" />
    <button @click="login">Login</button>
    <p>
      Don't have an account? <router-link to="/register">Register</router-link>
    </p>
  </div>
</template>
<style scoped>
.container {
  width: 300px;
  margin: 100px auto;
}

input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
}

button {
  width: 100%;
  padding: 10px;
}
</style>
