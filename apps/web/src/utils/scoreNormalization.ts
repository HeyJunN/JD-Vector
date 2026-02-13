/**
 * scoreNormalization - 점수 정규화 유틸리티
 *
 * 백엔드에서 0-1 범위 또는 0-100 범위로 혼용되어 오는 점수를
 * 0-100 정수 범위로 통일하는 함수 모음
 */

/**
 * 0-1 또는 0-100 범위의 점수를 자동 판별하여 0-100 정수로 변환
 * 유효하지 않은 값(NaN, 숫자 아님)은 0 반환
 */
export function normalizeScore(score: unknown): number {
  if (typeof score !== 'number' || isNaN(score)) {
    return 0;
  }
  const normalized = score <= 1 ? Math.round(score * 100) : Math.round(score);
  // 0-100 사이로 클램핑
  return Math.max(0, Math.min(100, normalized));
}
