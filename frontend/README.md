# ScottLMS Frontend

A modular Streamlit application for the ScottLMS Learning Management System.

## 🏗️ Project Structure

```
frontend/
├── Home.py              # Home page entry point
├── config.py            # Configuration and settings
├── styles.css           # Custom CSS styles
├── components/          # Reusable components
│   ├── __init__.py
│   ├── utils.py         # API utilities and helpers
│   ├── forms.py         # Form components
│   └── tables.py        # Table display components
├── pages/               # Individual page modules
│   ├── __init__.py
│   ├── Dashboard.py     # Dashboard logic
│   ├── Users.py         # User management page
│   ├── Courses.py       # Course management page
│   └── Enrollments.py   # Enrollment management page
└── README.md            # This file
```

## 🎯 Features

### Multi-Page Application
- **Dashboard**: Overview of users, courses, and enrollments
- **User Management**: Create, view, edit, and delete users
- **Course Management**: Create, view, edit, and delete courses  
- **Enrollment Management**: Create and view enrollments

### Modular Architecture
- **Reusable Components**: Forms and tables can be used across pages
- **Centralized Configuration**: All settings in one place
- **Utility Functions**: Shared API calls and helpers
- **Clean Separation**: Each page is self-contained

## 🚀 Usage

### Development
The application runs automatically via Docker Compose:

```bash
make start  # Starts all services including frontend
```

### Manual Run (if needed)
```bash
streamlit run frontend/Home.py
```

### Navigation
- **Main Dashboard**: Automatic landing page
- **Sidebar Navigation**: Streamlit automatically detects pages/ directory
- **Tabs**: Each management page has View/Create tabs

## 🔧 Adding New Features

### Adding a New Page
1. Create a new file in `pages/` (e.g., `Analytics.py`)
2. Use descriptive names (e.g., `Users.py`, `Courses.py`)
3. Import necessary components from `components/`
4. Streamlit will automatically add it to the sidebar

### Adding New Components
1. Add functions to appropriate files in `components/`
2. Import and use in your pages
3. Keep components focused and reusable

### Configuration Changes
- Update `config.py` for app-wide settings
- Use environment variables for deployment-specific configs

## 📁 Key Files

- **`Home.py`**: Entry point, shows dashboard
- **`config.py`**: All configuration and styling
- **`components/utils.py`**: API communication functions
- **`components/forms.py`**: All form components
- **`components/tables.py`**: Data display and detail views
- **`pages/*.py`**: Individual page implementations

## 🎨 Styling

Custom CSS is defined in `config.py` and applied across all pages for consistent styling.

## 🔌 API Integration

All API calls go through `components/utils.py` with consistent error handling and response formatting.
