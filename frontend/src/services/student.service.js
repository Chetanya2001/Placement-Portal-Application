// student.service.js

const BASE_URL = "http://127.0.0.1:5000/api/student";

function getHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  };
}

// ---------- Profile Registration ----------

// Called right after auth /register when role is Student
// body: { user_id, branch?, cgpa?, year?, phone?, skills?, resume? }
export async function registerStudent(studentData) {
  const response = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(studentData),
  });

  return await response.json();
}

// ---------- Profile ----------

// GET /api/student/profile
export async function getProfile() {
  const response = await fetch(`${BASE_URL}/profile`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// PUT /api/student/profile
// body: { name?, branch?, cgpa?, year?, phone?, skills?, resume? }
export async function updateProfile(profileData) {
  const response = await fetch(`${BASE_URL}/profile`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(profileData),
  });

  return await response.json();
}

// ---------- Job Postings ----------

// GET /api/student/jobs
// params: { company?, position?, skill? }  — all optional
export async function browseJobs(filters = {}) {
  const params = new URLSearchParams();

  if (filters.company) params.append("company", filters.company);
  if (filters.position) params.append("position", filters.position);
  if (filters.skill) params.append("skill", filters.skill);

  const query = params.toString() ? `?${params.toString()}` : "";

  const response = await fetch(`${BASE_URL}/jobs${query}`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// GET /api/student/jobs/:driveId
export async function getJobDetail(driveId) {
  const response = await fetch(`${BASE_URL}/jobs/${driveId}`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// ---------- Applications ----------

// POST /api/student/jobs/:driveId/apply
export async function applyForJob(driveId) {
  const response = await fetch(`${BASE_URL}/jobs/${driveId}/apply`, {
    method: "POST",
    headers: getHeaders(),
  });

  return await response.json();
}

// GET /api/student/applications
// optional status filter: "applied" | "shortlisted" | "selected" | "rejected" | "interview scheduled"
export async function getMyApplications(status = "") {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";

  const response = await fetch(`${BASE_URL}/applications${query}`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// GET /api/student/applications/:id
export async function getApplicationDetail(applicationId) {
  const response = await fetch(`${BASE_URL}/applications/${applicationId}`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// ---------- Interviews ----------

// GET /api/student/interviews
export async function getMyInterviews() {
  const response = await fetch(`${BASE_URL}/interviews`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// GET /api/student/interviews/:id
export async function getInterviewDetail(interviewId) {
  const response = await fetch(`${BASE_URL}/interviews/${interviewId}`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// ---------- Offer Letter ----------

// GET /api/student/applications/:id/offer-letter
// Returns a PDF blob — triggers a file download in the browser
export async function downloadOfferLetter(applicationId) {
  const response = await fetch(
    `${BASE_URL}/applications/${applicationId}/offer-letter`,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        // No Content-Type here — response is a binary PDF, not JSON
      },
    },
  );

  if (!response.ok) {
    // Server returned an error JSON, surface it normally
    const error = await response.json();
    return { error: true, message: error.message };
  }

  // Convert response to a blob and trigger browser download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = `offer_letter_${applicationId}.pdf`;

  document.body.appendChild(link);
  link.click();

  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);

  return { success: true };
}
