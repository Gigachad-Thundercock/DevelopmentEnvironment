function widget:GetInfo()
 return {name="40K accepted unit localization",desc="Conditional names through native BAR I18N",
  author="Local project",layer=-1000001,enabled=true}
end
-- Pinned Tweakdefs (-1000000) explicitly runs before Language (-999999).
-- Seed before both; native Language refreshes UnitDefs and each native panel then
-- refreshes its existing cache. Do not clone widgets or edit translated fields.
local function refresh()
 if not BAR or not BAR.I18N or type(BAR.I18N.set)~='function' then return end
 local language=Spring.GetConfigString('language','en')
 -- Four-faction labels for the native prefix-based picker.
 local factionStarts={
  arm={'armcom','Imperial Guard','Infantry supported by heavy weapons, tanks and artillery.'},
  cor={'corcom','Orks','Numerous infantry supported by walkers and heavy war machines.'},
  smc={'smcom','Space Marines','Elite infantry supported by Dreadnoughts and armoured vehicles.'},
  nec={'nec_lord','Necrons','Durable warriors supported by constructs and awakening technology.'},
 }
 for prefix,entry in pairs(factionStarts)do
  local d=UnitDefNames[entry[1]];local cp=d and d.customParams or{}
  if tostring(cp.prototype40k_four_faction)=='1'and cp.faction==entry[2]then
   BAR.I18N.set('en.units.factions.'..prefix,entry[2])
   BAR.I18N.set('en.ui.factionPicker.factions.'..prefix,entry[3])
   if language~='en'then
    BAR.I18N.set(language..'.units.factions.'..prefix,entry[2])
    BAR.I18N.set(language..'.ui.factionPicker.factions.'..prefix,entry[3])
   end
  end
 end
 local count=0
 for key,d in pairs(UnitDefNames) do
  local cp=d.customParams or {}
  if tostring(cp.prototype40k_ui_ready)=='1' and cp.prototype40k_ui_name then
   local englishName=cp.i18n_en_humanname or cp.prototype40k_ui_name
   local englishDescription=cp.i18n_en_tooltip or cp.prototype40k_ui_description
   BAR.I18N.set('en.units.names.'..key,englishName)
   if englishDescription then BAR.I18N.set('en.units.descriptions.'..key,englishDescription) end
   if language~='en' then
    -- Correct changed actors in the selected language, without fabricating a
    -- translation. Explicit localized CP overrides always win.
    BAR.I18N.set(language..'.units.names.'..key,cp['i18n_'..language..'_humanname'] or englishName)
    local description=cp['i18n_'..language..'_tooltip'] or englishDescription
    if description then BAR.I18N.set(language..'.units.descriptions.'..key,description) end
   end
   count=count+1
  end
 end
 Spring.Echo('40K UI LOCALIZATION',language,count,'accepted source actors; native fallback names retained')
end
function widget:Initialize() refresh() end
function widget:LanguageChanged() refresh() end
