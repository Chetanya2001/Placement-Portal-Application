<script setup>
const user = JSON.parse(localStorage.getItem("user"));
</script>

<template>
  <h1>Company Dashboard</h1>

  <p>Name: {{ user.name }}</p>
  <p>Email: {{ user.email }}</p>
  <p>Role: {{ user.role }}</p>
</template>
