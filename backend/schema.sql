-- Create movies table
create table if not exists movies (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  description text,
  genre text,
  languages text[], -- Array for multiple languages (e.g., ['English', 'Hindi'])
  original_language text, -- Native/First release language
  mood_tags text[], -- Array of strings for vibes
  poster_url text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Turn on Row Level Security
alter table movies enable row level security;

-- Drop (if exists) and Recreate policies to avoid conflicts
drop policy if exists "Public movies are viewable by everyone" on movies;
create policy "Public movies are viewable by everyone"
  on movies for select
  using ( true );

drop policy if exists "Public movies are insertable" on movies;
create policy "Public movies are insertable"
  on movies for insert
  with check ( true );

-- Create profiles table
create table if not exists profiles (
  id uuid references auth.users on delete cascade primary key,
  email text,
  full_name text,
  avatar_url text,
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- RLS for profiles
alter table profiles enable row level security;

create policy "Users can view their own profile"
  on profiles for select
  using ( auth.uid() = id );

create policy "Users can update their own profile"
  on profiles for update
  using ( auth.uid() = id );

-- Optional: Trigger to create profile on signup
-- Note: This requires database permissions often restricted in some environments, 
-- but we can do it manually in the frontend code for this project.
