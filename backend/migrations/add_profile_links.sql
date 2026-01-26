-- Add profile_links table for social profile analysis
CREATE TABLE IF NOT EXISTS profile_links (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Profile URLs/Usernames
    github_username VARCHAR(100),
    leetcode_username VARCHAR(100),
    linkedin_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    
    -- Cached profile data (JSON)
    github_data JSONB,
    leetcode_data JSONB,
    
    -- Analysis scores
    github_score INTEGER DEFAULT 0,
    leetcode_score INTEGER DEFAULT 0,
    overall_score INTEGER DEFAULT 0,
    
    -- AI-generated recommendations (JSON array)
    recommendations JSONB,
    
    -- Timestamps
    last_analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_profile_links_user_id ON profile_links(user_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_profile_links_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_profile_links_updated_at
    BEFORE UPDATE ON profile_links
    FOR EACH ROW
    EXECUTE FUNCTION update_profile_links_updated_at();
