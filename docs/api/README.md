# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## Modules

| Module         | Prefix              | Status   |
|----------------|---------------------|----------|
| Auth           | `/auth`             | Scaffold |
| Users          | `/users`            | Scaffold |
| Roles          | `/roles`            | Scaffold |
| Brands         | `/brands`           | Scaffold |
| Territories    | `/territories`      | Scaffold |
| Vendors        | `/vendors`          | Scaffold |
| Products       | `/products`         | Scaffold |
| Inventory      | `/inventory`        | Scaffold |
| Orders         | `/orders`           | Scaffold |
| Dispatch       | `/dispatch`         | Scaffold |
| Reports        | `/reports`          | Scaffold |
| Analytics      | `/analytics`        | Scaffold |
| Notifications  | `/notifications`    | Scaffold |
| Uploads        | `/uploads`          | Scaffold |
| GPS            | `/gps`              | Scaffold |
| Activity Logs  | `/activity-logs`    | Scaffold |
| Settings       | `/settings`         | Scaffold |

## Response Format

```json
{
  "success": true,
  "message": "OK",
  "data": {}
}
```

## Authentication

All protected endpoints require:

```
Authorization: Bearer <access_token>
```
