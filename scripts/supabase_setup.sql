-- ============================================================================
-- JD-Vector: Supabase Database Setup for RAG Pipeline
-- Phase 3: pgvector 확장 및 벡터 저장소 설정
-- ============================================================================
-- 실행 순서: Supabase SQL Editor에서 이 스크립트 전체를 복사하여 실행
-- ============================================================================

-- ============================================================================
-- 1. pgvector 확장 활성화
-- ============================================================================
-- 이 확장이 있어야 vector 타입과 유사도 연산자를 사용할 수 있습니다.

CREATE EXTENSION IF NOT EXISTS vector;

-- UUID 생성 함수 (이미 활성화되어 있을 수 있음)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 2. documents 테이블: 원본 문서 메타데이터 저장
-- ============================================================================
-- 업로드된 PDF의 기본 정보를 저장합니다.

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL UNIQUE,  -- 백엔드에서 생성한 파일 ID
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('resume', 'job_description')),

    -- 원본 텍스트 (정제 전/후)
    raw_text TEXT,
    cleaned_text TEXT,

    -- 문서 통계
    word_count INTEGER DEFAULT 0,
    char_count INTEGER DEFAULT 0,
    page_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,  -- 청크 개수 (나중에 업데이트)

    -- PDF 메타데이터
    language TEXT DEFAULT 'unknown',
    author TEXT,
    title TEXT,

    -- 상태 관리
    embedding_status TEXT DEFAULT 'pending' CHECK (embedding_status IN ('pending', 'processing', 'completed', 'failed')),

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스: file_id로 빠른 조회
CREATE INDEX IF NOT EXISTS idx_documents_file_id ON documents(file_id);
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);
CREATE INDEX IF NOT EXISTS idx_documents_embedding_status ON documents(embedding_status);

-- ============================================================================
-- 3. document_chunks 테이블: 청크별 임베딩 저장
-- ============================================================================
-- 문서를 의미 단위로 분할한 청크와 벡터 임베딩을 저장합니다.

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    file_id UUID NOT NULL,  -- documents 테이블의 file_id (조인 없이 빠른 조회용)

    -- 청크 정보
    chunk_index INTEGER NOT NULL,  -- 문서 내 청크 순서 (0부터 시작)
    content TEXT NOT NULL,         -- 청크 텍스트 내용

    -- 섹션 메타데이터 (이력서 섹션 구분용)
    section_type TEXT,  -- 'experience', 'skills', 'education', 'summary', 'requirements', 'benefits' 등

    -- 청크 통계
    char_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,  -- 임베딩 모델 토큰 수 (비용 계산용)

    -- 벡터 임베딩 (OpenAI text-embedding-3-small: 1536차원)
    embedding vector(1536),

    -- 임베딩 메타데이터
    embedding_model TEXT DEFAULT 'text-embedding-3-small',

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크 제약: 같은 문서 내 청크 인덱스 중복 방지
    UNIQUE(document_id, chunk_index)
);

-- 인덱스: 빠른 조회용
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_file_id ON document_chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_section_type ON document_chunks(section_type);

-- 벡터 인덱스: 코사인 유사도 검색 최적화 (IVFFlat 사용)
-- 참고: 데이터가 충분히 쌓인 후(1000개 이상) 인덱스 재생성 권장
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================================================
-- 4. updated_at 자동 갱신 트리거
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. match_documents: 유사도 검색 RPC 함수
-- ============================================================================
-- 주어진 쿼리 벡터와 가장 유사한 청크들을 반환합니다.
-- 백엔드에서 supabase.rpc('match_documents', {...})로 호출합니다.

CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),   -- 검색 쿼리 벡터
    match_count INT DEFAULT 10,     -- 반환할 최대 결과 수
    filter_file_type TEXT DEFAULT NULL,  -- 파일 타입 필터 ('resume' 또는 'job_description')
    filter_file_id UUID DEFAULT NULL,    -- 특정 파일 ID로 필터
    similarity_threshold FLOAT DEFAULT 0.0  -- 최소 유사도 임계값
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    file_id UUID,
    chunk_index INT,
    content TEXT,
    section_type TEXT,
    file_type TEXT,
    filename TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.file_id,
        dc.chunk_index,
        dc.content,
        dc.section_type,
        d.file_type,
        d.filename,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE
        dc.embedding IS NOT NULL
        AND (filter_file_type IS NULL OR d.file_type = filter_file_type)
        AND (filter_file_id IS NULL OR dc.file_id = filter_file_id)
        AND (1 - (dc.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================================
-- 6. match_documents_by_file: 두 문서 간 청크별 유사도 계산
-- ============================================================================
-- 이력서와 채용공고 간의 매칭에 사용됩니다.
-- 각 이력서 청크에 대해 가장 유사한 JD 청크를 찾습니다.

CREATE OR REPLACE FUNCTION match_documents_by_file(
    resume_file_id UUID,           -- 이력서 파일 ID
    jd_file_id UUID,               -- 채용공고 파일 ID
    top_k INT DEFAULT 3            -- 각 청크당 반환할 매칭 수
)
RETURNS TABLE (
    resume_chunk_id UUID,
    resume_chunk_index INT,
    resume_content TEXT,
    resume_section_type TEXT,
    jd_chunk_id UUID,
    jd_chunk_index INT,
    jd_content TEXT,
    jd_section_type TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.id AS resume_chunk_id,
        rc.chunk_index AS resume_chunk_index,
        rc.content AS resume_content,
        rc.section_type AS resume_section_type,
        jc.id AS jd_chunk_id,
        jc.chunk_index AS jd_chunk_index,
        jc.content AS jd_content,
        jc.section_type AS jd_section_type,
        1 - (rc.embedding <=> jc.embedding) AS similarity
    FROM document_chunks rc
    CROSS JOIN LATERAL (
        SELECT
            dc.id,
            dc.chunk_index,
            dc.content,
            dc.section_type,
            dc.embedding
        FROM document_chunks dc
        WHERE dc.file_id = jd_file_id
            AND dc.embedding IS NOT NULL
        ORDER BY dc.embedding <=> rc.embedding
        LIMIT top_k
    ) jc
    WHERE rc.file_id = resume_file_id
        AND rc.embedding IS NOT NULL
    ORDER BY rc.chunk_index, similarity DESC;
END;
$$;

-- ============================================================================
-- 7. calculate_overall_similarity: 전체 문서 유사도 계산
-- ============================================================================
-- 두 문서 간의 전체적인 유사도 점수를 계산합니다.
-- 평균 임베딩 간의 코사인 유사도를 반환합니다.

CREATE OR REPLACE FUNCTION calculate_overall_similarity(
    file_id_a UUID,
    file_id_b UUID
)
RETURNS FLOAT
LANGUAGE plpgsql
AS $$
DECLARE
    avg_embedding_a vector(1536);
    avg_embedding_b vector(1536);
    similarity_score FLOAT;
BEGIN
    -- 파일 A의 평균 임베딩 계산
    SELECT AVG(embedding) INTO avg_embedding_a
    FROM document_chunks
    WHERE file_id = file_id_a AND embedding IS NOT NULL;

    -- 파일 B의 평균 임베딩 계산
    SELECT AVG(embedding) INTO avg_embedding_b
    FROM document_chunks
    WHERE file_id = file_id_b AND embedding IS NOT NULL;

    -- 둘 다 존재하면 유사도 계산
    IF avg_embedding_a IS NOT NULL AND avg_embedding_b IS NOT NULL THEN
        similarity_score := 1 - (avg_embedding_a <=> avg_embedding_b);
    ELSE
        similarity_score := 0;
    END IF;

    RETURN similarity_score;
END;
$$;

-- ============================================================================
-- 8. get_document_stats: 문서 통계 조회 함수
-- ============================================================================

CREATE OR REPLACE FUNCTION get_document_stats(target_file_id UUID)
RETURNS TABLE (
    file_id UUID,
    filename TEXT,
    file_type TEXT,
    chunk_count BIGINT,
    total_tokens BIGINT,
    embedding_status TEXT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.file_id,
        d.filename,
        d.file_type,
        COUNT(dc.id) AS chunk_count,
        COALESCE(SUM(dc.token_count), 0) AS total_tokens,
        d.embedding_status,
        d.created_at
    FROM documents d
    LEFT JOIN document_chunks dc ON d.id = dc.document_id
    WHERE d.file_id = target_file_id
    GROUP BY d.id, d.file_id, d.filename, d.file_type, d.embedding_status, d.created_at;
END;
$$;

-- ============================================================================
-- 9. 정리용 함수: 문서 및 관련 청크 삭제
-- ============================================================================

CREATE OR REPLACE FUNCTION delete_document_by_file_id(target_file_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INT;
BEGIN
    -- CASCADE로 인해 document_chunks도 자동 삭제됨
    DELETE FROM documents WHERE file_id = target_file_id;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count > 0;
END;
$$;

-- ============================================================================
-- 10. Row Level Security (RLS) 설정 - 선택사항
-- ============================================================================
-- 프로덕션에서는 RLS를 활성화하여 보안을 강화하세요.
-- 현재는 개발 편의를 위해 비활성화 상태입니다.

-- ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 설정 완료 확인 쿼리
-- ============================================================================
-- 아래 쿼리를 실행하여 설정이 올바르게 되었는지 확인하세요:

-- SELECT * FROM pg_extension WHERE extname = 'vector';
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
-- SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public';

-- ============================================================================
-- 끝
-- ============================================================================
