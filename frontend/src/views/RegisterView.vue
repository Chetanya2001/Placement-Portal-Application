<script setup>
import { ref } from "vue";
import { registerUser } from "@/services/auth.service";
const name = ref("");
const email = ref("");
const password = ref("");
const role = ref("Student"); // Default selected

const register = async () => {
  try {
    const result = await registerUser({
      name: name.value,
      email: email.value,
      password: password.value,
      role: role.value,
    });

    alert(result.message);
  } catch (error) {
    alert(error.message);
  }
};
</script>

<template>
  <div class="container">
    <h2>Register</h2>

    <input v-model="name" type="text" placeholder="Name" />

    <input v-model="email" type="email" placeholder="Email" />

    <input v-model="password" type="password" placeholder="Password" />

    <!-- Role Toggle -->
    <div class="toggle-container">
      <label class="toggle-option" :class="{ active: role === 'Student' }">
        <input type="radio" value="Student" v-model="role" />
        Student
      </label>

      <label class="toggle-option" :class="{ active: role === 'Company' }">
        <input type="radio" value="Company" v-model="role" />
        Company
      </label>
    </div>

    <button @click="register">Register</button>

    <p>
      Already have an account?
      <router-link to="/login"> Login </router-link>
    </p>
  </div>
</template>

<style scoped>
.container {
  width: 300px;
  margin: 100px auto;
}

input[type="text"],
input[type="email"],
input[type="password"] {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
}

.toggle-container {
  display: flex;
  margin: 15px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.toggle-option {
  flex: 1;
  text-align: center;
  padding: 10px;
  cursor: pointer;
  background: #f5f5f5;
  transition: 0.3s;
}

.toggle-option input {
  display: none;
}

.toggle-option.active {
  background: #42b883;
  color: white;
  font-weight: bold;
}

button {
  width: 100%;
  padding: 10px;
  cursor: pointer;
}
</style>
