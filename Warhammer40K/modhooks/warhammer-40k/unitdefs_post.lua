-- Optional-mod integration hook. The stack executes RandomGuy Hosting first.
-- Only export Warhammer additions here; never rerun Hosting's post-processing.
VFS.Include('40k_configs/randomguy_additive_units.lua').Apply(UnitDefs, VFS, getfenv(1))
