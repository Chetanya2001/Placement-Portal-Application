const BASE_URL = "http://127.0.0.1:5000/api/company";

function getHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  };
}

// Register Company
export async function registerCompany(companyData) {
  console.log("company data in service", companyData);
  const response = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(companyData),
  });

  return await response.json();
}

// Company Dashboard
export async function getDashboard() {
  const response = await fetch(`${BASE_URL}/dashboard`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// Create Placement Drive
export async function createJob(jobData) {
  const response = await fetch(`${BASE_URL}/jobs`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(jobData),
  });

  return await response.json();
}

// Get Company's Jobs
export async function getCompanyJobs() {
  const response = await fetch(`${BASE_URL}/jobs`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// View Applicants of a Job
export async function getApplicants(driveId) {
  const response = await fetch(`${BASE_URL}/jobs/${driveId}/applications`, {
    headers: getHeaders(),
  });

  return await response.json();
}

// Shortlist Applicant
export async function shortlistApplicant(applicationId) {
  const response = await fetch(
    `${BASE_URL}/applications/${applicationId}/shortlist`,
    {
      method: "PUT",
      headers: getHeaders(),
    },
  );

  return await response.json();
}

// Reject Applicant
export async function rejectApplicant(applicationId, remarks = "") {
  const response = await fetch(
    `${BASE_URL}/applications/${applicationId}/reject`,
    {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify({ remarks }),
    },
  );

  return await response.json();
}

// Select Applicant
export async function selectApplicant(applicationId) {
  const response = await fetch(
    `${BASE_URL}/applications/${applicationId}/select`,
    {
      method: "PUT",
      headers: getHeaders(),
    },
  );

  return await response.json();
}

// Update Job Status
export async function updateJobStatus(jobId, status) {
  const response = await fetch(`${BASE_URL}/jobs/${jobId}/status`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify({ status }),
  });

  return await response.json();
}

// Schedule Interview
export async function scheduleInterview(applicationId, interviewData) {
  const response = await fetch(
    `${BASE_URL}/applications/${applicationId}/schedule-interview`,
    {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(interviewData),
    },
  );

  return await response.json();
}

// Update Application Status
export async function updateApplicationStatus(
  applicationId,
  status,
  remarks = "",
) {
  const response = await fetch(
    `${BASE_URL}/applications/${applicationId}/status`,
    {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify({
        status,
        remarks,
      }),
    },
  );

  return await response.json();
}
