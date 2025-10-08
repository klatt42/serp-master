-- ================================================
-- Week 6: Keyword Clustering & Niche Analysis Tables
-- ================================================
-- Supabase PostgreSQL Migration
-- Run this SQL in your Supabase SQL Editor
-- ================================================

-- Keyword Clusters Table
CREATE TABLE IF NOT EXISTS keyword_clusters (
    id SERIAL PRIMARY KEY,
    cluster_name VARCHAR(255) NOT NULL,
    parent_seed_keyword TEXT NOT NULL,
    keyword_ids INTEGER[] NOT NULL,  -- Array of keyword IDs in this cluster
    keywords TEXT[] NOT NULL,        -- Array of keyword strings for quick access
    avg_search_volume INTEGER,
    avg_difficulty DECIMAL(5, 2),
    avg_cpc DECIMAL(10, 2),
    total_keywords INTEGER NOT NULL,
    total_search_volume INTEGER,
    cluster_theme TEXT,              -- AI-generated theme description
    theme_type VARCHAR(100),         -- Type of content theme
    key_terms TEXT[],                -- Most important terms in cluster
    primary_intent VARCHAR(50),      -- Dominant search intent
    common_serp_features TEXT[],     -- Common SERP features
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clusters_seed ON keyword_clusters(parent_seed_keyword);
CREATE INDEX IF NOT EXISTS idx_clusters_theme ON keyword_clusters(cluster_theme);
CREATE INDEX IF NOT EXISTS idx_clusters_intent ON keyword_clusters(primary_intent);

-- Niche Analysis Table
CREATE TABLE IF NOT EXISTS niche_analyses (
    id SERIAL PRIMARY KEY,
    seed_keyword TEXT NOT NULL,
    cluster_ids INTEGER[],           -- References keyword_clusters(id)
    total_keywords INTEGER,
    total_search_volume INTEGER,
    market_size VARCHAR(50),         -- small, medium, large, huge
    competition_level VARCHAR(50),   -- low, medium, high, very_high
    avg_keyword_difficulty DECIMAL(5, 2),
    monetization_potential DECIMAL(10, 2),
    top_serp_features TEXT[],        -- Common SERP features
    content_gaps JSONB,              -- Identified gaps
    recommended_strategy TEXT,       -- AI-generated strategy
    confidence_score DECIMAL(3, 2),  -- 0-1 confidence in analysis
    opportunities JSONB,             -- Market opportunities
    cluster_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(seed_keyword)
);

CREATE INDEX IF NOT EXISTS idx_niche_seed ON niche_analyses(seed_keyword);
CREATE INDEX IF NOT EXISTS idx_niche_market_size ON niche_analyses(market_size);
CREATE INDEX IF NOT EXISTS idx_niche_competition ON niche_analyses(competition_level);

-- Content Strategy Table
CREATE TABLE IF NOT EXISTS content_strategies (
    id SERIAL PRIMARY KEY,
    niche_analysis_id INTEGER REFERENCES niche_analyses(id),
    cluster_id INTEGER REFERENCES keyword_clusters(id),
    content_type VARCHAR(100),       -- blog, video, landing page, etc.
    target_keywords TEXT[],          -- Keywords to target
    recommended_title TEXT,
    content_outline JSONB,           -- Structured content plan
    priority_score INTEGER,          -- 1-100 priority
    estimated_effort VARCHAR(50),    -- low, medium, high
    estimated_traffic INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_strategy_niche ON content_strategies(niche_analysis_id);
CREATE INDEX IF NOT EXISTS idx_strategy_priority ON content_strategies(priority_score DESC);

-- Discovery Cache Table (for Redis fallback)
CREATE TABLE IF NOT EXISTS discovery_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cache_key ON discovery_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON discovery_cache(expires_at);

-- Enable Row Level Security
ALTER TABLE keyword_clusters ENABLE ROW LEVEL SECURITY;
ALTER TABLE niche_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovery_cache ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Allow public access for MVP (can be restricted later)
CREATE POLICY "Anyone can view clusters" ON keyword_clusters
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert clusters" ON keyword_clusters
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update clusters" ON keyword_clusters
  FOR UPDATE USING (true);

CREATE POLICY "Anyone can view niche analyses" ON niche_analyses
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert niche analyses" ON niche_analyses
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update niche analyses" ON niche_analyses
  FOR UPDATE USING (true);

CREATE POLICY "Anyone can view strategies" ON content_strategies
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert strategies" ON content_strategies
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can view cache" ON discovery_cache
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert cache" ON discovery_cache
  FOR INSERT WITH CHECK (true);

-- Helper function: Clean up old cached data
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM discovery_cache
  WHERE expires_at < NOW();

  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Helper view: Recent cluster analyses
CREATE OR REPLACE VIEW recent_cluster_analyses AS
SELECT
  nc.id,
  nc.seed_keyword,
  nc.market_size,
  nc.competition_level,
  nc.cluster_count,
  nc.total_search_volume,
  nc.confidence_score,
  nc.created_at
FROM niche_analyses nc
WHERE nc.created_at > NOW() - INTERVAL '30 days'
ORDER BY nc.created_at DESC
LIMIT 100;

-- Verify tables were created
SELECT
  table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name IN ('keyword_clusters', 'niche_analyses', 'content_strategies', 'discovery_cache')
ORDER BY table_name, ordinal_position;

-- Success! Clustering and niche analysis tables ready 🚀
