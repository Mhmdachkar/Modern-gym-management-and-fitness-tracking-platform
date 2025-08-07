# Phase 1: Database Understanding & Exploration — COMPLETED ✅

## Overview
This phase focused strictly on restoring/exploring the SQL dump and documenting the schema and relationships (ERD). All outputs below are generated directly from the original dump `threesity_final.dump`.

## ✅ Completed Scope (Phase 1)
- 1. Restore and explore the SQL dump (MySQL) and generate ERD
- 3. Document schema and map relationships between members, plans, coaches, sessions

Note: Step 2 (data profiling/CSV analysis) is handled separately in Phase 2 and is not part of this folder.

## 🗄️ Database Source
- File: `threesity_final.dump` (167MB)
- Engine: MySQL

## 📊 Schema Summary (from dump)
- Total Tables: 32
- Total Columns: 271
- Primary Keys: 30
- Foreign Keys: 17

## 🔗 Key Business Entities & Relationships
- Members: `users`
- Coaches: `instructors`
- Subscriptions: `subscriptions`
- Sessions: `scheduled_sessions`
- Plans: `plans`
- Packages: `packages`

Core relationships:
- `users` (1) → (many) `subscriptions`
- `users` (1) → (many) `scheduled_sessions`
- `instructors` (1) → (many) `scheduled_sessions`
- `packages` (1) → (many) `scheduled_sessions`
- `plans` (1) → (many) `subscriptions`

## 📁 Outputs (Phase 1 artifacts only)
- `schema_report.json` — Full parsed schema: tables, columns, PKs, FKs, summary
- `key_entities.json` — Mapping of tables to business entities
- `erd_mermaid.md` — ERD in Mermaid format
- `erd_text.md` — Detailed ERD in readable text
- `erd_summary.md` — Concise business-focused ERD summary

## 🧭 Business Flow (high-level)
1. Users register in `users`
2. Users subscribe to `plans` → records in `subscriptions`
3. Users book sessions via `scheduled_sessions` (linked to `packages` and `instructors`)

## 📦 What’s intentionally NOT in Phase 1
- CSVs and exploratory profiling notebooks
- Any Streamlit/UI/dashboard code
- Derived or simulated datasets

These belong to Phase 2 and are available under `phase2_data/`.

## ✅ Status
Phase 1 is complete and clean. All files in this directory are strictly necessary for understanding the database and documenting its schema and relationships. 