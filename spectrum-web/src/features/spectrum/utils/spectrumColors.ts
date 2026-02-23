/**
 * Spectrum color utilities.
 * Uses blue-to-orange gradient for clear visual distinction.
 */

export type PoliticalLabel =
  | 'Far Left'
  | 'Left'
  | 'Slight Left'
  | 'Center'
  | 'Slight Right'
  | 'Right'
  | 'Far Right'

/**
 * Get political label from score (-1 to 1)
 */
export function getLabel(score: number): PoliticalLabel {
  if (score <= -0.6) return 'Far Left'
  if (score <= -0.3) return 'Left'
  if (score <= -0.1) return 'Slight Left'
  if (score <= 0.1) return 'Center'
  if (score <= 0.3) return 'Slight Right'
  if (score <= 0.6) return 'Right'
  return 'Far Right'
}

/**
 * Get color for a political score
 */
export function getColor(score: number): string {
  if (score <= -0.6) return '#1e40af' // Blue-800 - Far Left
  if (score <= -0.3) return '#2563eb' // Blue-600 - Left
  if (score <= -0.1) return '#3b82f6' // Blue-500 - Slight Left
  if (score <= 0.1) return '#64748b'  // Slate-500 - Center
  if (score <= 0.3) return '#f59e0b'  // Amber-500 - Slight Right
  if (score <= 0.6) return '#f97316'  // Orange-500 - Right
  return '#ea580c' // Orange-600 - Far Right
}

/**
 * Get Tailwind color class for a political score
 */
export function getColorClass(score: number): string {
  if (score <= -0.6) return 'bg-spectrum-far-left'
  if (score <= -0.3) return 'bg-spectrum-left'
  if (score <= -0.1) return 'bg-spectrum-center-left'
  if (score <= 0.1) return 'bg-spectrum-center'
  if (score <= 0.3) return 'bg-spectrum-center-right'
  if (score <= 0.6) return 'bg-spectrum-right'
  return 'bg-spectrum-far-right'
}

/**
 * Get text color class for a political score
 */
export function getTextColorClass(score: number): string {
  if (score <= -0.6) return 'text-spectrum-far-left'
  if (score <= -0.3) return 'text-spectrum-left'
  if (score <= -0.1) return 'text-spectrum-center-left'
  if (score <= 0.1) return 'text-spectrum-center'
  if (score <= 0.3) return 'text-spectrum-center-right'
  if (score <= 0.6) return 'text-spectrum-right'
  return 'text-spectrum-far-right'
}

/**
 * Convert score (-1 to 1) to percentage (0 to 100) for positioning
 */
export function scoreToPercent(score: number): number {
  return ((score + 1) / 2) * 100
}
