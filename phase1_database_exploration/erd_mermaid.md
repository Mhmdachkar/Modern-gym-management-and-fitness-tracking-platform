# Gym Management System - Entity Relationship Diagram

```mermaid
erDiagram
    action_events {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        batch_id char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        user_id bigint unsigned NOT NULL
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        actionable_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        actionable_id bigint unsigned NOT NULL
        target_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        target_id bigint unsigned NOT NULL
        model_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        model_id bigint unsigned DEFAULT NULL
        fields text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        status varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'running'
        exception text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        original mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        changes mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    }

    availabilities {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        available_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        available_id bigint unsigned NOT NULL
        day_of_week enum('monday'
        start_time time NOT NULL
        end_time time NOT NULL
        is_available tinyint(1) NOT NULL DEFAULT '1'
        notes text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    cafes {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        path varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    checkins {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        user_id bigint unsigned NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    devices {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        device_id varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        serial_id varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        brand varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        user_id bigint unsigned NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    failed_jobs {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        uuid varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        connection text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        queue text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        payload longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        exception longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        failed_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    }

    freeze_logs {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        subscription_id bigint unsigned NOT NULL
        requested_days int NOT NULL
        actual_days_used int NOT NULL DEFAULT '0'
        frozen_at datetime NOT NULL
        unfrozen_at datetime DEFAULT NULL
        is_active tinyint(1) NOT NULL DEFAULT '1'
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    group_user {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        user_id bigint unsigned NOT NULL
        group_id bigint unsigned NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    groups {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        description text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        path varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        menu varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
    }

    images {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        path varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        studio_id bigint unsigned NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    instructors {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        bio text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        photo varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        price varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        capacity int DEFAULT NULL
        deleted_at timestamp NULL DEFAULT NULL
    }

    invoices {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        email varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        phone varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        date datetime NOT NULL
        invoice_number varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        due_date varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        sub_total varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        discount varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        total varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        items json NOT NULL
        user_id bigint unsigned NOT NULL
        invoiceable_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        invoiceable_id bigint unsigned NOT NULL
        deleted_at timestamp NULL DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    migrations {
        id PK int unsigned NOT NULL AUTO_INCREMENT
        migration varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        batch int NOT NULL
    }

    notifications {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        title varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        message varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        user_id bigint unsigned NOT NULL
        seen tinyint(1) DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    nova_field_attachments {
        id PK int unsigned NOT NULL AUTO_INCREMENT
        attachable_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        attachable_id bigint unsigned NOT NULL
        attachment varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        disk varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        url varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    nova_notifications {
        id PK char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        notifiable_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        notifiable_id bigint unsigned NOT NULL
        data text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        read_at timestamp NULL DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        deleted_at timestamp NULL DEFAULT NULL
    }

    nova_pending_field_attachments {
        id PK int unsigned NOT NULL AUTO_INCREMENT
        draft_id varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        attachment varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        disk varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    o_t_p_s {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        email varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        otp varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    packages {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        price varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        validity_days int NOT NULL DEFAULT '0'
        description varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        model varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        days int NOT NULL DEFAULT '0'
        with_partner tinyint(1) NOT NULL DEFAULT '0'
        is_member tinyint(1) NOT NULL DEFAULT '0'
        model_id bigint unsigned DEFAULT NULL
        capacity int DEFAULT NULL
    }

    password_resets {
        email varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        token varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at timestamp NULL DEFAULT NULL
    }

    personal_access_tokens {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        tokenable_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        tokenable_id bigint unsigned NOT NULL
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        token varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        abilities text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        last_used_at timestamp NULL DEFAULT NULL
        expires_at timestamp NULL DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    plans {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        price varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        freezing_days int NOT NULL DEFAULT '0'
        active tinyint(1) NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        days varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        shots int NOT NULL DEFAULT '0'
    }

    post_photos {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        post_id bigint unsigned NOT NULL
        path varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        is_cover tinyint(1) NOT NULL DEFAULT '0'
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    posts {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        title varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        body text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        status enum('draft'
        published_at timestamp NULL DEFAULT NULL
        user_id bigint unsigned NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    reservations {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        user_id bigint unsigned NOT NULL
        start_datetime datetime NOT NULL
        end_datetime datetime NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        price varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        payment_method varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        reservable_type varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        reservable_id bigint unsigned NOT NULL
        status varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending'
        instructor_id bigint unsigned DEFAULT NULL
        instructor_name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        studio_id bigint unsigned DEFAULT NULL
        studio_name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        notes text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        balance int NOT NULL DEFAULT '0'
    }

    scheduled_sessions {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        user_id bigint unsigned NOT NULL
        package_id bigint unsigned NOT NULL
        package_name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        package_price varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        package_days int NOT NULL
        model varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        model_id bigint unsigned NOT NULL
        model_name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        with_partner tinyint(1) NOT NULL DEFAULT '0'
        payment_method varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        date date NOT NULL
        start_time time NOT NULL
        end_time time NOT NULL
        session_number int NOT NULL
        status enum('scheduled'
        reservation_id bigint unsigned DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
    }

    studios {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        description varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        price varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        capacity int DEFAULT NULL
        photo varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
    }

    subscriptions {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        user_id bigint unsigned NOT NULL
        start_date datetime NOT NULL
        end_date datetime NOT NULL
        plan_id bigint unsigned NOT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        price varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        status varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending'
        notes text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        freeze_days_used int NOT NULL DEFAULT '0'
        freeze_attempts int NOT NULL DEFAULT '0'
        frozen_until date DEFAULT NULL
        has_discount tinyint(1) NOT NULL DEFAULT '0'
        discount_amount decimal(8
    }

    telescope_entries {
        sequence PK bigint unsigned NOT NULL AUTO_INCREMENT
        uuid char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        batch_id char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        family_hash varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        should_display_on_index tinyint(1) NOT NULL DEFAULT '1'
        type varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        content longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        created_at datetime DEFAULT NULL
    }

    telescope_entries_tags {
        entry_uuid char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        tag varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
    }

    telescope_monitoring {
        tag PK varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
    }

    users {
        id PK bigint unsigned NOT NULL AUTO_INCREMENT
        name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        email varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        email_verified_at timestamp NULL DEFAULT NULL
        remember_token varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        created_at timestamp NULL DEFAULT NULL
        updated_at timestamp NULL DEFAULT NULL
        phone varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        dob date DEFAULT NULL
        photo varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        weight varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        height varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
        notes text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    }

    checkins ||--o{ users : "user_id -> id"
    devices ||--o{ users : "user_id -> id"
    freeze_logs ||--o{ subscriptions : "subscription_id -> id"
    images ||--o{ studios : "studio_id -> id"
    invoices ||--o{ users : "user_id -> id"
    notifications ||--o{ users : "user_id -> id"
    post_photos ||--o{ posts : "post_id -> id"
    posts ||--o{ users : "user_id -> id"
    reservations ||--o{ instructors : "instructor_id -> id"
    reservations ||--o{ studios : "studio_id -> id"
    reservations ||--o{ users : "user_id -> id"
    scheduled_sessions ||--o{ packages : "package_id -> id"
    scheduled_sessions ||--o{ reservations : "reservation_id -> id"
    scheduled_sessions ||--o{ users : "user_id -> id"
    subscriptions ||--o{ plans : "plan_id -> id"
    subscriptions ||--o{ users : "user_id -> id"
    telescope_entries_tags ||--o{ telescope_entries : "entry_uuid -> uuid"
```
