# Quiz Master

## 📌 Project Overview

**Quiz Master - V1** is a Flask-based multi-user quiz application with admin and user roles. The platform allows administrators to create and manage quizzes, while users can participate in quizzes and track their progress. It features user authentication, a search function, and a clean, responsive UI built using Jinja2 templates.

## 🚀 Features

- **User Authentication**: Secure login and registration system.
- **Role-Based Access**:
  - **Admin:** Create, edit, and delete quizzes; manage users.
  - **User:** Attempt quizzes, view scores, and track progress.
- **Quiz Management**:
  - Add and modify questions.
  - Set time limits for quizzes.
  - View quiz results.
- **Search Functionality**: Quickly find quizzes and users.
- **Custom Error Handling**: Redirect users based on their roles.
- **Responsive UI**: Built using Jinja2 templating and Bootstrap.

## 🛠️ Tech Stack

- **Backend**: Flask (Python), Flask-Login (Authentication), SQLite (Database)
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Database**: SQLite (Can be replaced with PostgreSQL/MySQL)
- **Hosting**: Flask (Can be deployed on Heroku/Vercel/Render)

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/quiz-master-v1.git
   cd quiz-master-v1
   ```
2. **Create a virtual environment & install dependencies:**
    1. open the terminal
    2. change the directory to the current app directory
    3. create a environment
    ```python -m venv .foldername```
    4. Activating the environment ``` .foldername/Scripts/Activate ```
    5. install the required packages from the file ``` pip install -r 'file.txt' ```
    6. if you want to check the packages ``` pip freeze ```

3. **Run the application:**
   ```python app.py ```

## 🔑 User Roles & Authentication

- **Admin**:
  - Login using predefined admin credentials.
  - Create, update, and delete quizzes.
- **User**:
  - Register and log in.
  - Attempt quizzes and view results.

## 📌 API Endpoints

| Endpoint             | Method | Description          |
| -------------------- | ------ | -------------------- |
| `/`                  | GET    | Home Page            |
| `/login`             | POST   | User Login           |
| `/signup`            | POST   | User Registration    |
| `/admin`             | GET    | Admin Dashboard      |
| `/quiz/create`       | POST   | Create a new quiz    |
| `/quiz/<id>`         | GET    | View a specific quiz |
and many more....
