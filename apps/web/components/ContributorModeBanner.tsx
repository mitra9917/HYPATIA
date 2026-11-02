"use client";

type Props = {
  active: boolean;
  tier?: string;
};

/** Shown when META_USE_CONTRIBUTOR routes Observer Spark to the Contributor variant. */
export function ContributorModeBanner({ active, tier }: Props) {
  if (!active) {
    return null;
  }

  return (
    <div className="contributor-banner shell" role="status">
      <strong>Spark Contributor mode</strong>
      <span>
        Observer calls use <code>muse-spark-1.3-contributor</code> ({tier ?? "contributor"}) for cost
        routing. Wonder, Image, and SAM stay on standard models. Do not enable for sensitive or
        user-owned IP you would not share with contributor training.
      </span>
    </div>
  );
}
