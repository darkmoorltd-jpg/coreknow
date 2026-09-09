-- CoreKnow Document Components Table
CREATE TABLE IF NOT EXISTS public.coreknow_document_components (
    id BIGSERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES public.coreknow_documents(id),
    component_type TEXT,  -- 'text', 'table', 'image', 'formulas', 'graph_data'
    content JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
