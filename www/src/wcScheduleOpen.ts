/** Dispatched on `window` so any view (e.g. Hero) can open the schedule modal owned by Nav. */
export const WC_OPEN_FULL_SCHEDULE = "wc:openFullSchedule";

export function openFullWorldCupSchedule(): void {
  window.dispatchEvent(new CustomEvent(WC_OPEN_FULL_SCHEDULE));
}
