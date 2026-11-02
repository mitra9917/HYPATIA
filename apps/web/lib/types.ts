export type Hypothesis = {
  id: string;
  form_latex: string;
  form_plain: string;
  params: Record<string, number>;
  train_score: number;
  heldout_score: number;
  r2_heldout: number;
  status: string;
  param_ci?: Record<string, [number, number]>;
};

export type ImaginationFrame = {
  hypothesis_id: string;
  predicted_description: string;
  audit_error_m: number;
  ghost_polyline: { t: number; x_m: number; y_m: number; angle_rad: number }[];
  source: string;
};

export type SessionEventPayload = {
  event?: string;
  session_id?: string;
  stage?: string;
  status?: string;
  message?: string;
  error?: string;
  pipeline_stages?: string[];
};

export type Session = {
  id: string;
  status: string;
  mode: string;
  video_file_id?: string | null;
  meta_file_ids?: string[];
  scene?: {
    narration: string;
    sam_prompts: string[];
    suggested_domain: string;
    candidate_variables?: string[];
    objects?: { name: string; why_interesting: string }[];
  } | null;
  hypotheses: Hypothesis[];
  experiment?: {
    instruction: string;
    rationale: string;
    expected_outcomes: Record<string, string>;
  } | null;
  experiment_result?: {
    notes: string;
    observed_period_ratio?: number | null;
    supports_winner?: boolean | null;
  } | null;
  law_gate?: {
    ok: boolean;
    held_out_winner?: boolean;
    g_in_range?: boolean;
    reasons?: string[];
  } | null;
  imagination: ImaginationFrame[];
  notebook?: {
    markdown: string;
    law_latex: string;
    params: Record<string, number>;
    error_bars: Record<string, number>;
  } | null;
  events: SessionEventPayload[];
  meta_calls: Record<string, unknown>[];
  tracks?: {
    object_name: string;
    sam_prompt: string;
    points: { t: number; x_m?: number; y_m?: number; angle_rad?: number }[];
    mask_frames: {
      frame_index: number;
      t_s: number;
      bbox_norm: { x: number; y: number; w: number; h: number };
    }[];
    source: string;
    frame_cost?: { frames_billed_estimate: number; scientific_fps: number } | null;
  }[];
  error?: string | null;
  upload_consent?: boolean;
  library_hint?: { message?: string; matches?: { law_latex: string; session_id: string }[] } | null;
};

export type HealthInfo = {
  ok: boolean;
  service?: string;
  fixture_mode?: boolean;
  replay_mode?: boolean;
  fixture_record?: boolean;
  session_store?: string;
  ops?: {
    ops_mode?: string;
    ops_mode_override?: string | null;
    fixture_mode?: boolean;
    hybrid_fallback_enabled?: boolean;
    meta_key_present?: boolean;
  };
  pipeline_stages?: string[];
  model_router?: {
    use_contributor?: boolean;
    observer?: string;
  };
  contributor_policy?: {
    meta_use_contributor?: boolean;
    observer_spark_tier?: string;
    policy?: string;
  };
};

export type LawSummary = {
  session_id: string;
  law_latex: string;
  params: Record<string, number>;
  mode: string;
  stages_completed?: number;
  error_bars?: Record<string, number>;
};
