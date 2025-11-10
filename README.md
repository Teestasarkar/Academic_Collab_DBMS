# 🎓 Academic Collaboration Platform

## 👥 Team Details
**Team No:** 25  
**Members:**  
- Teesta Sarkar  
- Vardha Kathuria  

---

## 🧾 Overview
The **Academic Collaboration Platform** is a web-based system for seamless collaboration among **students and teachers** — and also **teacher-to-teacher** or **student-to-student** — based on their **skills, interests, experience, and publications**.  
It enables users to create projects, find collaborators, and work together efficiently.

---

## ⚙️ Tech Stack
- **Frontend:** HTML, CSS, Jinja2 (Flask)
- **Backend:** Flask (Python)
- **Database:** MySQL
- **Tools:** VS Code, CLI

---

## 🧩 Key Features
- User Registration & Login  
- Profile Management (skills & interests)  
- Project Creation and Collaboration  
- Search & Match Based on Skills  
- Admin Control Panel  

---

## 🧠 SQL Components
**Trigger**
```sql
CREATE TRIGGER log_new_user 
AFTER INSERT ON users
FOR EACH ROW
INSERT INTO user_log (user_id, action, timestamp)
VALUES (NEW.user_id, 'Registered', NOW());
Procedure

sql
Copy code
CALL add_collaboration(user_id, project_id);
Function

sql
Copy code
SELECT total_projects(owner_id);
📊 Example Queries
Nested Query

sql
Copy code
SELECT name, email FROM users 
WHERE user_id IN (SELECT owner_id FROM projects);
Join Query

sql
Copy code
SELECT u.name, p.title, c.status 
FROM collaborations c
JOIN users u ON c.user_id = u.user_id
JOIN projects p ON c.project_id = p.project_id;
Aggregate Query

sql
Copy code
SELECT owner_id, COUNT(*) AS total_projects 
FROM projects GROUP BY owner_id;
🚀 How to Run
bash
Copy code
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Import Database
mysql -u root -p academic_collab < academic_collab.sql

# Run Flask App
python app.py

© 2025 Team 25 — Academic Collaboration Platform

yaml
Copy code
