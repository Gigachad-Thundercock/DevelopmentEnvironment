-- Naval Advanced Fusion II: LEG faction reactor assembly.
-- All pieces present in generated S3O. No changes to the finished unitdef.
local base = piece("base")
local rotor = piece("rotor")
local core = piece("core")
local pulse = piece("pulse")
local emit = piece("emit")

local SIG_REACTOR = 1
local active = true

local function ReactorCycle()
    Signal(SIG_REACTOR)
    SetSignalMask(SIG_REACTOR)
    while true do
        if active then
            EmitSfx(emit, 1024)
            -- Small reactor excitation movement, not the entire foundation.
            Move(pulse, y_axis, 0.7, 1.4)
            Sleep(360)
            Move(pulse, y_axis, 0, 1.4)
        end
        Sleep(1250)
    end
end

function script.Create()
    active = true
    Spin(rotor, y_axis, 0.31, 0.11)
    StartThread(ReactorCycle)
end

function script.Activate()
    active = true
    Spin(rotor, y_axis, 0.31, 0.11)
    return 1
end

function script.Deactivate()
    active = false
    StopSpin(rotor, y_axis, 0.11)
    Move(pulse, y_axis, 0, 2)
    return 0
end

function script.Killed(recentDamage, maxHealth)
    active = false
    Signal(SIG_REACTOR)
    StopSpin(rotor, y_axis, 0.11)
    return 1
end
