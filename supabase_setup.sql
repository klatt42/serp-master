-- ================================================
-- SERP Master Database Schema for Supabase
-- ================================================
-- Run this SQL in your Supabase SQL Editor
-- Project: https://fodcbmzxnxtuazmhklrf.supabase.co
-- ================================================

-- Projects table - stores user SEO projects
CREATE TABLE IF NOT EXISTS projects (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  domain TEXT,
  target_keywords TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Keywords table - stores keyword research data
CREATE TABLE IF NOT EXISTS keywords (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,
  search_volume INTEGER DEFAULT 0,
  competition INTEGER DEFAULT 0,
  cpc DECIMAL(10,2) DEFAULT 0,
  difficulty INTEGER DEFAULT 0,
  related_keywords TEXT[],
  researched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rankings table - stores keyword ranking history
CREATE TABLE IF NOT EXISTS rankings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,
  position INTEGER NOT NULL,
  url TEXT,
  previous_position INTEGER,
  change INTEGER,
  checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audits table - stores technical SEO audit results
CREATE TABLE IF NOT EXISTS audits (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  page_speed_score INTEGER,
  mobile_friendly BOOLEAN,
  core_web_vitals JSONB,
  issues_found JSONB,
  overall_score INTEGER,
  audited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content optimization table - stores content analysis results
CREATE TABLE IF NOT EXISTS content_optimizations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  title_score INTEGER,
  meta_description_score INTEGER,
  header_structure_score INTEGER,
  keyword_density_score INTEGER,
  internal_links_score INTEGER,
  content_length_score INTEGER,
  overall_score INTEGER,
  suggestions JSONB,
  analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SERP data table - stores search engine results page data
CREATE TABLE IF NOT EXISTS serp_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,
  results JSONB,
  serp_features TEXT[],
  fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================================
-- Create indexes for better query performance
-- ================================================

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_keywords_project_id ON keywords(project_id);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_rankings_project_id ON rankings(project_id);
CREATE INDEX IF NOT EXISTS idx_rankings_keyword ON rankings(keyword);
CREATE INDEX IF NOT EXISTS idx_rankings_checked_at ON rankings(checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_audits_project_id ON audits(project_id);
CREATE INDEX IF NOT EXISTS idx_content_project_id ON content_optimizations(project_id);
CREATE INDEX IF NOT EXISTS idx_serp_project_id ON serp_data(project_id);

-- ================================================
-- Enable Row Level Security (RLS)
-- ================================================

ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_optimizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE serp_data ENABLE ROW LEVEL SECURITY;

-- ================================================
-- RLS Policies (Simple - allow authenticated users)
-- ================================================

-- Projects policies
CREATE POLICY "Users can view their own projects" ON projects
  FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert their own projects" ON projects
  FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own projects" ON projects
  FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete their own projects" ON projects
  FOR DELETE USING (auth.uid()::text = user_id);

-- Keywords policies
CREATE POLICY "Users can view keywords for their projects" ON keywords
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = keywords.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can insert keywords for their projects" ON keywords
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = keywords.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

-- Rankings policies
CREATE POLICY "Users can view rankings for their projects" ON rankings
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = rankings.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can insert rankings for their projects" ON rankings
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = rankings.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

-- Audits policies
CREATE POLICY "Users can view audits for their projects" ON audits
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = audits.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can insert audits for their projects" ON audits
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = audits.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

-- Content optimizations policies
CREATE POLICY "Users can view content optimizations for their projects" ON content_optimizations
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = content_optimizations.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can insert content optimizations for their projects" ON content_optimizations
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = content_optimizations.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

-- SERP data policies
CREATE POLICY "Users can view SERP data for their projects" ON serp_data
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = serp_data.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can insert SERP data for their projects" ON serp_data
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = serp_data.project_id
      AND projects.user_id = auth.uid()::text
    )
  );

-- ================================================
-- Create function to update updated_at timestamp
-- ================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to projects table
CREATE TRIGGER update_projects_updated_at
  BEFORE UPDATE ON projects
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- Insert sample data for testing (optional)
-- ================================================

-- Uncomment to insert sample project
/*
INSERT INTO projects (user_id, name, domain, target_keywords)
VALUES (
  'test-user-123',
  'My SEO Project',
  'example.com',
  ARRAY['seo tools', 'keyword research', 'content optimization']
);
*/

-- ================================================
-- Verify tables were created
-- ================================================

SELECT
  table_name,
  (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
  AND table_name IN ('projects', 'keywords', 'rankings', 'audits', 'content_optimizations', 'serp_data')
ORDER BY table_name;

-- Success! Your SERP Master database is ready 🚀
