"""Postgres-backed session store (ARCHITECTURE §5)."""

from __future__ import annotations

import json
import threading
from typing import Any

import psycopg

from .models import Session


class PostgresSessionStore:
    """Persist full Session document + normalized rows for ARCHITECTURE §5 tables."""

    def __init__(self, database_url: str) -> None:
        self._url = database_url
        self._lock = threading.Lock()

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self._url)

    def put(self, session: Session) -> Session:
        doc = session.model_dump(mode="json")
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sessions (
                        id, status, source_type, mode, domain_hint, document, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, now())
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        source_type = EXCLUDED.source_type,
                        mode = EXCLUDED.mode,
                        domain_hint = EXCLUDED.domain_hint,
                        document = EXCLUDED.document,
                        updated_at = now()
                    """,
                    (
                        session.id,
                        session.status.value if hasattr(session.status, "value") else str(session.status),
                        session.source_type,
                        session.mode,
                        session.domain_hint,
                        json.dumps(doc),
                    ),
                )
                self._sync_children(cur, session, doc)
            conn.commit()
        return session

    def _sync_children(self, cur: psycopg.Cursor, session: Session, doc: dict[str, Any]) -> None:
        sid = session.id
        cur.execute("DELETE FROM tracks WHERE session_id = %s", (sid,))
        for t in session.tracks:
            cur.execute(
                """
                INSERT INTO tracks (
                    session_id, object_name, sam_prompt, trajectory_json, mask_frames_json,
                    metres_per_pixel, calibration_method, source, trajectory_csv
                ) VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s)
                ON CONFLICT (session_id, sam_prompt) DO UPDATE SET
                    object_name = EXCLUDED.object_name,
                    trajectory_json = EXCLUDED.trajectory_json,
                    mask_frames_json = EXCLUDED.mask_frames_json,
                    metres_per_pixel = EXCLUDED.metres_per_pixel,
                    calibration_method = EXCLUDED.calibration_method,
                    source = EXCLUDED.source,
                    trajectory_csv = EXCLUDED.trajectory_csv
                """,
                (
                    sid,
                    t.object_name,
                    t.sam_prompt,
                    json.dumps([p.model_dump(mode="json") for p in t.points]),
                    json.dumps([m.model_dump(mode="json") for m in t.mask_frames]),
                    t.metres_per_pixel,
                    t.calibration_method,
                    t.source,
                    t.trajectory_csv,
                ),
            )

        if session.scene:
            cur.execute("DELETE FROM observations WHERE session_id = %s", (sid,))
            cur.execute(
                """
                INSERT INTO observations (session_id, scene_brief, model)
                VALUES (%s, %s::jsonb, %s)
                """,
                (sid, json.dumps(session.scene.model_dump(mode="json")), "observer"),
            )

        cur.execute("DELETE FROM hypotheses WHERE session_id = %s", (sid,))
        for h in session.hypotheses:
            cur.execute(
                """
                INSERT INTO hypotheses (
                    id, session_id, form_latex, form_plain, params_json,
                    train_score, heldout_score, status
                ) VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s)
                """,
                (
                    h.id,
                    sid,
                    h.form_latex,
                    h.form_plain,
                    json.dumps(h.params),
                    h.train_score,
                    h.heldout_score,
                    h.status,
                ),
            )

        if session.experiment:
            cur.execute("DELETE FROM experiments WHERE session_id = %s", (sid,))
            cur.execute(
                """
                INSERT INTO experiments (session_id, instruction, rationale, expected_json)
                VALUES (%s, %s, %s, %s::jsonb)
                """,
                (
                    sid,
                    session.experiment.instruction,
                    session.experiment.rationale,
                    json.dumps(session.experiment.expected_outcomes),
                ),
            )

        cur.execute("DELETE FROM imagination_audits WHERE session_id = %s", (sid,))
        for frame in session.imagination:
            cur.execute(
                """
                INSERT INTO imagination_audits (
                    session_id, hypothesis_id, predicted_description,
                    audit_error_m, ghost_polyline, source
                ) VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    sid,
                    frame.hypothesis_id,
                    frame.predicted_description,
                    frame.audit_error_m,
                    json.dumps(frame.ghost_polyline),
                    frame.source,
                ),
            )

        if session.notebook:
            cur.execute(
                """
                INSERT INTO notebooks (
                    session_id, markdown, law_latex, params_json, error_bars_json, updated_at
                ) VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, now())
                ON CONFLICT (session_id) DO UPDATE SET
                    markdown = EXCLUDED.markdown,
                    law_latex = EXCLUDED.law_latex,
                    params_json = EXCLUDED.params_json,
                    error_bars_json = EXCLUDED.error_bars_json,
                    updated_at = now()
                """,
                (
                    sid,
                    session.notebook.markdown,
                    session.notebook.law_latex,
                    json.dumps(session.notebook.params),
                    json.dumps(session.notebook.error_bars),
                ),
            )

    def get(self, session_id: str) -> Session | None:
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT document FROM sessions WHERE id = %s", (session_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return Session.model_validate(row[0])

    def list_ids(self) -> list[str]:
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM sessions ORDER BY updated_at DESC")
                return [r[0] for r in cur.fetchall()]
