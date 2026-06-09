/**
 * Pomodoro Timer – main application script
 * Handles timer logic, settings persistence (localStorage),
 * theme switching, sound (Web Audio API), and statistics.
 */

// ─── Constants ────────────────────────────────────────────────────────────────

const STORAGE_KEY = "pomodoroSettings";
const STATS_KEY = "pomodoroStats";

const DEFAULT_SETTINGS = {
  workDuration: 25,
  breakDuration: 5,
  theme: "light",
  soundStart: true,
  soundEnd: true,
  soundTick: false,
};

const DEFAULT_STATS = {
  totalSessions: 0,
  totalMinutes: 0,
  streak: 0,
  lastSessionDate: null,
};

// ─── State ────────────────────────────────────────────────────────────────────

let settings = loadSettings();
let stats = loadStats();

let timeLeft = 0;
let totalTime = 0;
let isRunning = false;
let isBreak = false;
let intervalId = null;
let audioCtx = null;

// ─── DOM References ───────────────────────────────────────────────────────────

const timerTimeEl = document.getElementById("timer-time");
const timerLabelEl = document.getElementById("timer-label");
const sessionBadgeEl = document.getElementById("session-badge");
const startPauseBtn = document.getElementById("btn-start-pause");
const resetBtn = document.getElementById("btn-reset");
const progressCircle = document.getElementById("progress-circle");
const settingsBtn = document.getElementById("btn-settings");
const settingsOverlay = document.getElementById("settings-overlay");
const settingsCloseBtn = document.getElementById("settings-close");
const saveSettingsBtn = document.getElementById("btn-save-settings");
const toastEl = document.getElementById("toast");

// Stats display (timer card inline + stats card big)
const statSessionsEl = document.getElementById("stat-sessions");
const statMinutesEl = document.getElementById("stat-minutes");
const statStreakEl = document.getElementById("stat-streak");
const statSessionsBigEl = document.getElementById("stat-sessions-big");
const statMinutesBigEl = document.getElementById("stat-minutes-big");
const statStreakBigEl = document.getElementById("stat-streak-big");

// Settings chips
const workChips = document.querySelectorAll(".chip[data-group='work']");
const breakChips = document.querySelectorAll(".chip[data-group='break']");
const themeChips = document.querySelectorAll(".chip[data-group='theme']");

// Sound toggles
const soundStartToggle = document.getElementById("sound-start");
const soundEndToggle = document.getElementById("sound-end");
const soundTickToggle = document.getElementById("sound-tick");

// ─── Circular Progress Ring ───────────────────────────────────────────────────

const RADIUS = 88;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

progressCircle.style.strokeDasharray = CIRCUMFERENCE;

function setProgress(fraction) {
  const offset = CIRCUMFERENCE * (1 - Math.max(0, Math.min(1, fraction)));
  progressCircle.style.strokeDashoffset = offset;
}

// ─── Settings Persistence ─────────────────────────────────────────────────────

function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_SETTINGS };
    return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

function saveSettings(newSettings) {
  settings = { ...settings, ...newSettings };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch {
    /* storage unavailable */
  }
}

// ─── Statistics Persistence ───────────────────────────────────────────────────

function loadStats() {
  try {
    const raw = localStorage.getItem(STATS_KEY);
    if (!raw) return { ...DEFAULT_STATS };
    return { ...DEFAULT_STATS, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULT_STATS };
  }
}

function saveStatsData() {
  try {
    localStorage.setItem(STATS_KEY, JSON.stringify(stats));
  } catch {
    /* storage unavailable */
  }
}

function recordCompletedSession(minutes) {
  stats.totalSessions += 1;
  stats.totalMinutes += minutes;

  const today = new Date().toDateString();
  if (stats.lastSessionDate === today) {
    stats.streak += 1;
  } else if (
    stats.lastSessionDate ===
    new Date(Date.now() - 86400000).toDateString()
  ) {
    stats.streak += 1;
  } else {
    stats.streak = 1;
  }
  stats.lastSessionDate = today;
  saveStatsData();
  renderStats();
}

