-- Add user_id column to tracked_items to associate items with authenticated users
ALTER TABLE tracked_items ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Create index for efficient user-specific queries
CREATE INDEX IF NOT EXISTS idx_tracked_items_user_id ON tracked_items(user_id);
