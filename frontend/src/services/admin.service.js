const BASE_URL = "http://127.0.0.1:5000/api/admin";

function getHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  };
}
//1
export async function getDashboard() {
  const response = await fetch(`${BASE_URL}/dashboard`, {
    method: "GET",
    headers: getHeaders(),
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message);
  }

  return data;
}
//2
export async function getCompanies() {
  const response = await fetch(`${BASE_URL}/companies`, {
    headers: getHeaders(),
    method: "GET",
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message);
  }

  return data;
}
// 3
export async function getApplications() {
  const response = await fetch(`${BASE_URL}/applications`, {
    headers: getHeaders(),
    method: "GET",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message);
  }
  return data;
}
// 4
export async function getDrives() {
  const response = await fetch(`${BASE_URL}/drives`, {
    method: "GET",
    headers: getHeaders(),
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message);
  }
  return data;
}
//5
export async function approveCompany(id) {
  const response = await fetch(`${BASE_URL}/companies/${id}/approve`, {
    method: "PUT",
    headers: getHeaders(),
  });

  return await response.json();
}
//6
export async function rejectCompany(id) {
  const response = await fetch(`${BASE_URL}/companies/${id}/reject`, {
    method: "PUT",
    headers: getHeaders(),
  });

  return await response.json();
}
//7
export async function blacklistCompany(id) {
  const response = await fetch(`${BASE_URL}/companies/${id}/blacklisted`, {
    method: "PUT",
    headers: getHeaders(),
  });

  return await response.json();
}
//8
export async function approveDrive(id) {
  const response = await fetch(`${BASE_URL}/drives/${id}/approve`, {
    method: "PUT",
    headers: getHeaders(),
  });

  return await response.json();
}
//9
export async function deleteDrive(id) {
  const response = await fetch(`${BASE_URL}/drives/${id}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return await response.json();
}
//10
export async function searchCompany(name) {
  const response = await fetch(`${BASE_URL}/companies/search?name=${name}`, {
    method: "GET",
    headers: getHeaders(),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message);
  }
  return data;
}
//11
export async function searchStudent(name) {
  const response = await fetch(`${BASE_URL}/students/search?name=${name}`, {
    method: "GET",
    headers: getHeaders(),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message);
  }
  return data;
}
//12
export async function studentDeactivate(id) {
  const response = await fetch(`${BASE_URL}/students/${id}/deactivate`, {
    method: "PUT",
    headers: getHeaders(),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message);
  }
  return data;
}
//13
export async function getApplicationDetail(id) {
  const response = await fetch(`${BASE_URL}/applications/${id}`, {
    method: "GET",
    headers: getHeaders(),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message);
  }

  return data;
}

//14
export async function getStudentProfile(studentId) {
  const response = await fetch(`${BASE_URL}/profile/${studentId}`, {
    method: "GET",
    headers: getHeaders(),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message);
  }

  return data;
}

//15
export async function getStudents() {
  const response = await fetch(`${BASE_URL}/students`, {
    method: "GET",
    headers: getHeaders(),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message);
  }

  return data;
}