function renderStats() {
  statSessionsEl.textContent = stats.totalSessions;
  statMinutesEl.textContent = stats.totalMinutes;
  statStreakEl.textContent = stats.streak;
  statSessionsBigEl.textContent = stats.totalSessions;
  statMinutesBigEl.textContent = stats.totalMinutes;
  statStreakBigEl.textContent = stats.streak;
}

// ─── Theme ────────────────────────────────────────────────────────────────────

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
}

// ─── Sound (Web Audio API) ────────────────────────────────────────────────────

function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
}

function playTone(frequency, duration, type = "sine", volume = 0.3) {
  try {
    const ctx = getAudioContext();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);

    gainNode.gain.setValueAtTime(volume, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(
      0.001,
      ctx.currentTime + duration
    );

    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + duration);
  } catch {
    /* audio unavailable */
  }
}

function playStartSound() {
  if (!settings.soundStart) return;
  playTone(523.25, 0.15); // C5
  setTimeout(() => playTone(659.25, 0.15), 160); // E5
  setTimeout(() => playTone(783.99, 0.25), 320); // G5
}

function playEndSound() {
  if (!settings.soundEnd) return;
  playTone(783.99, 0.15); // G5
  setTimeout(() => playTone(659.25, 0.15), 160); // E5
  setTimeout(() => playTone(523.25, 0.3), 320); // C5
  setTimeout(() => playTone(392.0, 0.5), 500); // G4
}

function playTickSound() {
  if (!settings.soundTick) return;
  playTone(880, 0.04, "square", 0.05);
}

// ─── Timer Core ───────────────────────────────────────────────────────────────

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function initTimer() {
  clearInterval(intervalId);
  isRunning = false;
  isBreak = false;
  totalTime = settings.workDuration * 60;
  timeLeft = totalTime;
  updateTimerDisplay();
  setProgress(1);
  startPauseBtn.textContent = "▶ スタート";
  sessionBadgeEl.textContent = "🍅 作業中";
  sessionBadgeEl.classList.remove("break");
  updateProgressColor();
}

function updateTimerDisplay() {
  timerTimeEl.textContent = formatTime(timeLeft);
  timerLabelEl.textContent = isBreak
    ? `休憩 ${settings.breakDuration}分`
    : `作業 ${settings.workDuration}分`;
  document.title = `${formatTime(timeLeft)} – ${isBreak ? "休憩" : "作業"} | Pomodoro`;
}

function updateProgressColor() {
  if (isBreak) {
    progressCircle.style.stroke = "var(--break-progress)";
  } else {
    progressCircle.style.stroke = "var(--progress-fill)";
  }
}

function tick() {
  if (timeLeft <= 0) {
    handleSessionEnd();
    return;
  }
  timeLeft -= 1;
  playTickSound();
  updateTimerDisplay();
  setProgress(timeLeft / totalTime);
}

function handleSessionEnd() {
  clearInterval(intervalId);
  isRunning = false;

  if (!isBreak) {
    recordCompletedSession(settings.workDuration);
    playEndSound();
    showToast(`🎉 作業完了！${settings.breakDuration}分の休憩をどうぞ`);
    startBreak();
  } else {
    playEndSound();
    showToast("☕ 休憩終了！次のセッションを始めましょう");
    initTimer();
    startPauseBtn.textContent = "▶ スタート";
  }
}

function startBreak() {
  isBreak = true;
  totalTime = settings.breakDuration * 60;
  timeLeft = totalTime;
  isRunning = true;
  playStartSound();
  startPauseBtn.textContent = "⏸ 一時停止";
  sessionBadgeEl.textContent = "☕ 休憩中";
  sessionBadgeEl.classList.add("break");
  updateProgressColor();
  updateTimerDisplay();
  setProgress(1);
  intervalId = setInterval(tick, 1000);
}

function toggleStartPause() {
  if (isRunning) {
    clearInterval(intervalId);
    isRunning = false;
    startPauseBtn.textContent = "▶ 再開";
  } else {
    if (timeLeft === totalTime && !isBreak) {
      playStartSound();
    }
    isRunning = true;
    startPauseBtn.textContent = "⏸ 一時停止";
    intervalId = setInterval(tick, 1000);
  }
}

