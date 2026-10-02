-- Course calendar shortcode
--
-- Builds the course calendar table from _variables.yml, so dates only live in one place.
--   {{< course-calendar >}}               full term (weeks 0-10 and finals)
--   {{< course-calendar weeks="9-11" >}}  only some weeks (finals week is week 11)
--
-- What goes in the calendar is listed under `calendar-events` in _variables.yml.
-- Each event points to a date variable (e.g. hwk1-due), and is placed in the right
-- week and weekday column from that date.
--
-- Every date variable written as 'Weekday, Month D' is checked against the real calendar:
-- a weekday that does not match the date prints a render warning and shows ⚠ in the table.

local MONTHS = { January = 1, February = 2, March = 3, April = 4, May = 5, June = 6, July = 7,
  August = 8, September = 9, October = 10, November = 11, December = 12 }
local SHORT_MONTHS = { "Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec" }
local WEEKDAYS = { "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" }
-- Calendar columns, Monday (wday 2) to Saturday (wday 7)
local COLUMNS = { "Monday", "Tuesday - Lecture", "Wednesday", "Thursday - Lecture",
  "Friday - Discussion section", "Saturday" }
local FINALS = 11
local DAY = 86400

local CSS = [[
<style>
.course-calendar-wrap { overflow-x: auto; margin: 1rem 0; }
.course-calendar { border-collapse: collapse; width: 100%; font-size: 0.85rem; text-align: center; }
.course-calendar th, .course-calendar td { border: 1px solid #555; padding: 0.3rem 0.45rem; vertical-align: bottom; }
.course-calendar th { font-weight: 600; vertical-align: middle; }
.course-calendar .cal-week { white-space: nowrap; }
.course-calendar .cal-date { font-weight: 700; white-space: nowrap; }
.course-calendar .cal-topic { color: #1f4e9c; }
.course-calendar .cal-due { color: #c8102e; }
.course-calendar .cal-available { color: #3b7d23; }
.course-calendar .cal-resubmission { color: #d98200; }
.course-calendar .cal-info, .course-calendar .cal-noclass { color: #b0648f; }
.course-calendar .cal-warning { color: #c8102e; font-weight: 700; cursor: help; }
.reveal .course-calendar { font-size: 0.45em; }
</style>
]]

local function stringify(v)
  if v == nil then return nil end
  return pandoc.utils.stringify(v)
end

local function escape(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local vars
local function load_vars()
  if vars then return vars end
  local path = pandoc.path.join({ quarto.project.directory, "_variables.yml" })
  local f = io.open(path, "r")
  if not f then error("course-calendar: cannot open " .. path) end
  local txt = f:read("a")
  f:close()
  vars = pandoc.read("---\n" .. txt .. "\n---\n", "markdown").meta
  return vars
end

-- 'Friday, October 2' -> date table, with a check that the weekday matches the date
local function parse_date(value, year)
  local wd, month_name, day = value:match("^(%a+),%s+(%a+)%s+(%d+)$")
  local month = month_name and MONTHS[month_name]
  if not month then return nil end
  local t = os.time({ year = year, month = month, day = tonumber(day), hour = 12 })
  local wday = os.date("*t", t).wday
  return { time = t, month = month, day = tonumber(day), wday = wday,
    written = wd, actual = WEEKDAYS[wday], ok = (WEEKDAYS[wday] == wd) }
end

local function short_date(t)
  local d = os.date("*t", t)
  return SHORT_MONTHS[d.month] .. " " .. d.day
end

local warned = {}
local function warn(msg)
  if not warned[msg] then
    io.stderr:write("WARNING (course-calendar): " .. msg .. "\n")
    warned[msg] = true
  end
end

local function build(weeks_arg)
  local meta = load_vars()
  local year = tonumber((stringify(meta["term"]) or ""):match("%d%d%d%d"))
  if not year then error("course-calendar: could not read the year from the `term` variable") end

  -- Check every 'Weekday, Month D' variable, not only the ones in the calendar
  for key, value in pairs(meta) do
    local s = pandoc.utils.type(value) == "Inlines" and stringify(value) or nil
    local d = s and parse_date(s, year)
    if d and not d.ok then
      warn(string.format("%s is '%s', but that date is a %s", key, s, d.actual))
    end
  end

  local monday_value = stringify(meta["week0-monday"])
  local monday = monday_value and parse_date(monday_value, year)
  if not monday then error("course-calendar: add `week0-monday: 'Monday, Month D'` to _variables.yml") end

  local first, last = 0, FINALS
  if weeks_arg and weeks_arg ~= "" then
    local a, b = weeks_arg:match("^(%d+)%s*%-%s*(%w+)$")
    a = a or weeks_arg:match("^(%d+)$")
    first = tonumber(a) or 0
    last = (b == "finals") and FINALS or tonumber(b) or first
  end

  -- cells[week][column] = list of events
  local cells = {}
  for w = 0, FINALS do cells[w] = {} end
  for _, ev in ipairs(meta["calendar-events"] or {}) do
    local key = stringify(ev.date)
    local value = stringify(meta[key])
    local d = value and parse_date(value, year)
    if not d then
      warn("calendar event '" .. stringify(ev.label) .. "' points to '" .. tostring(key) ..
        "', which is missing or not written as 'Weekday, Month D'")
    else
      local week = math.floor((d.time - monday.time) / DAY / 7 + 1e-6)
      local col = d.wday - 1
      if week < 0 or week > FINALS or col < 1 then
        warn(key .. " (" .. value .. ") falls outside the Monday-Saturday calendar for weeks 0-10 and finals")
      else
        cells[week][col] = cells[week][col] or {}
        table.insert(cells[week][col], {
          d = d,
          label = stringify(ev.label),
          type = stringify(ev.type) or "info",
          time = ev.time and stringify(meta[stringify(ev.time)]),
        })
      end
    end
  end

  local h = { CSS, '<div class="course-calendar-wrap"><table class="course-calendar">',
    "<thead><tr><th>Week<br>(Monday start date)</th><th>Topic</th>" }
  for _, c in ipairs(COLUMNS) do table.insert(h, "<th>" .. c .. "</th>") end
  table.insert(h, "</tr></thead><tbody>")

  for w = first, last do
    local week_label = (w == FINALS) and "Finals" or ("Week " .. w)
    local topic_key = (w == FINALS) and "finals-week-topic" or ("week" .. w .. "-topic")
    local topic = stringify(meta[topic_key]) or ""
    table.insert(h, string.format(
      '<tr><td class="cal-week">%s<br><strong>%s</strong></td><td class="cal-topic">%s</td>',
      week_label, short_date(monday.time + w * 7 * DAY), escape(topic)))
    for col = 1, #COLUMNS do
      local evs = cells[w][col]
      if not evs then
        table.insert(h, "<td></td>")
      else
        local d = evs[1].d
        local time
        for _, e in ipairs(evs) do time = time or e.time end
        local cell = { '<div class="cal-date">' .. short_date(d.time) ..
          (time and (" @ " .. escape(time)) or "") }
        if not d.ok then
          table.insert(cell, string.format(
            ' <span class="cal-warning" title="Written as %s, but this date is a %s">⚠</span>',
            d.written, d.actual))
        end
        table.insert(cell, "</div>")
        for _, e in ipairs(evs) do
          table.insert(cell, string.format('<div class="cal-%s">%s</div>', escape(e.type), escape(e.label)))
        end
        table.insert(h, "<td>" .. table.concat(cell) .. "</td>")
      end
    end
    table.insert(h, "</tr>")
  end
  table.insert(h, "</tbody></table></div>")
  return table.concat(h, "\n")
end

return {
  ["course-calendar"] = function(args, kwargs)
    if not quarto.doc.is_format("html") then return pandoc.Null() end
    return pandoc.RawBlock("html", build(stringify(kwargs["weeks"])))
  end
}
