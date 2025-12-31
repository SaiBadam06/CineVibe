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

-- Ensure original_language column exists if table was already created
alter table movies add column if not exists original_language text;

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

drop policy if exists "Users can view their own profile" on profiles;
create policy "Users can view their own profile"
  on profiles for select
  using ( auth.uid() = id );

drop policy if exists "Users can update their own profile" on profiles;
create policy "Users can update their own profile"
  on profiles for update
  using ( auth.uid() = id );

drop policy if exists "Users can insert their own profile" on profiles;
create policy "Users can insert their own profile"
  on profiles for insert
  with check ( auth.uid() = id );

-- Function to handle new user profiles with robustness
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name, updated_at)
  values (
    new.id, 
    new.email, 
    coalesce(new.raw_user_meta_data->>'full_name', ''),
    now()
  )
  on conflict (id) do update set
    email = excluded.email,
    full_name = coalesce(excluded.full_name, profiles.full_name),
    updated_at = now();
  return new;
end;
$$ language plpgsql security definer;

-- Trigger to create profile on signup
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Note: This trigger handles profile creation automatically at the database level.
