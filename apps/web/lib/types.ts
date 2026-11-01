export type Hypothesis = {
  id: string;
  form_latex: string;
  form_plain: string;
  params: Record<string, number>;
  train_score: number;
  heldout_score: number;
  r2_heldout: number;
  status: string;
};

export type ImaginationFrame = {
  hypothesis_id: string;
  predicted_description: string;
  audit_error_m: number;
  ghost_polyline: { t: number; x_m: number; y_m: number; angle_rad: number }[];
  source: string;
};

export type Session = {
  id: string;
  status: string;
  mode: string;
  scene?: {
    narration: string;
    sam_prompts: string[];
    suggested_domain: string;
  } | null;
  hypotheses: Hypothesis[];
  experiment?: {
    instruction: string;
    rationale: string;
    expected_outcomes: Record<string, string>;
  } | null;
  imagination: ImaginationFrame[];
  notebook?: {
    markdown: string;
    law_latex: string;
    params: Record<string, number>;
    error_bars: Record<string, number>;
  } | null;
  events: { stage: string; message: string }[];
  meta_calls: Record<string, unknown>[];
  error?: string | null;
};
