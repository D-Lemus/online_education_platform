# Online-Edu: Online Education Platform

Online-Edu is a full educational platform that manages users, courses, lessons, enrollments, and academic progress.  
It integrates three different databases:

- MongoDB for users, courses, and lessons  
- Dgraph for graph-based enrollments  
- Cassandra for logs and academic progress  

The system includes:

- FastAPI backend  
- Interactive CLI client  
- Business-rule search assistant using ChromaDB  
- Full auditing and security logging  
- Role-based functionality (Student, Teacher, Admin)

------------------------------------------------------------

# Technologies Used

Backend: FastAPI  
Database (primary): MongoDB  
Graph database: Dgraph  
Log and progress database: Apache Cassandra  
CLI Client: Python  
Vector search engine: ChromaDB  
Serialization: Pydantic

------------------------------------------------------------

# Project Structure
```
online-edu/
│
├── edu_app/
│   ├── db/
│   │   ├── mongo.py
│   │   ├── dgraph.py
│   │   └── cassandra.py
│   │
│   ├── models/
│   │   ├── courses.py
│   │   ├── enrollments.py
│   │   ├── progress.py
│   │   └── user.py
│   │
│   ├── routes/
│   │   ├── courses.py
│   │   ├── enrollments.py
│   │   ├── lessons.py
│   │   ├── progress.py
│   │   └── users.py
│   │
│   ├── services/
│   │   ├── audit_service.py
│   │   ├── choma_engine.py
│   │   └── business_knowledge.txt
│   │
│   └── main.py
│
├
├── menu_main.py
├── menu_admin.py
├── menu_teacher.py
├── menu_student.py
├── Client_common.py
└── requirements.txt
```


------------------------------------------------------------

# Installation

Create virtual environment:

python -m venv .venv
source .venv/bin/activate   (Linux/macOS)
.\.venv\Scripts\activate    (Windows)

Install dependencies:

pip install -r requirements.txt

------------------------------------------------------------

# Database Configuration
```
MongoDB:
Should run locally at mongodb://localhost:27017  
Database name: online_edu

Dgraph:
docker run -it -p 8080:8080 -p 9080:9080 dgraph/standalone

Cassandra:
docker run --name cassandra -p 9042:9042 -d cassandra

Then create the keyspace:

CREATE KEYSPACE online_edu WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};

Create the required tables:

CREATE TABLE query_audit (
  log_date date,
  ts timestamp,
  user_id text,
  query_text text,
  params text,
  PRIMARY KEY (log_date, ts)
);

CREATE TABLE security_logs (
  user_id text,
  ts timestamp,
  action text,
  details text,
  PRIMARY KEY (user_id, ts)
);

CREATE TABLE lesson_progress (
  user_id text,
  course_id text,
  lesson_id text,
  ts timestamp,
  status text,
  PRIMARY KEY (user_id, course_id, ts)
);
```
------------------------------------------------------------

# Running the Backend

uvicorn edu_app.main:app --reload

API documentation available at:
http://127.0.0.1:8000/docs

------------------------------------------------------------

# Running the CLI Client

python menu_main.py

------------------------------------------------------------

# User Roles

STUDENT:
- View available courses
- Enroll in courses
- View enrolled courses
- View lessons
- View academic progress
- Cannot modify courses or lessons

TEACHER:
- Create courses
- Create lessons for their courses
- View their own courses
- View students enrolled in their courses
- Update their courses and lessons
- Delete their courses and lessons
- Cannot modify users or roles

ADMIN:
- View all users
- Update any user
- Change user roles
- Delete users
- View all courses
- Edit any course
- Edit any lesson
- Delete any course or lesson

------------------------------------------------------------

# ChromaDB Knowledge Assistant

The file business_knowledge.txt contains domain knowledge used by the vector search engine.

chroma_engine.py loads the knowledge and provides a simple function:

answer = search(query)

Menu option added to main menu:

4) Ask Assistant (AI)

Allows users to ask business-rule related questions.

------------------------------------------------------------

# Main Endpoints
```
Users:
POST /users/
POST /users/login
GET /users/
PUT /users/{email}
PUT /users/{email}/role
DELETE /users/{email}

Courses:
POST /courses/
GET /courses/
GET /courses/{id}
PUT /courses/{id}
DELETE /courses/{id}

Lessons:
POST /courses/{id}/lessons
GET /courses/{id}/lessons
PUT /courses/{id}/lessons/{lesson_id}
DELETE /courses/{id}/lesson/{lesson_id}

Enrollments:
POST /enrollments/enroll
POST /enrollments/unenroll
GET /enrollments/me
GET /enrollments/courses/{id}/students

Progress:
POST /progress/complete-lesson
GET /progress/my-progress/{course_id}
```
------------------------------------------------------------

# Logging and Auditing

Cassandra tracks system events including:

- Successful logins
- Failed logins
- User updates
- Role changes
- Course updates
- Deleting courses or lessons
- User deletions
- Student enrollments and unenrollments
- Lesson completion progress

------------------------------------------------------------

# Requirements

Python 3.10+  
MongoDB 6+  
Cassandra 4+  
Dgraph latest  
ChromaDB pip package

------------------------------------------------------------

# Current Status

Backend fully implemented  
CLI functional with role-based interaction  
Databases fully integrated  
Logging and auditing complete  
ChromaDB knowledge assistant integrated  
Business rules fully implemented  
Project meets all functional requirements

