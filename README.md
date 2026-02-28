# EyesEdge REST API

This is the REST API component of the EyesEdge security camera system. Built with Django and Django REST Framework, it provides endpoints for managing cameras, motion events, and captured images.

## Technology Stack

- Python 3.13
- Django 5.2.11
- Django REST Framework 3.16.1
- SQLite (default database)

## Setup and Installation

### Prerequisites

- Python 3.13 or higher
- pip
- Pipenv (recommended)

### Installation Steps

1. Navigate to the api directory:
```bash
cd api
```

2. Install dependencies using Pipenv:
```bash
pipenv install
```

3. Activate the virtual environment:
```bash
pipenv shell
```

4. Apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Cameras

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cameras/` | List all cameras |
| POST | `/api/cameras/` | Create a new camera |
| GET | `/api/cameras/<id>/` | Retrieve a specific camera |
| PUT | `/api/cameras/<id>/` | Update a camera |
| DELETE | `/api/cameras/<id>/` | Delete a camera |
| GET | `/api/cameras/<id>/motions/` | List all motion events for a camera |
| GET | `/api/cameras/<id>/images/` | List all images for a camera |

### Motion Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/motions/` | List all motion events |
| POST | `/api/motions/` | Create a new motion event |
| GET | `/api/motions/<id>/` | Retrieve a specific motion event |
| PUT | `/api/motions/<id>/` | Update a motion event |
| DELETE | `/api/motions/<id>/` | Delete a motion event |
| GET | `/api/motions/<id>/images/` | List all images for a motion event |

### Images

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/images/` | List all images |
| POST | `/api/images/` | Upload a new image |
| GET | `/api/images/<id>/` | Retrieve a specific image |
| PUT | `/api/images/<id>/` | Update image metadata |
| DELETE | `/api/images/<id>/` | Delete an image |

## Admin Interface

Access the Django admin interface at `http://127.0.0.1:8000/admin/` to manage data through a web interface.

---

## Testing

### Running Tests

Run all tests:
```bash
python manage.py test
```

Run tests for a specific app:
```bash
python manage.py test cameras
python manage.py test motions
python manage.py test images
```

Run tests with verbose output:
```bash
python manage.py test -v 2
```

### Test Coverage

Install coverage tool:
```bash
pipenv install coverage --dev
```

Run tests with coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

Generate HTML coverage report:
```bash
coverage html
```

The coverage report will be available in the `htmlcov/` directory.

---

## Code Quality

### PyLint

Run PyLint to check code quality:
```bash
pipenv install pylint pylint-django --dev
pylint --load-plugins pylint_django --django-settings-module=eyesedge.settings cameras motions images
```

The project maintains a PyLint score of 9.0 or higher.

---

## Database Description

The EyesEdge API uses a relational database with five main models that work together to manage security camera monitoring, motion detection, and object recognition.

### Models Overview

**Camera**
The Camera model stores configuration for physical security cameras. Each camera has a unique address, resolution settings (720p, 1080p, or 4K), frame rate (fps), motion sensitivity threshold, and status. Cameras serve as the root entity that connects to all monitoring activities.

**MotionEvent**
The MotionEvent model records when motion is detected by a camera. Each event captures the timestamp, duration of motion, and the sensitivity threshold used. Motion events belong to one camera and act as containers for images and detections.

**Image**
The Image model stores captured photographs. Each image is linked to a motion event, and the camera is accessed through the motion event relationship. Images contain the file path, file size, and creation timestamp. When motion is detected, one or more images are captured and stored.

**Detection**
The Detection model represents objects identified in images using YOLO with the COCO dataset. Each detection records the object class name (like person, car, dog), confidence score, and creation time. Detections can be associated with either a motion event or a specific image, allowing flexible tracking of what objects were found.

**Alert**
The Alert model manages notifications triggered by detections. Each alert links to a detection and contains a message, creation timestamp, and delivery status. Alerts notify users when specific objects are detected.

### Relationships

The database follows a hierarchical structure:

- Camera to MotionEvent: 1 to N
- MotionEvent to Camera: N to 1
- MotionEvent to Image: 1 to N
- MotionEvent to Detection: 1 to N
- Image to MotionEvent: N to 1
- Image to Camera: via MotionEvent (no direct FK)
- Image to Detection: 1 to N
- Detection to MotionEvent: N to 0..1 (optional)
- Detection to Image: N to 0..1 (optional)
- Detection to Alert: 1 to N
- Alert to Detection: N to 1

This design allows the system to track the complete flow from motion detection to object recognition to user notification, while maintaining clear relationships between all components.

