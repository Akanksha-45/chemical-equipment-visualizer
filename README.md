# Chemical Equipment Parameter Visualizer - Backend API

## 🎯 Project Overview
Django REST API backend for a hybrid web + desktop application for chemical equipment data visualization and analytics.

## ✅ Completed Features

### 1. **CSV Upload API** (`/api/upload/`)
- Accept CSV files with columns: Equipment Name, Type, Flowrate, Pressure, Temperature
- Automatic data validation and storage
- Returns summary statistics after upload

### 2. **Data Analysis Functions** 
- Calculate averages, min, max, median, standard deviation
- Equipment type distribution analysis
- Risk assessment (Normal/Warning/Critical)

### 3. **API Endpoints**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload/` | POST | Upload CSV file |
| `/api/summary/` | GET | Get statistics (with optional dataset_id) |
| `/api/equipment/` | GET | Get equipment list (first 100 records) |
| `/api/datasets/` | GET | Get last 5 uploaded datasets |
| `/api/report/pdf/` | GET | Generate PDF report (with optional dataset_id) |
| `/api/auth/login/` | POST | User login - returns auth token |
| `/api/auth/register/` | POST | User registration - returns auth token |
| `/api/auth/logout/` | POST | User logout - invalidates token |
| `/api/auth/user/` | GET | Get current user information |

### 4. **Database Models**
- **Dataset**: Stores metadata about uploaded CSV files
- **Equipment**: Stores individual equipment records with parameters

### 5. **Data Storage**
- Automatic history tracking (stores last 5 datasets)
- SQLite database for persistence
- Django ORM for database management

## 📦 Tech Stack Installed
- Django 6.0.1 ✅
- Django REST Framework ✅
- Pandas 3.0.0 ✅
- django-cors-headers 4.9.0 ✅
- ReportLab 4.4.9 ✅

## 🚀 How to Use

### 1. Start the Server
```bash
cd Backend/backend_project
python manage.py runserver
# Server runs at http://127.0.0.1:8000/
```

### 2. Upload CSV File
```bash
curl -X POST http://127.0.0.1:8000/api/upload/ \
  -F "file=@sample_equipment_data.csv"
```

### 3. Get Summary Statistics
```bash
curl http://127.0.0.1:8000/api/summary/
```

### 4. Get Equipment List
```bash
curl http://127.0.0.1:8000/api/equipment/
```

### 5. Get Dataset History
```bash
curl http://127.0.0.1:8000/api/datasets/
```

## 📊 API Response Examples

### Upload Response
```json
{
  "message": "CSV uploaded successfully",
  "dataset_id": 1,
  "summary": {
    "total_equipment": 20,
    "avg_flowrate": 150.5,
    "avg_pressure": 2.5,
    "avg_temperature": 85.0,
    "equipment_type_distribution": {
      "Reactor": 3,
      "Distillation": 2,
      "Heat Exchanger": 2
    }
  }
}
```

### Summary Response
```json
{
  "total_count": 20,
  "averages": {
    "avg_flowrate": 150.5,
    "avg_pressure": 2.5,
    "avg_temperature": 85.0
  },
  "type_distribution": {
    "Reactor": 3,
    "Distillation": 2,
    "Heat Exchanger": 2
  },
  "statistics": {
    "flowrate": {
      "min": 0.0,
      "max": 250.0,
      "median": 165.0,
      "std": 65.2
    }
  }
}
```

## 🛠️ Admin Interface
Access Django admin at `http://127.0.0.1:8000/admin/`
- View/manage datasets
- View/search equipment records
- Filter by type and upload date

## 📁 Project Structure
```
Backend/
├── backend_project/
│   ├── db.sqlite3          # Database
│   ├── manage.py           # Django management
│   └── backend_project/
│       ├── settings.py     # Django settings (CORS enabled)
│       ├── urls.py         # URL routing
│       └── wsgi.py         # WSGI config
│   └── equipment/
│       ├── models.py       # Dataset & Equipment models
│       ├── views.py        # API endpoints
│       ├── urls.py         # API routing
│       ├── admin.py        # Admin interface
│       ├── data_analysis.py # Pandas analysis functions
│       └── migrations/     # Database migrations
└── sample_equipment_data.csv  # Sample data for testing
```

## 🔐 Security Notes
- CSRF protection enabled
- CORS enabled for React (http://localhost:3000) and Vite (http://localhost:5173)
- Modify `CORS_ALLOWED_ORIGINS` in settings.py for production

## 📝 Next Steps
1. **Create React Web Frontend** (consume `/api/equipment/`, `/api/summary/`, upload to `/api/upload/`)
2. **Create PyQt5 Desktop App** (same API consumption with GUI)
3. **Add PDF Report Generation** (using ReportLab)
4. **Add Authentication** (Django's built-in auth system)
5. **Deploy** to Heroku/AWS/DigitalOcean

## 📚 Learning Resources
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [React.js](https://react.dev/)
- [PyQt5](https://doc.qt.io/qt-5/)
- [Chart.js](https://www.chartjs.org/)
- [Matplotlib](https://matplotlib.org/)

## ✨ API Features Ready for Frontend
- ✅ File upload with validation
- ✅ Real-time data analysis
- ✅ Comprehensive statistics (mean, median, std, min, max)
- ✅ Equipment type categorization
- ✅ Risk assessment
- ✅ Dataset history (last 5)
- ✅ CORS enabled for cross-origin requests
