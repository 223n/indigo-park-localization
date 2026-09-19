-- Indigo Park 日本語化: エンディングの歌詞の訳を、画面の中央下（または中央上）に出す
--
-- エンディングの曲は動画（Content/Movies/CreditsSong.mp4）です。
-- レベル CreditsCutscene が、/Game/Movies/CreditsSongMediaPlayer で再生します。
-- このスクリプトは再生中の時刻を読み、同じMODのフォルダにある lyrics.srt から
-- その時刻の行を出します。
--
-- 出す位置や大きさは、同じフォルダの settings.ini で変えられます。
-- 行の頭に {\an8} と書いた行は中央上に、{\an2} と書いた行は中央下に出します。
--
-- lyrics.srt と settings.ini は、エンディングが始まるたびに読み直します。
-- ゲームを起動したまま書き換えても、エンディングを見直せば反映されます。
--
-- UE4SS（https://github.com/UE4SS-RE/RE-UE4SS）v3.0.1 の Lua MOD として動きます。

local MOD = "IndigoParkJP_Lyrics"

-- 動画を再生するメディアプレーヤー
local PLAYER_PATH = "/Game/Movies/CreditsSongMediaPlayer.CreditsSongMediaPlayer"

-- 動画を映すウィジェットのクラス。エンディングを飛ばすと、動画の再生は続いたまま
-- このウィジェットだけが画面から外れるため、字幕を出してよいかの判断に使う
local VIDEO_WIDGET = "W_CreditsCutscene_C"

-- ゲームの字幕と同じフォント。日本語化のMODが中身をM PLUS 1pに差し替えている
local FONT_PATH = "/Game/RefinedMainMenu/Menu/Fonts/Subtitle_Font_Quicksand.Subtitle_Font_Quicksand"

-- 見た目の既定。大きさは1920x1080のときの値で、画面の大きさに合わせてゲームが拡大縮小する。
-- position、margin、size、plate は settings.ini で変えられる
local STYLE = {
  position = "bottom", -- bottom（中央下）か top（中央上）
  margin = 72,         -- 画面の端（下か上）からの距離
  size = 30,           -- 文字の大きさ
  plate = 0.75,        -- 文字の後ろに敷く黒い帯の濃さ（0〜1。0で敷かない）
  typeface = "Bold",   -- Light、Regular、Medium、SemiBold、Bold のどれか
  outline = 2,         -- 文字の縁取りの太さ
  wrap = 1600,         -- これより長い行は折り返す
}

-- settings.ini で変えられる項目と、その値の種類
local SETTINGS = { position = "string", margin = "number", size = "number", plate = "number" }

-- 再生の時刻を確かめる間隔（ミリ秒）
local POLL_MS = 100

-- 再生の時刻を読むための名前。下の use_time_property を見る
local TICKS = "IndigoParkJP_TimeTicks"

-- UMG の列挙の値
local HIDDEN = 2              -- ESlateVisibility::Hidden
local HIT_TEST_INVISIBLE = 3  -- ESlateVisibility::HitTestInvisible
local JUSTIFY_CENTER = 1      -- ETextJustify::Center
local HALIGN_CENTER = 2       -- EHorizontalAlignment::HAlign_Center
local VALIGN_TOP = 1          -- EVerticalAlignment::VAlign_Top
local VALIGN_BOTTOM = 3       -- EVerticalAlignment::VAlign_Bottom

local function log(fmt, ...)
  print(string.format("[%s] " .. fmt .. "\n", MOD, ...))
end

local function valid(obj)
  return obj ~= nil and obj:IsValid()
end

-- このMODのフォルダ。lyrics.srt と settings.ini はここに置く
local function mod_dir()
  local info = debug.getinfo(1, "S")
  local dir = info and info.source:match("^@(.*)[\\/][Ss]cripts[\\/][^\\/]*$")
  if dir then return dir end
  for entry in package.path:gmatch("[^;]+") do
    dir = entry:match("^(.*[\\/]" .. MOD .. ")[\\/][Ss]cripts[\\/]%?%.lua$")
    if dir then return dir end
  end
  return nil
end

local function read_file(path)
  local f = io.open(path, "rb")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  text = text:gsub("^\239\187\191", "")  -- UTF-8 の BOM
  text = text:gsub("\r\n?", "\n")
  return text
end

-- SRT の時刻（時:分:秒,ミリ秒）を秒にする
local function seconds(h, m, s, frac)
  return tonumber(h) * 3600 + tonumber(m) * 60 + tonumber(s) + tonumber(frac) / 10 ^ #frac
end

