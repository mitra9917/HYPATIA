"use client";

import {
  resolveActiveStep,
  STEPPER_KEYS,
  STEPPER_LABELS,
  stageState,
  type StepperKey,
} from "@/lib/pipeline";
import type { Session } from "@/lib/types";

type Props = {
  session: Session;
  activeStep?: StepperKey;
  busy?: boolean;
};

export function PipelineStepper({ session, activeStep, busy }: Props) {
  const active = activeStep ?? resolveActiveStep(session);

  return (
    <nav className="pipeline-stepper" aria-label="Scientific loop progress">
      <ol>
        {STEPPER_KEYS.map((step) => {
          const state =
            busy && step === active ? "active" : stageState(step, active, session.status);
          return (
            <li key={step} className={`step step-${state}`} data-step={step}>
              <span className="step-dot" aria-hidden />
              <span className="step-label">{STEPPER_LABELS[step]}</span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
