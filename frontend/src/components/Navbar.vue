<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// Reactive user + token state — this is the fix. Previously `user` was read
// once as a plain const at setup time, so clearing localStorage on logout
// never updated the template (Vue had no reactive value to re-render from).
const user = ref(null);
const token = ref(null);

// Logout button (and avatar/email) only render when BOTH a token and a
// user object actually exist — not just one of the two.
const isAuthenticated = computed(() => !!token.value && !!user.value);

const loadUserFromStorage = () => {
  const rawUser = localStorage.getItem("user");
  token.value = localStorage.getItem("token");
  try {
    user.value = rawUser ? JSON.parse(rawUser) : null;
  } catch (e) {
    user.value = null;
  }
};

const handleLogout = () => {
  // Clears the auth token and user object stored at login time
  localStorage.removeItem("token");
  localStorage.removeItem("user");

  // Immediately clear the reactive state so the avatar/email/logout button
  // disappear right away, without waiting on a route change or reload.
  user.value = null;
  token.value = null;

  // Send the user back to the login screen
  router.push("/login");
};

// Keeps the navbar in sync if the token/user is cleared or changed in
// another tab (e.g. logging out of one tab logs out all open tabs).
const handleStorageEvent = (e) => {
  if (e.key === "user" || e.key === "token") {
    loadUserFromStorage();
  }
};

onMounted(() => {
  loadUserFromStorage();
  window.addEventListener("storage", handleStorageEvent);

  // storage events only fire in OTHER tabs, never the tab that made the
  // change. Login calls localStorage.setItem then router.push in the same
  // tab, so we also re-check on every route change to pick that up.
  router.afterEach(() => {
    loadUserFromStorage();
  });
});
</script>

<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <span class="brand-mark">&lt;/&gt;</span>
      <span class="brand-name">Placement Portal</span>
    </div>

    <div class="navbar-right">
      <template v-if="isAuthenticated">
        <div class="navbar-user">
          <span class="avatar">{{
            (user.name || user.email || "U")[0].toUpperCase()
          }}</span>
          <span class="user-email">{{ user.email }}</span>
        </div>

        <button class="logout-btn" @click="handleLogout">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <polyline
              points="16 17 21 12 16 7"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <line
              x1="21"
              y1="12"
              x2="9"
              y2="12"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          Logout
        </button>
      </template>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  --green: #2ec866;
  --green-dark: #1f9e4f;
  --black: #0d1021;
  --black-soft: #171a2e;
  --white: #ffffff;
  --gray-400: #9aa0ab;

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 24px;
  background: var(--black);
  color: var(--white);
  font-family:
    "Inter",
    "Sora",
    "Space Grotesk",
    -apple-system,
    BlinkMacSystemFont,
    sans-serif;
}

.navbar-brand {
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
.brand-name {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 8px;
}
.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--green);
  color: var(--black);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}
.user-email {
  font-size: 13px;
  color: var(--gray-400);
  display: none;
}
@media (min-width: 560px) {
  .user-email {
    display: inline;
  }
}

.logout-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  color: var(--white);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 6px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  min-height: 40px;
  transition:
    background 180ms ease,
    border-color 180ms ease,
    transform 180ms ease;
}
.logout-btn:hover {
  background: var(--black-soft);
  border-color: var(--green);
  color: var(--green);
}
.logout-btn:active {
  transform: scale(0.97);
}
.logout-btn:focus-visible {
  outline: 2px solid var(--green);
  outline-offset: 2px;
}

@media (max-width: 480px) {
  .navbar {
    padding: 12px 16px;
  }
  .brand-name {
    font-size: 15px;
  }
}
</style>
