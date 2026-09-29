local wezterm = require 'wezterm'

local config = wezterm.config_builder()

-- Machine-specific fonts, sizes, and executable paths.
local baseFont = { '움돋모노12' }
local fontSize = 12.0
local tabFontSize = 14.0
local powershell = wezterm.home_dir .. '/scoop/shims/pwsh.exe'
local sublimeEditor = '"C:\\Program Files\\Sublime Text\\subl.exe" --wait'

config.font = wezterm.font_with_fallback(baseFont)
config.font_rules = {
  {
    intensity = 'Bold',
    italic = false,
    font = wezterm.font_with_fallback(
      baseFont,
      { weight = 'Bold' }
    ),
  },
}
config.font_size = fontSize

config.color_scheme = 'zenbones'

config.window_background_opacity = 1

-- Start local PowerShell by default.
config.set_environment_variables = { EDITOR = sublimeEditor, VISUAL = sublimeEditor }
config.default_prog = { powershell, '-NoLogo' }
config.launch_menu = {
  {
    label = 'PS',
    domain = { DomainName = 'local' },
    args = { powershell, '-NoLogo' },
  },
}

config.use_fancy_tab_bar = true
config.tab_max_width = 48
config.tab_bar_at_bottom = true
config.window_frame = {
  font = wezterm.font_with_fallback(baseFont),
  font_size = tabFontSize,
}

config.window_padding = {
  left = 1,
  right = 1,
  top = 1,
  bottom = 1,
}

config.keys = {
  { key = 'RightArrow', mods = 'CTRL|ALT|SHIFT',
    action = wezterm.action.SplitHorizontal { domain = 'CurrentPaneDomain' } },
  { key = 'UpArrow', mods = 'CTRL|ALT|SHIFT',
    action = wezterm.action.SplitVertical { domain = 'CurrentPaneDomain' } },
  { key = 'LeftArrow', mods = 'CTRL|ALT',
    action = wezterm.action.AdjustPaneSize { 'Left', 1 } },
  { key = 'RightArrow', mods = 'CTRL|ALT',
    action = wezterm.action.AdjustPaneSize { 'Right', 1 } },
  { key = 'UpArrow', mods = 'CTRL|ALT',
    action = wezterm.action.AdjustPaneSize { 'Up', 1 } },
  { key = 'DownArrow', mods = 'CTRL|ALT',
    action = wezterm.action.AdjustPaneSize { 'Down', 1 } },
  { key = 'Tab', mods = 'CTRL',
    action = wezterm.action.SendString '\x1b[9;5u' },
  { key = 'Tab', mods = 'CTRL|SHIFT',
    action = wezterm.action.SendString '\x1b[9;6u' },
  { key = 'Enter', mods = 'CTRL',
    action = wezterm.action.SendString '\x1b[13;5u' },
}

return config
