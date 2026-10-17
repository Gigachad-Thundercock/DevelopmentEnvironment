-- Authored wrapper; native pinned Initial Spawn remains the sole spawning owner.
-- The extracted dependency has only two callback guards in isUnitValid; all
-- position, resource, readiness, warp/paralyze and actual CreateUnit paths remain
-- original. Do not grant replacement units or create a second commander here.
local function allowNecronStartUnit(unitDefID)
 local named=UnitDefNames and UnitDefNames.nec_lord
 if not named or unitDefID~=named.id then return false end
 local def=UnitDefs and UnitDefs[unitDefID]
 local cp=def and def.customParams
 if not cp or tostring(cp.prototype40k)~='1' or cp.animsource~='nec_lord' then return false end
 for _,path in ipairs({'objects3d/nec_lord.glb','scripts/generated/nec_lord_anim.lua',
  'scripts/40k_roster.lua'}) do
  if not VFS.FileExists(path) then return false end
 end
 local mode=Spring and Spring.GetModOptions and Spring.GetModOptions().prototype_diagnostic
 local diagnostic=mode=='roster' or mode=='ui' or mode=='expandedproduction' or mode=='vital'
 if not diagnostic and not VFS.Include('40k_configs/development_playtest.lua').Allowed('nec_lord',Spring and Spring.GetModOptions and Spring.GetModOptions() or {}) and not VFS.FileExists('40k_configs/validated/nec_lord.lua') then return false end
 return true
end
local path='40k_reference/game_initial_spawn.lua'
assert(VFS.FileExists(path),'40K initial spawn: missing checked pinned dependency')
-- Isolated include environment avoids a global hook leaked to other gadgets.
local split=VFS.Include('40k_configs/four_faction_playtest.lua')
local opts=Spring and Spring.GetModOptions and Spring.GetModOptions()or{}
local starts
if split.Enabled(opts)then
 starts=function()
  local out={}
  for _,name in ipairs(VFS.Include('40k_configs/randomguy_startunits.lua').RuntimeStarts(UnitDefs,UnitDefNames,split.Starts))do
   local named=assert(UnitDefNames[name],'Four-faction starting commander missing: '..name)
   local d=assert(UnitDefs[named.id]);local cp=d.customParams or{}
   assert(tostring(cp.prototype40k)=='1'and tostring(cp.prototype40k_four_faction)=='1','Unmarked faction commander: '..name)
   out[#out+1]=named.id
  end
  return out
 end
 assert(VFS.LoadFile(path):find('Prototype40kStartUnits',1,true),'Four factions require checked stock spawn adapter')
end
local environment=setmetatable({Prototype40kIsNecronStartUnit=allowNecronStartUnit,Prototype40kStartUnits=starts},
 {__index=getfenv(1)})
return VFS.Include(path,environment)
