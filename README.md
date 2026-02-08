# API

## Database Description

The EyesEdge API uses a relational database with five main models that work together to manage security camera monitoring, motion detection, and object recognition.

### Models Overview

**Camera**
The Camera model stores configuration for physical security cameras. Each camera has a unique address, resolution settings (720p, 1080p, or 4K), frame rate (fps), motion sensitivity threshold, and status. Cameras serve as the root entity that connects to all monitoring activities.

**MotionEvent**
The MotionEvent model records when motion is detected by a camera. Each event captures the timestamp, duration of motion, and the sensitivity threshold used. Motion events belong to one camera and act as containers for images and detections.

**Image**
The Image model stores captured photographs. Each image is linked to both a camera and a motion event. Images contain the file path, file size, and creation timestamp. When motion is detected, one or more images are captured and stored.

**Detection**
The Detection model represents objects identified in images using YOLO with the COCO dataset. Each detection records the object class name (like person, car, dog), confidence score, and creation time. Detections can be associated with either a motion event or a specific image, allowing flexible tracking of what objects were found.

**Alert**
The Alert model manages notifications triggered by detections. Each alert links to a detection and contains a message, creation timestamp, and delivery status. Alerts notify users when specific objects are detected.

### Relationships

The database follows a hierarchical structure:

- A Camera has many MotionEvents (one-to-many)
- A Camera has many Images (one-to-many)
- A MotionEvent belongs to one Camera (many-to-one)
- A MotionEvent has many Images (one-to-many)
- A MotionEvent has many Detections (one-to-many)
- An Image belongs to one Camera (many-to-one)
- An Image belongs to one MotionEvent (many-to-one)
- An Image has many Detections (one-to-many)
- A Detection belongs to one MotionEvent or one Image (many-to-one, optional)
- A Detection has many Alerts (one-to-many)
- An Alert belongs to one Detection (many-to-one)

This design allows the system to track the complete flow from motion detection to object recognition to user notification, while maintaining clear relationships between all components.
