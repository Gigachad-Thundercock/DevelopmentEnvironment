local split=VFS.Include('40k_configs/four_faction_playtest.lua')
-- Native SideParser runs before BAR's Spring option normalization. Its raw
-- startscript table omits defaults; unitsync has no Spring.GetModOptions at all.
-- Resolve only these gates from this archive (frozen defaults may differ).
-- Do not mutate the engine table or override any explicit choice, including false.
local raw=Spring and Spring.GetModOptions and Spring.GetModOptions()or{}
local opts={prototype_development_playtest=raw.prototype_development_playtest,
 prototype_source_progression=raw.prototype_source_progression,
 prototype_diagnostic=raw.prototype_diagnostic}
if opts.prototype_development_playtest==nil or opts.prototype_source_progression==nil then
 for _,option in ipairs(VFS.Include('40k_configs/randomguy_options_schema.lua'))do
  if (option.key=='prototype_development_playtest' or option.key=='prototype_source_progression')
   and opts[option.key]==nil then opts[option.key]=option.def end
 end
end
if split.Enabled(opts)then
 -- Existing Modded Chobby sends these fixed lobby names. Native four-faction
 -- names remain first; aliases affect starting selection only, not UnitDefs.
 local sides={};for i,side in ipairs(split.Sides)do sides[i]=side end
 sides[#sides+1]={name='Armada',startunit='armcom'}
 sides[#sides+1]={name='Cortex',startunit='corcom'}
 sides[#sides+1]={name='Legion',startunit='smcom'}
 return sides
end
-- Authored adapter; the unchanged pinned side table is an ignored dependency.
local sides=VFS.Include('40k_reference/sidedata.lua')
assert(type(sides)=='table','40K starting sides: missing pinned BAR side table')
local required={'objects3d/nec_lord.glb','scripts/generated/nec_lord_anim.lua',
 'scripts/40k_roster.lua'}
for _,path in ipairs(required) do if not VFS.FileExists(path) then return sides end end
local mode=Spring and Spring.GetModOptions and Spring.GetModOptions().prototype_diagnostic
local diagnostic=mode=='roster' or mode=='ui' or mode=='expandedproduction' or mode=='vital'
if not diagnostic and not VFS.Include('40k_configs/development_playtest.lua').Allowed('nec_lord',Spring and Spring.GetModOptions and Spring.GetModOptions() or {}) and not VFS.FileExists('40k_configs/validated/nec_lord.lua') then return sides end
-- Engine side parsing may precede UnitDefs. Native spawn validation below always
-- checks the loaded definition; this early gate checks the real validated assets.
if UnitDefNames and not UnitDefNames.nec_lord then return sides end
for _,side in ipairs(sides) do if side.name=='Necrons' then return sides end end
sides[#sides+1]={name='Necrons',startunit='nec_lord'}
return sides
