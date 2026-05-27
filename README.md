# Placement Portal Application (PPA)

A full-stack web application built for managing campus recruitment activities between Institutes, Companies, and Students.

The application allows:

- Admins to manage companies, students, and placement drives
- Companies to conduct placement drives
- Students to apply for placement opportunities

---

# Tech Stack

## Backend

- Flask
- Flask REST APIs
- SQLite
- Redis
- Celery

## Frontend

- VueJS
- Bootstrap 5
- Jinja2 (only for entry point if required)

## Other Tools

- JWT Authentication / Session Authentication
- CSV Export
- Email/SMS/Webhook Notifications

---

# Features

## Admin Features

- Admin login
- Approve/reject companies
- Approve/reject placement drives
- View all applications
- Search students and companies
- Blacklist/deactivate users
- Placement statistics dashboard

## Company Features

- Company registration/login
- Create placement drives
- Manage applications
- Shortlist students
- Update hiring status
- Schedule interviews

## Student Features

- Student registration/login
- View approved drives
- Apply to placement drives
- Track application status
- Upload resume
- Export application history as CSV

---

# Database Models

## User

| Field     | Type    |
| --------- | ------- |
| id        | Integer |
| name      | String  |
| email     | String  |
| password  | String  |
| role      | String  |
| is_active | Boolean |

---

## Student

| Field   | Type        |
| ------- | ----------- |
| id      | Integer     |
| user_id | Foreign Key |
| branch  | String      |
| cgpa    | Float       |
| year    | Integer     |
| resume  | String      |

---

## Company

| Field           | Type        |
| --------------- | ----------- |
| id              | Integer     |
| user_id         | Foreign Key |
| company_name    | String      |
| hr_contact      | String      |
| website         | String      |
| approval_status | String      |

---

## PlacementDrive

| Field                | Type        |
| -------------------- | ----------- |
| id                   | Integer     |
| company_id           | Foreign Key |
| job_title            | String      |
| description          | Text        |
| eligibility_branch   | String      |
| min_cgpa             | Float       |
| application_deadline | Date        |
| status               | String      |

---

## Application

| Field      | Type        |
| ---------- | ----------- |
| id         | Integer     |
| student_id | Foreign Key |
| drive_id   | Foreign Key |
| applied_on | DateTime    |
| status     | String      |

---

# Folder Structure

```bash
placement-portal/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   ├── controllers/
│   ├── services/
│   ├── tasks/
│   ├── utils/
│   ├── static/
│   ├── templates/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── components/
│   ├── views/
│   ├── router/
│   └── package.json
│
├── instance/
│
├── redis/
│
├── screenshots/
│
├── README.md
└── report.pdf
```
