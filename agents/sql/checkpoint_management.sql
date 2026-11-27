-- PostgreSQL checkpoint management queries for LangGraph's PostgresSaver.
-- Run these statements only against the database configured by POSTGRES_DB.

/* List tables in the public schema. */
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- LangGraph/PostgresSaver tables:
-- checkpoint_migrations tracks the applied database schema migration versions.
SELECT * FROM checkpoint_migrations;
-- checkpoint_blobs stores serialized channel values used by checkpoints.
SELECT * FROM checkpoint_blobs;
-- checkpoints stores the checkpoint snapshots and their JSONB metadata.
SELECT * FROM checkpoints;
-- checkpoint_writes stores pending task writes associated with checkpoints.
SELECT * FROM checkpoint_writes;

/* Delete all persisted checkpoint data. */
-- This is destructive: it intentionally removes blob and write data as well.
-- checkpoint_migrations is left intact so LangGraph/PostgresSaver retains
-- the database schema migration state.
BEGIN;

DELETE FROM checkpoint_writes;
DELETE FROM checkpoint_blobs;
DELETE FROM checkpoints;

COMMIT;

/* Search checkpoints by the UTC created_at value supplied in agent invocation metadata. */
SELECT *
FROM checkpoints
WHERE metadata->>'created_at' ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?[+-][0-9]{2}:[0-9]{2}$'
  AND (metadata->>'created_at')::timestamptz >= '2026-11-27T00:00:00+00:00'::timestamptz
  AND (metadata->>'created_at')::timestamptz <  '2026-11-28T00:00:00+00:00'::timestamptz
ORDER BY (metadata->>'created_at')::timestamptz DESC;
