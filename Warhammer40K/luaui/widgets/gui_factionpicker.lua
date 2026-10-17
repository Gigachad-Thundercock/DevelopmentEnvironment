-- Release labels around the unchanged stock BAR faction picker.
-- It consumes native validStartUnits and sends the original changeStartUnit message.
local labels={
 ['units.factions.arm']='Imperial Guard', ['units.factions.cor']='Orks',
 ['units.factions.smc']='Space Marines', ['units.factions.nec']='Necrons',
 ['units.factions.random']='Random',
 ['ui.factionPicker.factions.arm']='Imperial Guard: Field Commander',
 ['ui.factionPicker.factions.cor']='Orks: Big Mek Commander',
 ['ui.factionPicker.factions.smc']='Space Marines: Force Commander',
 ['ui.factionPicker.factions.nec']='Necrons: Lord',
 ['ui.factionPicker.factions.random']='Random choice among the four 40K factions',
}
local originalBAR=BAR
local labelledBAR=setmetatable({I18N=function(key,...)
 if labels[key]then return labels[key]end
 return originalBAR.I18N(key,...)
end},{__index=originalBAR})
VFS.Include('40k_reference/randomguy_gui_factionpicker.lua',
 setmetatable({BAR=labelledBAR},{__index=getfenv(1)}))
