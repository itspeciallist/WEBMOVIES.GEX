# Overview

This is a Georgian-language movie streaming and discovery platform built with Flask. The application allows users to browse movies, rate them, add favorites, and stream content from various video sources. It features user authentication, role-based access control (admin/moderator/user), and a modern responsive UI with Georgian language support.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with a base template structure for consistent UI
- **UI Framework**: Custom CSS with modern design patterns, responsive grid layouts, and dark theme
- **JavaScript**: Vanilla JavaScript for video player functionality and AJAX interactions
- **Video Player**: Universal video player supporting YouTube, Vimeo, Dailymotion, and direct video URLs
- **Internationalization**: Georgian language interface throughout the application

## Backend Architecture
- **Web Framework**: Flask with Blueprint-style route organization
- **Authentication**: Session-based authentication with password hashing using Werkzeug
- **Security**: CSRF protection using Flask-WTF, secure file uploads with filename sanitization
- **File Management**: Static file serving for user uploads (movie posters, profile pictures)
- **Database**: SQLite with foreign key constraints and row factory for dictionary-like access

## Data Storage
- **Primary Database**: SQLite with comprehensive schema including:
  - Users table with profile management and role-based access
  - Movies table with metadata (title, description, genre, year, ratings)
  - Reviews and favorites system for user interactions
  - Foreign key relationships for data integrity
- **File Storage**: Local filesystem storage for uploaded media files
- **Session Management**: Flask session storage for user state

## Authentication & Authorization
- **User Roles**: Three-tier system (user, moderator, admin)
- **Password Security**: Werkzeug password hashing with salt
- **Session Management**: Secure session handling with configurable secret keys
- **Access Control**: Route-level permissions based on user roles
- **User Moderation**: Ban system with temporary restrictions

## Core Features
- **Movie Discovery**: Advanced filtering by genre, year, and rating
- **Search Functionality**: Full-text search across movie titles and descriptions
- **User Interactions**: Rating system, favorites, and review capabilities
- **Content Management**: Admin/moderator tools for adding and managing movies
- **Profile Management**: User profile customization with picture uploads

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **Flask-WTF**: CSRF protection and form handling
- **Werkzeug**: Password hashing and secure filename utilities
- **SQLite3**: Database connectivity (Python standard library)

## Frontend Libraries
- **Font Awesome 6.0.0**: Icon library via CDN
- **Plyr 3.8.3**: Universal video player via CDN for enhanced media playback

## Video Platform Integrations
- **YouTube**: Embedded video player support
- **Vimeo**: Embedded video player support  
- **Dailymotion**: Embedded video player support
- **Direct Video URLs**: Support for MP4 and other direct video formats

## Environment Configuration
- **SESSION_SECRET**: Environment variable for Flask session security
- **File Upload Directories**: Configurable paths for user-generated content storage

## Third-party Services
The application is designed to integrate with various video hosting platforms through their embed APIs, with fallback mechanisms for unsupported video sources. The modular video player architecture allows for easy extension to additional video platforms.