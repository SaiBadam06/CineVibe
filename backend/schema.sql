-- Create movies table
create table if not exists movies (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  description text,
  genre text,
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
