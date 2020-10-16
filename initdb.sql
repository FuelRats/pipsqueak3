-- Initialize database on first time DB container run via docker-compose.
-- See "Initialization scripts" at https://hub.docker.com/_/postgres for more info.
CREATE TABLE public.fact ( name character varying NOT NULL, lang character varying NOT NULL, message character varying NOT NULL, author character varying, CONSTRAINT fact_pkey PRIMARY KEY (name, lang));
INSERT INTO public.fact (name, lang, message, author) VALUES ('test', 'en', 'This is a test fact.', 'Shatt');
