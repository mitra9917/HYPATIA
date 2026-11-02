-- HYPATIA ARCHITECTURE §5 — initial schema (P1.15 / Playbook #21, issue #55)

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'upload',
    mode TEXT NOT NULL DEFAULT 'fixture',
    domain_hint TEXT,
    document JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions (status);
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions (updated_at DESC);

CREATE TABLE IF NOT EXISTS observations (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    scene_brief JSONB,
    model TEXT,
    tokens_used INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tracks (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    object_name TEXT NOT NULL,
    sam_prompt TEXT NOT NULL,
    trajectory_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    mask_frames_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    metres_per_pixel DOUBLE PRECISION,
    calibration_method TEXT,
    source TEXT,
    trajectory_csv TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, sam_prompt)
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT NOT NULL,
    session_id TEXT NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    form_latex TEXT NOT NULL,
    form_plain TEXT,
    params_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    train_score DOUBLE PRECISION,
    heldout_score DOUBLE PRECISION,
    status TEXT,
    PRIMARY KEY (session_id, id)
);

CREATE TABLE IF NOT EXISTS experiments (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    instruction TEXT,
    rationale TEXT,
    expected_json JSONB,
    result_json JSONB,
    info_gain DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS imagination_audits (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    hypothesis_id TEXT,
    frame_t DOUBLE PRECISION,
    predicted_description TEXT,
    audit_error_m DOUBLE PRECISION,
    ghost_polyline JSONB,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tools (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    source TEXT,
    tests_json JSONB,
    adopted_at TIMESTAMPTZ,
    session_origin TEXT REFERENCES sessions (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS laws (
    id BIGSERIAL PRIMARY KEY,
    form_latex TEXT NOT NULL,
    params_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    domain_tags TEXT[] DEFAULT '{}',
    evidence_session_ids TEXT[] DEFAULT '{}',
    confidence DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notebooks (
    session_id TEXT PRIMARY KEY REFERENCES sessions (id) ON DELETE CASCADE,
    markdown TEXT,
    law_latex TEXT,
    params_json JSONB,
    error_bars_json JSONB,
    export_uri TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
