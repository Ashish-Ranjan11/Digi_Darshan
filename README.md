# Digii-Darshan — Smart Pilgrimage & Temple Crowd Management System

**Digii-Darshan** is a full-stack web platform designed to improve crowd regulation, queue management, emergency response, and accessibility across high-footfall temples and pilgrimage sites. The project was developed for **Smart India Hackathon 2025**, under the problem statement **Temple & Pilgrimage Crowd Management — Somnath, Dwarka, Ambaji, and Pavagadh**.

The platform provides a digital ecosystem where pilgrims can book darshan slots, receive QR-based e-tickets, track queue status, access parking and route guidance, and receive emergency alerts. Temple authorities can monitor live crowd density, manage time slots, view occupancy analytics, verify tickets, and respond to safety alerts through a centralized admin dashboard.

---

## Project Overview

Large pilgrimage sites often face overcrowding, long queues, traffic congestion, lack of real-time communication, and safety risks during peak hours and festivals. Digii-Darshan addresses these issues through a scalable software-based solution that combines slot-based ticketing, live occupancy tracking, QR verification, emergency alerting, and role-based dashboards.

The goal is to make temple visits safer, smoother, more accessible, and better organized for pilgrims, senior citizens, differently-abled visitors, temple administrators, and emergency response teams.

---

## Key Features

### Pilgrim Module

* Secure pilgrim registration and login.
* Temple-wise darshan slot booking.
* QR-based digital ticket generation.
* Live queue and booking status.
* Parking and route guidance.
* Emergency alerts and temple notifications.
* Senior citizen and differently-abled priority booking support.

### Admin Control Room

* Role-based admin login.
* Temple-wise crowd monitoring dashboard.
* Live occupancy and crowd density updates.
* Slot creation and capacity management.
* Emergency alert generation.
* Booking and check-in analytics.
* Parking zone and route visibility.

### Scanner / Gate Staff Module

* QR ticket verification.
* Pilgrim check-in and check-out flow.
* Ticket validity status.
* Entry control support for temple gates.

### Emergency & Safety Module

* Real-time alert broadcasting.
* Emergency instructions for pilgrims.
* Crowd risk visibility for admins.
* Supports faster coordination with response teams.

---

## Tech Stack

### Frontend

* Next.js
* React.js
* TypeScript
* Tailwind CSS
* Axios
* Responsive UI Components

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT Authentication
* WebSockets
* REST APIs

### Database

* SQLite for local development
* PostgreSQL-ready for production deployment

### DevOps & Deployment

* Git & GitHub
* Vercel-ready frontend
* Render/Railway-ready backend
* Environment-based configuration
* Docker support

---

## System Architecture

```text
digidarshan-fullstack/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── seed.py
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── temples.py
│   │       ├── bookings.py
│   │       ├── crowd.py
│   │       ├── alerts.py
│   │       ├── scanner.py
│   │       └── analytics.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── login/
│   │   ├── register/
│   │   ├── dashboard/
│   │   ├── admin/
│   │   └── scanner/
│   │
│   ├── components/
│   ├── lib/
│   ├── package.json
│   ├── tailwind.config.ts
│   └── .env.local.example
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Database Design

The backend uses SQLAlchemy ORM with a relational database structure.

### Main Tables

```text
users
temples
time_slots
bookings
crowd_readings
alerts
parking_zones
transport_routes
notifications
```

### User Roles

```text
pilgrim
admin
operator
scanner
```

Each role has a separate workflow and dashboard access, making the system suitable for real-world temple administration and crowd-control operations.

---



---

## Demo Credentials

After running the seed command, use the following demo accounts:

| Role               | Email                                                     | Password     |
| ------------------ | --------------------------------------------------------- | ------------ |
| Admin              | [admin@digidarshan.in](mailto:admin@digidarshan.in)       | Admin@123    |
| Emergency Operator | [operator@digidarshan.in](mailto:operator@digidarshan.in) | Operator@123 |
| Scanner            | [scanner@digidarshan.in](mailto:scanner@digidarshan.in)   | Scanner@123  |
| Pilgrim            | [pilgrim@digidarshan.in](mailto:pilgrim@digidarshan.in)   | Pilgrim@123  |

---

## API Modules

### Authentication

* User registration
* Login
* JWT token generation
* Role-based access control

### Booking System

* Temple selection
* Slot booking
* QR ticket generation
* Booking status tracking

### Crowd Monitoring

* Live crowd readings
* Occupancy updates
* Temple-wise crowd density
* Admin dashboard integration

### Alert System

* Emergency alert creation
* Alert broadcasting
* Pilgrim-side safety notifications

### Scanner System

* QR validation
* Check-in
* Check-out
* Ticket status verification

---


```

Backend environment variables:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB_NAME
SECRET_KEY=your-secure-secret-key
CORS_ORIGINS=https://your-frontend-domain.vercel.app
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Production Database

Recommended databases:

```text
Neon PostgreSQL
Supabase PostgreSQL
Railway PostgreSQL
Render PostgreSQL
```

---

## Real-World Impact

Digii-Darshan is designed to support safer and more efficient pilgrimage experiences by reducing overcrowding, improving queue discipline, supporting emergency communication, and making darshan more accessible for senior citizens and differently-abled pilgrims.

### Expected Benefits

* Reduced waiting time for pilgrims.
* Improved crowd regulation at temple entry points.
* Faster emergency response.
* Better accessibility for elderly and differently-abled visitors.
* Organized parking and traffic flow.
* Data-driven decision-making for temple authorities.
* Scalable model for multiple pilgrimage sites.

---





## Author

**Ashish Ranjan**
Full-Stack Developer | AI/ML Enthusiast | Smart India Hackathon Participant

GitHub: [Ashish-Ranjan11](https://github.com/Ashish-Ranjan11)

---

## Repository

```text
https://github.com/Ashish-Ranjan11/Digi_Darshan
```

---

## License

This project is developed for educational, innovation, and hackathon purposes.

