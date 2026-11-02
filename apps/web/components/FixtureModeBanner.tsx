"use client";

type Props = {
  fixtureMode: boolean;
  fixtureRecord?: boolean;
};

/** Visible when API is in fixture replay (demo / CI / offline judges). */
export function FixtureModeBanner({ fixtureMode, fixtureRecord }: Props) {
  if (!fixtureMode) {
    return null;
  }

  return (
    <div className="fixture-banner shell" role="status">
      <strong>Replay mode</strong>
      <span>
        Observer and SAM responses are loaded from repo fixtures (<code>FIXTURE_MODE=true</code>
        ). Set <code>FIXTURE_MODE=false</code> with a Meta API key for live calls.
      </span>
      {fixtureRecord ? (
        <span className="meta">Fixture recorder active — live observe/measure will update data/fixtures/.</span>
      ) : null}
    </div>
  );
}
