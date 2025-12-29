<div align="center">

# 🤖 Telegram CRM Bot

### Enterprise-style CRM system built on top of Telegram

**Role-based access • Advanced MySQL logic • Analytics & Reports • Local AI recommendations**

---

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Local%20LLM-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

</div>

---

## 💼 About the Project (HR Overview)

This repository contains a **completed enterprise-style CRM system implemented as a Telegram bot**.

The project was created as a **portfolio project** to demonstrate:

* backend and database-centric development;
* real business logic and auditability;
* system architecture and scalability;
* analytics, reporting, and AI-assisted decision support.

The system focuses on **practical business workflows** such as client management, deal tracking, employee task control, performance analytics, and transparent auditing.

---

## ✨ Highlights

✅ Enterprise-style role model (Admin / Manager / Employee)
✅ Strong database-driven logic (triggers, procedures, functions)
✅ Full audit log of all critical actions
✅ Automated reminders and notifications
✅ Visual analytics with charts and PDF reports
✅ Local AI model for analytical recommendations
✅ Telegram as a business interface (no separate frontend)

---

## 👥 Roles & Access Model

<details>
<summary><strong>👑 Administrator</strong></summary>

* Full access to all system data
* User and role management (except other admins)
* Employee → Manager assignment
* Global analytics and reports
* Sales analysis and sales funnel
* Full PDF report generation with AI recommendations

**Reports available:**

* 📊 Employee activity
* 📈 Deal progress
* 💰 Sales by clients
* 🪣 Sales funnel
* 📅 Period dynamics
* 🤖 Full analytical report

</details>

<details>
<summary><strong>🧑‍💼 Manager</strong></summary>

* Access to all clients
* Deal and task management
* Employee assignment and control
* Deal progress visualization
* **Employees section** (assigned staff & direct messaging)
* Team analytics

**Reports available:**

* 📊 Employee task performance
* 📈 Deal progress
* 📅 Task timeline dynamics

AI recommendations are generated when building selected charts.

</details>

<details>
<summary><strong>👤 Employee</strong></summary>

* Access only to assigned deals and tasks
* Task status updates
* Client work within assigned deals
* Personal progress tracking

</details>

---

## 🧾 Core Modules

### 👥 Clients

* Create, edit, delete clients
* Search and filtering:

  * name
  * segment
  * creation date
  * manager
  * deal stage

### 🤝 Deals

* Deal creation and manager assignment
* Employee assignment
* Deal stages: `New → In Progress → Closed`
* Automatic closure when all tasks are completed
* Visual progress charts
* Complete change history

### ✅ Tasks

* Task creation and assignment
* Statuses: `New / In Progress / Completed / Overdue`
* Deadlines and priorities
* Automated reminders
* Overdue notifications

All changes are recorded in the audit log.

---

## 📊 Analytics & Reporting

📈 **Charts**

* Generated in Python
* Sent as PNG via Telegram
* Short explanatory summaries

📄 **PDF Reports (Admin only)**

* Period-based (day / week / month / year)
* Charts + aggregated data
* AI recommendations
* Stored in database
* Delivered via Telegram

---

## 🧠 AI Integration

Local LLM model:

```
models/tinyllama
```

**AI principles:**

* Analytics and recommendations only
* No direct influence on business logic
* Limited, conservative management insights
* Triggered:

  * by Managers — for selected charts
  * by Admins — for full reports

Admin reports (including AI insights) are stored in the database.

---

## 🗄 Database-Driven Architecture

**Database: MySQL (MySQL Workbench)**

The database plays an **active architectural role**.

Implemented at DB level:

* triggers
* stored procedures
* user-defined functions
* centralized audit log

Database logic handles:

* deadline control
* reminder conditions
* overdue detection
* automatic audit logging

**APScheduler** works alongside the database to deliver notifications to Telegram users.

---

## 🔐 Security Model

* Authentication via **Telegram ID**
* No passwords stored
* Role and permission control via database
* Sensitive configuration stored in `.env`

---

## 🧩 Tech Stack

| Category      | Technology                  |
| ------------- | --------------------------- |
| Language      | Python 3.11+                |
| Bot Framework | aiogram                     |
| Database      | MySQL + asyncmy             |
| ORM           | SQLAlchemy                  |
| Scheduler     | APScheduler                 |
| Analytics     | pandas, matplotlib / plotly |
| Reports       | reportlab (PDF)             |
| AI            | Local LLM (TinyLLaMA)       |

---

## 🚀 Project Status

🟢 **Completed**
Designed with focus on scalability, auditability, and real-world business use cases.

---

## 👩‍💻 Author

**Polina Shevtsova**
Python / Backend Developer

This project was developed independently and is intended for professional portfolio and hiring evaluation.

⭐ If you find this project interesting — feel free to star the repository!
