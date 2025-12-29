# FilmHub 🎬

A modern film reviewing web application built with Flask and Vue.js, featuring a beautiful interface for discovering, reviewing, and discussing movies.

## ✨ Features

### Core Functionality
- **Movie Discovery**: Browse and search through a comprehensive movie database
- **User Reviews**: Write and read detailed movie reviews and ratings
- **Community Posts**: Share thoughts and discussions about movies
- **Advanced Search**: Find movies by title, genre, year, and language
- **Personal Watchlist**: Keep track of movies you want to watch
- **User Profiles**: Manage your reviews, posts, and preferences

### Admin Panel
- **User Management**: View and manage user accounts
- **Content Moderation**: Monitor posts, comments, and reviews
- **Analytics Dashboard**: Track site statistics and user activity
- **Log Management**: View system logs and user activities

### Technical Features
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Real-time Notifications**: Toast notifications for user actions
- **Secure Authentication**: JWT-based authentication system
- **Database Flexibility**: Support for both SQLite and MySQL
- **Modern UI**: Clean, intuitive interface with smooth animations

## 🛠️ Tech Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router 4** - Official router for Vue.js
- **Pinia** - State management library
- **Axios** - HTTP client for API calls
- **ECharts** - Data visualization for admin analytics
- **Vite** - Fast build tool and development server

### Backend
- **Flask** - Lightweight WSGI web application framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Flask-JWT-Extended** - JWT authentication extension
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **bcrypt** - Password hashing library
- **PyMySQL** - MySQL driver for Python

### Database
- **SQLite** (default) - Embedded database for development
- **MySQL** - Production-ready relational database

## 📁 Project Structure

```
filmhub/
├── api/                   # Backend (Flask)
│   ├── config.ini         # Application configuration
│   ├── requirements.txt   # Python dependencies
│   ├── scripts/           # Utility scripts
│   └── src/               # Flask application source
│       ├── app.py         # Main Flask application
│       ├── blueprints/    # Flask blueprints (API routes)
│       ├── common/        # Shared utilities and validation
│       ├── config.py      # Configuration management
│       ├── db.py          # Database connection
│       ├── models/        # SQLAlchemy models
│       ├── services/      # Business logic layer
│       └── data/          # Static data and assets
├── web/                   # Frontend (Vue.js)
│   ├── package.json       # Node.js dependencies
│   ├── vite.config.js     # Vite configuration
│   └── src/               # Vue.js application source
│       ├── api/           # API client functions
│       ├── components/    # Vue components
│       ├── router/        # Vue Router configuration
│       ├── stores/        # Pinia stores
│       └── views/         # Page components
└── README.md              # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** for the backend
- **Node.js 20+** for the frontend
- **MySQL** (optional, SQLite is used by default)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd filmhub
   ```

2. **Backend Setup**

   ```bash
   # Navigate to backend directory
   cd api

   # Install Python dependencies
   pip install -r requirements.txt

   # Initialize the database
   python src/init_db.py
   ```

3. **Frontend Setup**

   ```bash
   # Navigate to frontend directory
   cd ../web

   # Install Node.js dependencies
   npm install

   # Start development server
   npm run dev
   ```

4. **Start the Backend**

   ```bash
   # From the api directory
   cd src
   python app.py
   ```

### Configuration

#### Database Configuration

The application supports both SQLite (default) and MySQL databases. Configure your choice in `api/config.ini`:

**SQLite (Default):**
```ini
[DATABASE]
TYPE = sqlite
SQLITE_NAME = filmhub.db
SQLITE_PATH = db
```

**MySQL:**
```ini
[DATABASE]
TYPE = mysql
MYSQL_HOST = localhost
MYSQL_PORT = 3306
MYSQL_USER = your_username
MYSQL_PASSWORD = your_password
MYSQL_DB_NAME = filmhub
```

#### JWT Configuration

Update JWT settings in `api/config.ini`:
```ini
[JWT]
SECRET = your-secret-key-here
ALGORITHM = HS256
ACCESS_EXPIRES_DAYS = 7
```

## 🎯 Usage

### For Users
1. **Register/Login**: Create an account or sign in
2. **Browse Movies**: Explore the movie catalog with filters and search
3. **Write Reviews**: Share your thoughts on movies
4. **Create Posts**: Start discussions about cinema
5. **Manage Profile**: Update your information and view your activity

### For Administrators
1. **Access Admin Panel**: Navigate to `/admin` (admin user only)
2. **User Management**: View user statistics and manage accounts
3. **Content Monitoring**: Review posts, comments, and logs
4. **Analytics**: Monitor site usage and activity trends

## 🔧 Development

### Running in Development Mode

**Frontend:**
```bash
cd web
npm run dev
```

**Backend:**
```bash
cd api/src
python app.py
```

### Building for Production

**Frontend:**
```bash
cd web
npm run build
npm run preview
```

**Backend:**
Use a WSGI server like Gunicorn:
```bash
cd api/src
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 app:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Vue.js and Flask best practices
- Write clear, concise commit messages
- Test your changes thoroughly
- Update documentation as needed

## 📝 API Documentation

The backend provides RESTful APIs for:
- User authentication and management
- Movie data retrieval and management
- Review and rating systems
- Post and comment management
- Administrative functions

API endpoints are organized in blueprints located in `api/src/blueprints/`.

## 🔒 Security

- Password hashing using bcrypt
- JWT token-based authentication
- CORS protection
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Movie data and posters sourced from various public APIs
- Icons from various open-source icon libraries
- UI inspiration from modern web design trends

---

Made with ❤️ for film enthusiasts worldwide
