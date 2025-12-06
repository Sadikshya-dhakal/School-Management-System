# 🏫 School Management System
A Django-based School Management System designed for administrators, staff, and students to efficiently manage attendance, results, notifications, feedback, timetables, and more.


<img width="1103" height="729" alt="Screenshot 2025-07-18 120236" src="https://github.com/user-attachments/assets/45a22284-d05c-4cb2-938d-94dee1598fd9" />


![WhatsApp Image 2025-07-25 at 13 59 59_dd8c38fb](https://github.com/user-attachments/assets/2ebc8d68-fb61-46f1-99d7-f51c38d02cad)

<img width="1901" height="917" alt="Screenshot 2025-07-18 120806" src="https://github.com/user-attachments/assets/dbc45d4c-5eca-4644-9a4d-9c50b79683c7" />


<img width="1899" height="914" alt="Screenshot 2025-07-18 120523" src="https://github.com/user-attachments/assets/52a17cd1-eeac-4645-b3eb-6b42529a81a6" />

<img width="1919" height="814" alt="Screenshot 2025-07-18 123154" src="https://github.com/user-attachments/assets/6b2776e5-2924-440a-bda1-5536522f4a4a" />
<img width="1919" height="818" alt="Screenshot 2025-07-18 123112" src="https://github.com/user-attachments/assets/69847cde-655c-4cc6-89e1-f0e209f24603" />
<img width="1916" height="899" alt="Screenshot 2025-07-18 123054" src="https://github.com/user-attachments/assets/c8a0332a-4462-41e4-9b66-170ae679063b" />
<img width="1915" height="880" alt="Screenshot 2025-07-18 123024" src="https://github.com/user-attachments/assets/55acdd16-a924-44a9-9dd7-a10dc35d8ca2" />
<img width="1917" height="912" alt="Screenshot 2025-07-18 123006" src="https://github.com/user-attachments/assets/9209a2fe-be93-4564-acd3-5c0d09701b35" />
<img width="1913" height="879" alt="Screenshot 2025-07-18 122924" src="https://github.com/user-attachments/assets/5c50141a-19c5-403c-8e76-98a01e77d834" />
<img width="1919" height="851" alt="Screenshot 2025-07-18 122906" src="https://github.com/user-attachments/assets/ac3c3638-c4be-4189-b6da-6e9d9ddfb92b" />
<img width="1889" height="813" alt="Screenshot 2025-07-18 121718" src="https://github.com/user-attachments/assets/d4f159bf-cab8-46d2-aa16-b2fe2059efcc" />
<img width="1891" height="910" alt="Screenshot 2025-07-18 121406" src="https://github.com/user-attachments/assets/74ef7391-8f08-425d-82ba-b0e9dbc20cf2" />
<img width="1919" height="914" alt="Screenshot 2025-07-18 121332" src="https://github.com/user-attachments/assets/afbce0e2-310d-4f64-8a23-c854cc3e46d0" />
<img width="1909" height="878" alt="Screenshot 2025-07-18 121301" src="https://github.com/user-attachments/assets/51b89db9-4e29-477b-a27c-b66f56fa9708" />









### 🚀 Features
## 👩‍💼 Admin (HOD)
✅ Add, view, edit, and delete students, staff, courses, and subjects

🕒 Create and manage class timetables for each course/semester

📋 View leave applications and feedback submitted by staff and students

📢 Send notifications to staff and students

📊 View overall attendance records and student results

## 👨‍🏫 Staff
📝 Mark and view student attendance

🧮 Add and manage student results

🕒 View assigned class timetable

📨 Apply for leave and submit feedback

🔔 View notifications sent by the admin

## 👨‍🎓 Student
📅 View personal attendance records and academic results

🕒 View daily/weekly class timetable

📝 Apply for leave and send feedback to staff or admin

🔔 Receive and view notifications from the admin

## 🧱 Built With
Backend: Django (Python)

Frontend: HTML, CSS, Bootstrap

Database: SQLite

Authentication: Django Custom User Model

Admin Dashboard: Role-based access for HOD, Staff, and Students

## ⚙ Installation
# 1. Clone the Repository

git clone https://github.com/ManjilS/PROJECT_5SEM.git



# 2. Create a Virtual Environment

python -m venv venv

  **For Linux/macOS**

source venv/bin/activate

 **For Windows**

venv\Scripts\activate

# 3. Install Dependencies

pip install -r requirements.txt

# 4. Run Migrations
-python manage.py makemigrations

-python manage.py migrate

# 5. Create Superuser

python manage.py createsuperuser
# 6. Start the Development Server


python manage.py runserver

Then open your browser and visit:
👉 http://127.0.0.1:8000/
