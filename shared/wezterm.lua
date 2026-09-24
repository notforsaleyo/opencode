local wezterm = require 'wezterm'

local config = wezterm.config_builder()

config.font = wezterm.font_with_fallback { 'CodexMono EA' }
config.font_size = 13.0

config.color_scheme = 'Github Light (Gogh)'
config.colors = {
  tab_bar = {
    background = '#d8dee8',
    active_tab = {
      bg_color = '#c5ddf5',
      fg_color = '#163b61',
      intensity = 'Bold',
    },
    inactive_tab = {
      bg_color = '#e7ebf1',
      fg_color = '#465365',
    },
    inactive_tab_hover = {
      bg_color = '#d5e3f2',
      fg_color = '#243f5c',
      italic = false,
    },
    new_tab = {
      bg_color = '#d8dee8',
      fg_color = '#465365',
    },
    new_tab_hover = {
      bg_color = '#c5ddf5',
      fg_color = '#163b61',
      italic = false,
    },
  },
}

config.window_background_opacity = 1

-- Windows launches use PowerShell; WSL remains available from the launcher.
local powershell = wezterm.home_dir .. '/scoop/shims/pwsh.exe'
config.default_prog = { powershell, '-NoLogo' }
config.launch_menu = {
  {
    label = 'PS',
    domain = { DomainName = 'local' },
    args = { powershell, '-NoLogo' },
  },
  {
    label = 'WSL',
    domain = { DomainName = 'WSL:Ubuntu-26.04' },
    args = { '/bin/bash', '-lc', 'cd ~ && exec /bin/bash -l' },
  },
}

config.use_fancy_tab_bar = true
config.tab_max_width = 48
config.tab_bar_at_bottom = true
config.window_frame = {
  font = wezterm.font_with_fallback { 'CodexMono EA' },
  font_size = 13.0,
  active_titlebar_bg = '#d8dee8',
  inactive_titlebar_bg = '#d8dee8',
}

wezterm.on('format-tab-title', function(tab)
  local pane = tab.active_pane
  local title = tab.tab_title
  if not title or title == '' then
    if (pane.title or ''):match('^OC |') then
      title = 'OC'
    else
      local process = (pane.foreground_process_name or ''):match('([^/\\]+)$') or ''
      local names = { ['pwsh.exe'] = 'PowerShell', ['powershell.exe'] = 'PowerShell' }
      title = names[process] or process:gsub('%.exe$', '')
      if title == '' or title == 'wsl' or title == 'wslhost' then
        title = (pane.domain_name or ''):match('^WSL:(.+)$') or pane.title or 'Terminal'
      end
    end
    local cwd = pane.current_working_dir
    local folder = cwd and cwd.file_path:gsub('[/\\]+$', ''):match('([^/\\]+)$')
    if folder then
      title = title .. '/' .. folder
    end
  end
  return ' ' .. (tab.tab_index + 1) .. ' ' .. wezterm.truncate_right(title, 48) .. ' '
end)

config.window_padding = {
  left = 0,
  right = 0,
  top = 0,
  bottom = 0,
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
