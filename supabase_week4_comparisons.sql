-- ================================================
-- Week 4: Competitor Comparison Tables
-- ================================================
-- Add to existing SERP Master Supabase schema
-- Run this SQL in your Supabase SQL Editor
-- ================================================

-- Competitor comparisons table - stores comparison analysis results
CREATE TABLE IF NOT EXISTS competitor_comparisons (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  comparison_id TEXT UNIQUE NOT NULL,
  user_url TEXT NOT NULL,
  competitor_urls TEXT[] NOT NULL,
  max_pages INTEGER DEFAULT 50,

  -- Results (stored as JSONB)
  user_site JSONB,
  competitors JSONB,
  comparison_data JSONB,
  gaps JSONB,
  competitive_strategy JSONB,
  quick_wins JSONB,

  -- Metadata
  status TEXT NOT NULL DEFAULT 'crawling', -- crawling, analyzing, complete, failed
  progress INTEGER DEFAULT 0,
  sites_completed INTEGER DEFAULT 0,
  sites_total INTEGER NOT NULL,
  error_message TEXT,

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,

  -- Optional: User association (for logged-in users)
  user_id TEXT,

  -- Indexes
  CONSTRAINT status_check CHECK (status IN ('crawling', 'analyzing', 'complete', 'failed'))
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_comparisons_comparison_id ON competitor_comparisons(comparison_id);
CREATE INDEX IF NOT EXISTS idx_comparisons_user_url ON competitor_comparisons(user_url);
CREATE INDEX IF NOT EXISTS idx_comparisons_user_id ON competitor_comparisons(user_id);
CREATE INDEX IF NOT EXISTS idx_comparisons_created_at ON competitor_comparisons(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comparisons_status ON competitor_comparisons(status);

-- Enable Row Level Security
ALTER TABLE competitor_comparisons ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Allow public access for MVP (can be restricted later)
CREATE POLICY "Anyone can view comparisons" ON competitor_comparisons
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert comparisons" ON competitor_comparisons
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update comparisons" ON competitor_comparisons
  FOR UPDATE USING (true);

-- Optional: Restrict to authenticated users only (uncomment to use)
/*
CREATE POLICY "Users can view their own comparisons" ON competitor_comparisons
  FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert comparisons" ON competitor_comparisons
  FOR INSERT WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can update their own comparisons" ON competitor_comparisons
  FOR UPDATE USING (auth.uid()::text = user_id OR user_id IS NULL);
*/

-- ================================================
-- Helper function: Clean up old comparisons
-- ================================================

CREATE OR REPLACE FUNCTION cleanup_old_comparisons(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM competitor_comparisons
  WHERE created_at < NOW() - (days_old || ' days')::INTERVAL
  AND (status = 'complete' OR status = 'failed');

  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- Helper view: Recent comparisons summary
-- ================================================

CREATE OR REPLACE VIEW recent_comparisons AS
SELECT
  id,
  comparison_id,
  user_url,
  array_length(competitor_urls, 1) as competitor_count,
  status,
  progress,
  created_at,
  completed_at,
  EXTRACT(EPOCH FROM (completed_at - created_at)) as duration_seconds
FROM competitor_comparisons
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;

-- ================================================
-- Verify table was created
-- ================================================

SELECT
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'competitor_comparisons'
ORDER BY ordinal_position;

-- Success! Competitor comparison tracking is ready 🚀
