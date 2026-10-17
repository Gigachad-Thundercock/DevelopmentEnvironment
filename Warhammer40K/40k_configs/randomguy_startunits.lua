-- Release compatibility only. No unit creation, orders or resource changes.
local M={}
local names={'armcom','smcom','corcom','nec_lord'}
local expected={armcom=true,smcom=true,corcom=true,nec_lord=true}
-- Exactly the forms accepted by pinned/current RandomGuy Initial Spawn.
local function marked(v)return v=='1'or v=='true'or v==true or v==1 end
function M.ApplyRaw(defs)
 for _,name in ipairs(names)do
  local d=assert(defs[name],'Missing release commander: '..name)
  local cp=assert(d.customparams,'Missing raw commander customparams: '..name)
  assert(tostring(cp.prototype40k)=='1'and tostring(cp.prototype40k_four_faction)=='1','Unmarked 40K commander: '..name)
  cp.startunit=true
 end
 for name,d in pairs(defs)do
  assert(not marked((d.customparams or{}).startunit)or expected[name],'Unexpected release startunit: '..name)
 end
end
function M.RuntimeStarts(defs,named,starts)
 local out,seen={},{}
 assert(#starts==4,'Exactly four release commander identities required')
 for _,name in ipairs(starts)do
  assert(expected[name]and not seen[name],'Unexpected or duplicate release commander: '..tostring(name))
  seen[name]=true
  local n=assert(named[name],'Missing native release commander: '..name)
  local d=assert(defs[n.id],'Missing native release commander definition: '..name)
  assert(marked((d.customParams or{}).startunit),'Missing native startunit customparam: '..name)
  out[#out+1]=name
 end
 for name,n in pairs(named)do
  local d=defs[n.id]
  assert(not(d and marked((d.customParams or{}).startunit))or expected[name],'Unexpected native release startunit: '..name)
 end
 return out
end
return M