// ─── Settings Panel ───────────────────────────────────────────────────────────

function openSettings() {
  populateSettingsUI();
  settingsOverlay.classList.add("open");
}

function closeSettings() {
  settingsOverlay.classList.remove("open");
}

function populateSettingsUI() {
  // Work duration chips
  workChips.forEach((chip) => {
    chip.classList.toggle(
      "selected",
      parseInt(chip.dataset.value) === settings.workDuration
    );
  });

  // Break duration chips
  breakChips.forEach((chip) => {
    chip.classList.toggle(
      "selected",
      parseInt(chip.dataset.value) === settings.breakDuration
    );
  });

  // Theme chips
  themeChips.forEach((chip) => {
    chip.classList.toggle("selected", chip.dataset.value === settings.theme);
  });

  // Sound toggles
  soundStartToggle.checked = settings.soundStart;
  soundEndToggle.checked = settings.soundEnd;
  soundTickToggle.checked = settings.soundTick;
}

function collectSettingsFromUI() {
  const workChipSelected = document.querySelector(
    ".chip[data-group='work'].selected"
  );
  const breakChipSelected = document.querySelector(
    ".chip[data-group='break'].selected"
  );
  const themeChipSelected = document.querySelector(
    ".chip[data-group='theme'].selected"
  );

  return {
    workDuration: workChipSelected
      ? parseInt(workChipSelected.dataset.value)
      : settings.workDuration,
    breakDuration: breakChipSelected
      ? parseInt(breakChipSelected.dataset.value)
      : settings.breakDuration,
    theme: themeChipSelected ? themeChipSelected.dataset.value : settings.theme,
    soundStart: soundStartToggle.checked,
    soundEnd: soundEndToggle.checked,
    soundTick: soundTickToggle.checked,
  };
}

function onSaveSettings() {
  const newSettings = collectSettingsFromUI();
  const timerWasRunning = isRunning;

  saveSettings(newSettings);
  applyTheme(settings.theme);

  // Reset timer with new durations (only if not mid-session)
  if (!isRunning && !isBreak) {
    initTimer();
  } else if (!isRunning && isBreak) {
    // Update break display without resetting break
    updateTimerDisplay();
  }

  closeSettings();
  showToast("✅ 設定を保存しました");
}

// ─── Chip selection logic ─────────────────────────────────────────────────────

function setupChipGroup(chips) {
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("selected"));
      chip.classList.add("selected");
    });
  });
}

// ─── Toast ────────────────────────────────────────────────────────────────────

let toastTimeout = null;

function showToast(message, duration = 2800) {
  if (toastTimeout) clearTimeout(toastTimeout);
  toastEl.textContent = message;
  toastEl.classList.add("show");
  toastTimeout = setTimeout(() => toastEl.classList.remove("show"), duration);
}

// ─── Event Listeners ──────────────────────────────────────────────────────────

startPauseBtn.addEventListener("click", toggleStartPause);
resetBtn.addEventListener("click", () => {
  clearInterval(intervalId);
  initTimer();
  showToast("🔄 タイマーをリセットしました");
});
settingsBtn.addEventListener("click", openSettings);
settingsCloseBtn.addEventListener("click", closeSettings);
saveSettingsBtn.addEventListener("click", onSaveSettings);

// Close settings when clicking overlay background
settingsOverlay.addEventListener("click", (e) => {
  if (e.target === settingsOverlay) closeSettings();
});

// Chip groups
setupChipGroup(workChips);
setupChipGroup(breakChips);
setupChipGroup(themeChips);

// Keyboard shortcut: Space = start/pause, R = reset, S = open settings
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "BUTTON") return;
  if (e.code === "Space") {
    e.preventDefault();
    toggleStartPause();
  } else if (e.code === "KeyR") {
    clearInterval(intervalId);
    initTimer();
  } else if (e.code === "KeyS") {
    settingsOverlay.classList.contains("open")
      ? closeSettings()
      : openSettings();
  }
});

// ─── Initialise ───────────────────────────────────────────────────────────────

applyTheme(settings.theme);
initTimer();
renderStats();
populateSettingsUI();
