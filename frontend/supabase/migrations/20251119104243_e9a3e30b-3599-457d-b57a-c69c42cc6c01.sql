-- Add address column to branches table
ALTER TABLE public.branches ADD COLUMN IF NOT EXISTS address TEXT;

-- Add branch_id column to employees table
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS branch_id UUID REFERENCES public.branches(id) ON DELETE SET NULL;