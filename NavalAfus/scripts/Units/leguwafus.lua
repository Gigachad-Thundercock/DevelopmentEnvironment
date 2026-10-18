-- Original Naval AFUS LEG Lua unit animation.
-- Uses exact names present in the generated S3O; no dependency on land AFUS COB pieces.
local base = piece("base")
local rotor = piece("rotor")
local core = piece("core")
local pulse = piece("pulse")
local emit = piece("emit")
local active = false
local productionThreadStarted = false
local function ProductionEffects()
    while true do
        if active then
            EmitSfx(emit, 1024)
        end
        Sleep(1050)
    end
end
function script.Create()
    active = true
    Spin(rotor, y_axis, 0.25, 0.12)
    if not productionThreadStarted then
        productionThreadStarted = true
        StartThread(ProductionEffects)
    end
end
function script.Activate()
    active = true
    Spin(rotor, y_axis, 0.25, 0.12)
    return 1
end
function script.Deactivate()
    active = false
    StopSpin(rotor, y_axis, 0.12)
    return 0
end
function script.Killed(recentDamage, maxHealth)
    active = false
    return 1
end
