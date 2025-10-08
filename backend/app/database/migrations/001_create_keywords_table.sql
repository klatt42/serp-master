-- ================================================
-- Week 5: Niche Discovery - Keywords Tables
-- ================================================
-- Supabase PostgreSQL Migration
-- Run this SQL in your Supabase SQL Editor
-- ================================================

-- Keywords table - stores discovered keyword data
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    search_volume INTEGER NOT NULL DEFAULT 0,
    keyword_difficulty INTEGER,  -- 0-100 scale
    cpc DECIMAL(10, 2),          -- Cost per click in USD
    competition DECIMAL(3, 2),   -- 0-1 scale
    trend JSONB,                 -- Monthly volume trend data
    intent VARCHAR(50),          -- informational, commercial, transactional, navigational
    serp_features JSONB,         -- Array of SERP features
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(keyword)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_keywords_volume ON keywords(search_volume DESC);
CREATE INDEX IF NOT EXISTS idx_keywords_difficulty ON keywords(keyword_difficulty);
CREATE INDEX IF NOT EXISTS idx_keywords_cpc ON keywords(cpc);
CREATE INDEX IF NOT EXISTS idx_keywords_intent ON keywords(intent);

-- Keyword discoveries table - stores discovery sessions
CREATE TABLE IF NOT EXISTS keyword_discoveries (
    id SERIAL PRIMARY KEY,
    seed_keyword TEXT NOT NULL,
    discovered_keyword_ids INTEGER[],  -- Array of keyword IDs
    total_opportunities INTEGER,
    avg_volume INTEGER,
    avg_difficulty DECIMAL(5, 2),
    filters_applied JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_discoveries_seed ON keyword_discoveries(seed_keyword);
CREATE INDEX IF NOT EXISTS idx_discoveries_created ON keyword_discoveries(created_at DESC);

-- Enable Row Level Security
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE keyword_discoveries ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Allow public access for MVP (can be restricted later)
CREATE POLICY "Anyone can view keywords" ON keywords
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert keywords" ON keywords
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update keywords" ON keywords
  FOR UPDATE USING (true);

CREATE POLICY "Anyone can view discoveries" ON keyword_discoveries
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert discoveries" ON keyword_discoveries
  FOR INSERT WITH CHECK (true);

-- Helper function: Clean up old keyword data
CREATE OR REPLACE FUNCTION cleanup_old_keywords(days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM keywords
  WHERE last_updated < NOW() - (days_old || ' days')::INTERVAL;

  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Helper view: Recent keyword discoveries
CREATE OR REPLACE VIEW recent_keyword_discoveries AS
SELECT
  id,
  seed_keyword,
  total_opportunities,
  avg_volume,
  avg_difficulty,
  created_at
FROM keyword_discoveries
WHERE created_at > NOW() - INTERVAL '30 days'
ORDER BY created_at DESC
LIMIT 100;

-- Verify tables were created
SELECT
  table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name IN ('keywords', 'keyword_discoveries')
ORDER BY table_name, ordinal_position;

-- Success! Keyword discovery tables ready 🚀