-- 行の頭の {\an数字} を位置にする。テンキーの並びで、7〜9は上、1〜3は下
local function position_of(body)
  local an = tonumber(body:match("{\\an(%d)}"))
  if not an then return nil end
  if an >= 7 then return "top" end
  if an <= 3 then return "bottom" end
  return nil
end

-- SRT を読み、{ from, to, text, position } の一覧を開始の早い順に返す。読めなかった塊の数も返す。
-- tools/srt.py と同じ読み方にする
local function parse_srt(text)
  local cues, block, bad = {}, {}, 0

  local function flush()
    if #block == 0 then return end
    local i = 1
    if block[1]:match("^%s*%d+%s*$") and block[2] then i = 2 end
    local h1, m1, s1, f1, h2, m2, s2, f2 = block[i]:match(
      "^%s*(%d+):(%d%d):(%d%d)[,.](%d+)%s*%-%->%s*(%d+):(%d%d):(%d%d)[,.](%d+)")
    local body = table.concat(block, "\n", i + 1)
    local position = position_of(body)
    -- 字幕の編集ソフトが付ける書式（<i> や {\an8}）は画面にそのまま出てしまうため除く
    body = body:gsub("<[^>]*>", "")
    body = body:gsub("{\\[^}]*}", "")
    if h1 and body ~= "" and utf8.len(body) then
      cues[#cues + 1] = {
        from = seconds(h1, m1, s1, f1),
        to = seconds(h2, m2, s2, f2),
        text = body,
        position = position,
      }
    else
      bad = bad + 1
    end
    block = {}
  end

  for line in (text .. "\n"):gmatch("(.-)\n") do
    if line:match("^%s*$") then flush() else block[#block + 1] = line end
  end
  flush()
  table.sort(cues, function(a, b) return a.from < b.from end)
  return cues, bad
end

-- settings.ini を読み、STYLE に上書きした見た目を返す
local function parse_settings(text)
  local style = {}
  for k, v in pairs(STYLE) do style[k] = v end
  for line in (text .. "\n"):gmatch("(.-)\n") do
    local key, value = line:match("^%s*([%w_]+)%s*=%s*(.-)%s*$")
    local kind = key and SETTINGS[key]
    if kind == "number" and tonumber(value) then
      style[key] = tonumber(value)
    elseif kind == "string" then
      style[key] = value:lower()
    elseif key then
      log("settings.ini の %s は使えません: %s", key, value)
    end
  end
  if style.position ~= "top" and style.position ~= "bottom" then
    log("settings.ini の position は top か bottom にしてください: %s", style.position)
    style.position = STYLE.position
  end
  return style
end

-- lyrics.srt と settings.ini を読み、字幕の一覧と見た目を返す
local function load_files()
  local dir = mod_dir()
  if not dir then
    log("MODのフォルダが分かりません")
    return {}, STYLE
  end
  local text = read_file(dir .. "\\lyrics.srt")
  if not text then
    log("字幕のファイルがありません: %s\\lyrics.srt", dir)
    return {}, STYLE
  end
  local cues, bad = parse_srt(text)
  log("字幕を%d行読みました", #cues)
  if bad > 0 then
    log("読めなかった塊が%d個あります。時刻の書き方と、UTF-8で保存したかを確かめてください", bad)
  end
  local settings = read_file(dir .. "\\settings.ini")
  return cues, settings and parse_settings(settings) or STYLE
end

local function cue_at(cues, t)
  for _, c in ipairs(cues) do
    if t < c.from then return nil end
    if t < c.to then return c end
  end
  return nil
end

-- 再生の時刻は FTimespan で返るが、UE4SS 3.0.1 はこの型の中身を読めない（空の表になる）。
-- そこで GetTimeStamp() が返す MediaTimeStampInfo の Time を、
-- FTimespan の中身（100ナノ秒単位の int64）として読めるようにする
local time_property = false

local function use_time_property()
  if time_property then return end
  RegisterCustomProperty({
    ["Name"] = TICKS,
    ["Type"] = PropertyTypes.Int64Property,
    ["BelongsToClass"] = "/Script/MediaAssets.MediaTimeStampInfo",
    ["OffsetInternal"] = { ["Property"] = "Time", ["RelativeOffset"] = 0 },
  })
  time_property = true
end

local function media_seconds(player)
  use_time_property()
  return player:GetTimeStamp()[TICKS] / 10000000
end

-- 字幕を載せるウィジェットを作って画面に足す
local function create_ui(style)
  local outer = FindFirstOf("GameInstance")
  if not valid(outer) then return nil end

  local widget = StaticConstructObject(StaticFindObject("/Script/UMG.UserWidget"), outer)
  local tree = StaticConstructObject(StaticFindObject("/Script/UMG.WidgetTree"), widget)
  widget.WidgetTree = tree
  local root = StaticConstructObject(StaticFindObject("/Script/UMG.Overlay"), tree)
  tree.RootWidget = root
  local plate = StaticConstructObject(StaticFindObject("/Script/UMG.Border"), tree)
  local text = StaticConstructObject(StaticFindObject("/Script/UMG.TextBlock"), tree)

  local slot = root:AddChildToOverlay(plate)
  slot:SetHorizontalAlignment(HALIGN_CENTER)
  plate:SetBrushColor({ R = 0, G = 0, B = 0, A = style.plate })
  plate:SetPadding({ Left = 20, Top = 6, Right = 20, Bottom = 6 })
  plate:SetContent(text)

  local font = StaticFindObject(FONT_PATH)
  if valid(font) then
    text.Font.FontObject = font
    text.Font.TypefaceFontName = FName(style.typeface)
  else
    log("字幕のフォントが見つかりません。日本語が表示されないことがあります")
  end
  text.Font.Size = style.size
  text.Font.OutlineSettings.OutlineSize = style.outline
  text.WrapTextAt = style.wrap
  text:SetJustification(JUSTIFY_CENTER)
  plate:SetVisibility(HIDDEN)

  -- 操作を奪わないよう、当たり判定を持たせない
  widget:SetVisibility(HIT_TEST_INVISIBLE)
  widget:AddToViewport(1000)
  return { widget = widget, slot = slot, plate = plate, text = text, style = style }
end

-- 字幕を中央上か中央下に寄せる
local function place(ui, position)
  if ui.position == position then return end
  local m = ui.style.margin
  if position == "top" then
    ui.slot:SetVerticalAlignment(VALIGN_TOP)
    ui.slot:SetPadding({ Left = 0, Top = m, Right = 0, Bottom = 0 })
  else
    ui.slot:SetVerticalAlignment(VALIGN_BOTTOM)
    ui.slot:SetPadding({ Left = 0, Top = 0, Right = 0, Bottom = m })
  end
  ui.position = position
end

local function show(ui, cue)
  if ui.shown == cue then return end
  place(ui, cue.position or ui.style.position)
  ui.text:SetText(FText(cue.text))
  ui.plate:SetVisibility(HIT_TEST_INVISIBLE)
  ui.shown = cue
end

local function hide(ui)
  if ui.shown == nil then return end
  ui.plate:SetVisibility(HIDDEN)
  ui.shown = nil
end

local player = nil
local session = nil -- エンディングの再生中だけ持つ { cues, style, enabled, ui, video }

local function remove_ui()
  local ui = session.ui
  session.ui = nil
  if ui and valid(ui.widget) then
    ui.widget:RemoveFromParent()
  end
end

local function end_session()
  remove_ui()
  session = nil
end

-- 動画のウィジェットが画面に出ているか。
-- ウィジェットが見つからないとき（ゲームの更新で名前が変わったときなど）は確かめない
local function video_on_screen()
  if valid(session.video) and session.video:IsInViewport() then return true end
  local all = FindAllOf(VIDEO_WIDGET)
  if not all then return session.video == nil end
  for _, w in ipairs(all) do
    if w:IsValid() and w:IsInViewport() then
      session.video = w
      return true
    end
  end
  return false
end

local function tick()
  if not valid(player) then
    player = StaticFindObject(PLAYER_PATH)
  end
  local active = valid(player) and (player:IsPlaying() or player:IsPaused())
  if not active then
    if session then end_session() end
    return
  end

  if not session then
    local cues, style = load_files()
    session = { cues = cues, style = style, enabled = #cues > 0, ui = nil, video = nil }
    log("エンディングが始まりました")
  end
  if not session.enabled then return end

  if not video_on_screen() then
    -- 飛ばされた。動画の再生が止まるまで、このエンディングでは出さない
    session.enabled = false
    remove_ui()
    log("エンディングの動画が閉じられたため、字幕を止めました")
    return
  end

  if not (session.ui and valid(session.ui.widget)) then
    session.ui = create_ui(session.style)
    if not session.ui then return end
  end

  local cue = cue_at(session.cues, media_seconds(player))
  if cue then show(session.ui, cue) else hide(session.ui) end
end

local errors = 0

LoopAsync(POLL_MS, function()
  ExecuteInGameThread(function()
    local ok, err = pcall(tick)
    if not ok then
      errors = errors + 1
      if errors <= 3 then log("字幕を出せませんでした: %s", tostring(err)) end
      -- 同じ失敗を繰り返さないよう、このエンディングの間は止め、出ている行も消す
      if session then
        session.enabled = false
        if session.ui then pcall(hide, session.ui) end
      end
    end
  end)
  return false
end)

log("読み込みました")
