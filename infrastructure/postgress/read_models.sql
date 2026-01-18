CREATE SCHEMA IF NOT EXISTS skinny_hedgehog_read_models;

CREATE USER skinny_hedgehog_pg_rms WITH PASSWORD 'S8cure!Passw0rd#2024';

GRANT USAGE, CREATE ON SCHEMA skinny_hedgehog_read_models TO skinny_hedgehog_pg_rms;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA skinny_hedgehog_read_models TO skinny_hedgehog_pg_rms;

ALTER ROLE skinny_hedgehog_pg_rms SET search_path TO skinny_hedgehog_read_models;

CREATE TABLE IF NOT EXISTS skinny_hedgehog_read_models.ledger_state (
  ID_ledger VARCHAR(255) PRIMARY KEY,
  initial_balance NUMERIC,
  current_balance NUMERIC
);

SELECT * FROM skinny_hedgehog_read_models.ledger_state;