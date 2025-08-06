# Gym Management System - Key Entity Relationships

## Core Business Entities

### 1. Members (Users)
- **users** - Main user/member table
- **group_user** - User group associations

### 2. Coaches (Instructors)
- **instructors** - Coach/trainer profiles

### 3. Subscriptions & Plans
- **subscriptions** - Member subscriptions
- **packages** - Training packages
- **plans** - Membership plans

### 4. Sessions
- **scheduled_sessions** - Booked training sessions

## Key Relationships

```
users (1) ←→ (many) subscriptions
users (1) ←→ (many) scheduled_sessions
instructors (1) ←→ (many) scheduled_sessions
packages (1) ←→ (many) scheduled_sessions
plans (1) ←→ (many) subscriptions
```

## Data Volume Summary
- **339** registered users
- **7** active instructors
- **525** subscription records
- **33** scheduled sessions
- **25** training packages
- **8** membership plans

## Business Flow
1. Users register in the `users` table
2. Users subscribe to `plans` or purchase `packages`
3. Subscriptions are recorded in the `subscriptions` table
4. Users book sessions with instructors via `scheduled_sessions`
5. Sessions are linked to specific packages and instructors
