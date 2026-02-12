/**
 * 간단한 API 응답 캐시 유틸리티
 *
 * 동일한 API 요청을 여러 번 보내지 않도록 메모리에 캐싱합니다.
 * TTL(Time To Live)을 설정하여 일정 시간 후 캐시를 무효화합니다.
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class ApiCache {
  private cache: Map<string, CacheEntry<any>>;

  constructor() {
    this.cache = new Map();
  }

  /**
   * 캐시에서 데이터 가져오기
   * @param key 캐시 키
   * @returns 캐시된 데이터 또는 null
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // TTL 체크
    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      // 만료된 캐시 삭제
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * 캐시에 데이터 저장
   * @param key 캐시 키
   * @param data 저장할 데이터
   * @param ttl TTL (밀리초, 기본값: 5분)
   */
  set<T>(key: string, data: T, ttl: number = 5 * 60 * 1000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  /**
   * 특정 키의 캐시 삭제
   * @param key 캐시 키
   */
  delete(key: string): void {
    this.cache.delete(key);
  }

  /**
   * 모든 캐시 삭제
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * 캐시 크기 반환
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * 패턴과 일치하는 모든 캐시 삭제
   * @param pattern 정규식 패턴
   */
  deletePattern(pattern: RegExp): void {
    const keysToDelete: string[] = [];

    this.cache.forEach((_, key) => {
      if (pattern.test(key)) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
  }
}

// 싱글톤 인스턴스 생성
export const apiCache = new ApiCache();

/**
 * API 요청을 캐싱하는 헬퍼 함수
 *
 * @param key 캐시 키
 * @param fetcher 데이터를 가져오는 함수
 * @param ttl TTL (밀리초, 기본값: 5분)
 * @returns 캐시된 데이터 또는 새로 가져온 데이터
 */
export async function cachedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl?: number
): Promise<T> {
  // 캐시에서 먼저 확인
  const cached = apiCache.get<T>(key);
  if (cached !== null) {
    console.log(`[Cache HIT] ${key}`);
    return cached;
  }

  // 캐시 미스 - 새로 가져오기
  console.log(`[Cache MISS] ${key}`);
  const data = await fetcher();

  // 캐시에 저장
  apiCache.set(key, data, ttl);

  return data;
}

export default apiCache;
