# TrabahoPH API Documentation

## Overview
The TrabahoPH REST API provides access to job listings, employer information, and job applications. All endpoints return JSON responses and support pagination.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
- Public endpoints (job listings, employer info) are accessible without authentication
- Protected endpoints (applications, user-specific data) require SessionAuthentication
- Include session cookies from login for authenticated requests

## Rate Limiting
- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour

---

## Endpoints

### Jobs

#### List All Jobs
```
GET /api/jobs/
```

Query Parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `category` - Filter by category
- `province` - Filter by province
- `search` - Search keyword (searches title, description, location)
- `ordering` - Sort by field (`created_at`, `salary`)

Response:
```json
{
  "count": 156,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Senior Developer",
      "employer_name": "Tech Company",
      "category": "IT",
      "location": "Manila",
      "province": "Metro Manila",
      "salary": "60000",
      "applications_count": 5,
      "created_at": "2024-04-20T10:30:00Z"
    }
  ]
}
```

#### Get Job Details
```
GET /api/jobs/{id}/
```

Response:
```json
{
  "id": 1,
  "title": "Senior Developer",
  "employer": {
    "id": 1,
    "business_name": "Tech Company",
    "business_type": "IT",
    "province": "Metro Manila",
    "contact_number": "02123456789",
    "business_email": "hr@techco.com"
  },
  "description": "We're looking for an experienced senior developer...",
  "category": "IT",
  "location": "Manila, Metro Manila",
  "salary": "60000",
  "is_active": true,
  "applications_count": 5,
  "created_at": "2024-04-20T10:30:00Z"
}
```

#### List Jobs by Province
```
GET /api/jobs/by_province/?province=Metro%20Manila
```

#### List Jobs by Category
```
GET /api/jobs/by_category/?category=IT
```

#### Get Applications for a Job (Employer Only)
```
GET /api/jobs/{id}/applications/
```

---

### Employers

#### List All Employers
```
GET /api/employers/
```

Query Parameters:
- `page` - Page number
- `page_size` - Items per page
- `business_type` - Filter by business type
- `province` - Filter by province
- `search` - Search by business name or description

Response:
```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "business_name": "Tech Company",
      "business_type": "IT",
      "business_description": "Leading IT solutions provider",
      "contact_number": "02123456789",
      "province": "Metro Manila",
      "municipality": "Manila",
      "barangay": "Intramuros",
      "business_email": "hr@techco.com",
      "full_name": "John Manager",
      "created_at": "2024-04-15T08:00:00Z"
    }
  ]
}
```

#### Get Employer Details
```
GET /api/employers/{id}/
```

#### Get All Jobs by Employer
```
GET /api/employers/{id}/jobs/
```

---

### Applications

#### List My Applications
```
GET /api/applications/
```

Requires authentication.

Query Parameters:
- `page` - Page number
- `status` - Filter by status (`pending`, `accepted`, `rejected`)
- `job__category` - Filter by job category
- `ordering` - Sort by field (`-applied_at` for newest first)

Response:
```json
{
  "count": 8,
  "results": [
    {
      "id": 5,
      "job_seeker": {
        "id": 2,
        "full_name": "John Seeker",
        "email": "john@example.com",
        "mobile": "09123456789",
        "province": "Metro Manila",
        "skills": "Python, Django, REST API"
      },
      "job": {
        "id": 1,
        "title": "Senior Developer",
        "employer_name": "Tech Company",
        "category": "IT"
      },
      "status": "pending",
      "status_display": "Pending",
      "applied_at": "2024-04-20T15:30:00Z"
    }
  ]
}
```

#### Create New Application
```
POST /api/applications/
```

Requires authentication.

Request Body:
```json
{
  "job_id": 1
}
```

Response (201 Created):
```json
{
  "id": 6,
  "job_seeker": 2,
  "job": 1,
  "status": "pending",
  "status_display": "Pending",
  "applied_at": "2024-04-21T10:00:00Z"
}
```

#### Get Application Details
```
GET /api/applications/{id}/
```

Requires authentication.

#### List Applications for Job (Employer Only)
```
GET /api/applications/by_job/{job_id}/
```

Requires authentication as the job's employer.

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "bad_request",
  "message": "Invalid parameter value"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 409 Conflict
```json
{
  "message": "You have already applied for this job"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### 500 Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred.",
  "reference": "ABC12345"
}
```

---

## Examples

### JavaScript (Fetch)

List active jobs:
```javascript
fetch('/api/jobs/?page_size=20')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

Apply for a job (requires authentication):
```javascript
fetch('/api/applications/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // Include session cookies
  body: JSON.stringify({ job_id: 1 })
})
  .then(response => response.json())
  .then(data => console.log('Application created:', data))
  .catch(error => console.error('Error:', error));
```

### Python (Requests)

```python
import requests

# List jobs
response = requests.get('http://localhost:8000/api/jobs/', params={'page_size': 20})
jobs = response.json()

# Apply for a job (with session)
session = requests.Session()
session.auth = ('username', 'password')  # Or use login endpoint
response = session.post('http://localhost:8000/api/applications/', 
                       json={'job_id': 1})
if response.status_code == 201:
    print('Application created:', response.json())
```

### cURL

List jobs by province:
```bash
curl "http://localhost:8000/api/jobs/by_province/?province=Metro%20Manila"
```

Apply for a job:
```bash
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1}' \
  --cookie "sessionid=YOUR_SESSION_ID"
```

---

## Pagination

All list endpoints support pagination. Response includes:
- `count` - Total number of items
- `next` - URL to next page (if available)
- `previous` - URL to previous page (if available)
- `results` - Array of items on current page

Example:
```json
{
  "count": 156,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Field Descriptions

### Job Status
- `is_active` - Job post is active/public
- `is_approved` - Admin has approved the job post

### Application Status
- `pending` - Application awaiting employer review
- `accepted` - Employer has accepted the application
- `rejected` - Employer has rejected the application

### User Roles
- Job Seekers - Browse jobs and apply
- Employers - Post jobs and review applications
- Admins - Manage all content and moderate job posts

---

## WebSocket Support (Future)

Real-time notifications for application status changes will be added in future versions.

---

## Support

For issues or questions, contact: support@trabahoph.com
