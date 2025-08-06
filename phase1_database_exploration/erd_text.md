# Gym Management System - Entity Relationship Diagram

## Database Overview
- **Total Tables**: 32
- **Total Columns**: 271
- **Primary Keys**: 30
- **Foreign Keys**: 17

## Entity Relationships

### Members
- **group_user** (5 columns)
  - Primary Keys: id
- **users** (13 columns)
  - Primary Keys: id

### Coaches
- **instructors** (9 columns)
  - Primary Keys: id

### Subscriptions
- **subscriptions** (15 columns)
  - Primary Keys: id
  - Foreign Keys: 2 relationships

### Sessions
- **scheduled_sessions** (19 columns)
  - Primary Keys: id
  - Foreign Keys: 3 relationships

### Plans
- **packages** (13 columns)
  - Primary Keys: id
- **plans** (9 columns)
  - Primary Keys: id

### System
- **action_events** (17 columns)
  - Primary Keys: id
- **availabilities** (10 columns)
  - Primary Keys: id
- **cafes** (4 columns)
  - Primary Keys: id
- **checkins** (4 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **devices** (7 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **failed_jobs** (7 columns)
  - Primary Keys: id
- **freeze_logs** (9 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **groups** (7 columns)
  - Primary Keys: id
- **images** (5 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **invoices** (17 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **migrations** (3 columns)
  - Primary Keys: id
- **notifications** (7 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **nova_field_attachments** (8 columns)
  - Primary Keys: id
- **nova_notifications** (9 columns)
  - Primary Keys: id
- **nova_pending_field_attachments** (6 columns)
  - Primary Keys: id
- **o_t_p_s** (5 columns)
  - Primary Keys: id
- **password_resets** (3 columns)
- **personal_access_tokens** (10 columns)
  - Primary Keys: id
- **post_photos** (6 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **posts** (8 columns)
  - Primary Keys: id
  - Foreign Keys: 1 relationships
- **reservations** (17 columns)
  - Primary Keys: id
  - Foreign Keys: 3 relationships
- **studios** (8 columns)
  - Primary Keys: id
- **telescope_entries** (8 columns)
  - Primary Keys: sequence
- **telescope_entries_tags** (2 columns)
  - Foreign Keys: 1 relationships
- **telescope_monitoring** (1 columns)
  - Primary Keys: tag

## Key Relationships

### checkins
- `user_id` → `users.id`

### devices
- `user_id` → `users.id`

### freeze_logs
- `subscription_id` → `subscriptions.id`

### images
- `studio_id` → `studios.id`

### invoices
- `user_id` → `users.id`

### notifications
- `user_id` → `users.id`

### post_photos
- `post_id` → `posts.id`

### posts
- `user_id` → `users.id`

### reservations
- `instructor_id` → `instructors.id`
- `studio_id` → `studios.id`
- `user_id` → `users.id`

### scheduled_sessions
- `package_id` → `packages.id`
- `reservation_id` → `reservations.id`
- `user_id` → `users.id`

### subscriptions
- `plan_id` → `plans.id`
- `user_id` → `users.id`

### telescope_entries_tags
- `entry_uuid` → `telescope_entries.uuid`

