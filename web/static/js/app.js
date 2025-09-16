// Estado de la aplicación
let appState = {
  isRecording: false,
  recordingStartTime: null,
  recordingTimer: null,
  systemStatus: null,
  currentText: ''
};

// Elementos del DOM
const elements = {
  recordBtn: document.getElementById('record-btn'),
  recordingIndicator: document.getElementById('recording-indicator'),
  recordingStatus: document.getElementById('recording-status'),
  recordingTimer: document.getElementById('recording-timer'),
  timerText: document.getElementById('timer-text'),
  whisperStatus: document.getElementById('whisper-status'),
  llmStatus: document.getElementById('llm-status'),
  useLlmCheckbox: document.getElementById('use-llm-checkbox'),
  currentTranscription: document.getElementById('current-transcription'),
  dictationsList: document.getElementById('dictations-list'),
  loadingOverlay: document.getElementById('loading-overlay'),
  toastContainer: document.getElementById('toast-container'),
  themeToggle: document.getElementById('theme-toggle'),
  copyCurrentBtn: document.getElementById('copy-current-btn'),
  downloadCurrentBtn: document.getElementById('download-current-btn'),
  translateBtn: document.getElementById('translate-btn'),
  summaryBtn: document.getElementById('generate-summary-btn'),
  summarySection: document.getElementById('summary-section'),
  summaryBox: document.getElementById('summary-box'),
  translationSection: document.getElementById('translation-section'),
  translationBox: document.getElementById('translation-box')
};

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
  initializeApp();
});

// Inicializar la aplicación
async function initializeApp() {
  try {
    initTheme();
    await loadSystemStatus();
    await loadRecentDictations();
    setupEventListeners();
    
    // Animación de entrada para las tarjetas
    animateCards();
    
    console.log('Aplicación inicializada correctamente');
  } catch (error) {
    console.error('Error al inicializar la aplicación:', error);
    showToast('Error al inicializar la aplicación', 'error');
  }
}

// Animación de entrada de las tarjetas
function animateCards() {
  const cards = document.querySelectorAll('.status-panel, .recording-section, .transcription-section, .dictations-section');
  cards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    
    setTimeout(() => {
      card.style.transition = 'all 0.6s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, index * 100);
  });
}

// Cargar estado del sistema
async function loadSystemStatus() {
  try {
    const response = await fetch('/api/status');
    const data = await response.json();
    appState.systemStatus = data;

    // Whisper
    elements.whisperStatus.textContent = data.whisper_available ? 'Disponible' : 'No disponible';
    elements.whisperStatus.classList.remove('ok', 'error');
    elements.whisperStatus.classList.add(data.whisper_available ? 'ok' : 'error');

    // LLM
    elements.llmStatus.textContent = data.llm_available ? 'Disponible' : 'No disponible';
    elements.llmStatus.classList.remove('ok', 'error');
    elements.llmStatus.classList.add(data.llm_available ? 'ok' : 'error');

    // Controles
    if (elements.recordBtn) elements.recordBtn.disabled = !data.whisper_available;
    if (elements.useLlmCheckbox) elements.useLlmCheckbox.disabled = !data.llm_available;
  } catch (error) {
    console.error('Error al cargar estado del sistema:', error);
    elements.whisperStatus.textContent = 'Error';
    elements.whisperStatus.classList.remove('ok');
    elements.whisperStatus.classList.add('error');
  }
}

// Eventos
function setupEventListeners() {
  if (elements.recordBtn) elements.recordBtn.addEventListener('click', toggleRecording);

  if (elements.useLlmCheckbox) {
    elements.useLlmCheckbox.addEventListener('change', function () {
      if (this.checked && !(appState.systemStatus && appState.systemStatus.llm_available)) {
        showToast('LLM no está disponible', 'warning');
        this.checked = false;
      }
    });
  }

  if (elements.copyCurrentBtn) {
    elements.copyCurrentBtn.addEventListener('click', () => {
      if (!appState.currentText) return;
      copyToClipboard(appState.currentText);
    });
  }
  if (elements.downloadCurrentBtn) {
    elements.downloadCurrentBtn.addEventListener('click', () => {
      if (!appState.currentText) return;
      const ts = new Date();
      const name = `transcripcion_${ts.getFullYear()}${String(ts.getMonth() + 1).padStart(2, '0')}${String(ts.getDate()).padStart(2, '0')}_${String(ts.getHours()).padStart(2, '0')}${String(ts.getMinutes()).padStart(2, '0')}`;
      downloadText(`${name}.txt`, appState.currentText);
    });
  }

  if (elements.translateBtn) elements.translateBtn.addEventListener('click', translateCurrentText);
  if (elements.summaryBtn) elements.summaryBtn.addEventListener('click', generateSummary);

  if (elements.themeToggle) elements.themeToggle.addEventListener('click', toggleTheme);
}

// Alternar Grabación
async function toggleRecording() {
  if (appState.isRecording) await stopRecording();
  else await startRecording();
}

// Iniciar Grabación
async function startRecording() {
  try {
    const useLlm = !!(elements.useLlmCheckbox && elements.useLlmCheckbox.checked);
    const response = await fetch('/api/start_recording', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ use_llm: useLlm })
    });
    const data = await response.json();
    if (response.ok) {
      appState.isRecording = true;
      appState.recordingStartTime = Date.now();
      updateRecordingUI(true);
      startRecordingTimer();
      showToast('Grabación iniciada', 'success');
      // Reset secciones secundarias
      if (elements.summaryBox) { elements.summaryBox.innerHTML = ''; }
      if (elements.translationSection) { elements.translationSection.style.display = 'none'; if (elements.translationBox) elements.translationBox.innerHTML = ''; }
    } else {
      throw new Error(data.error || 'Error al iniciar Grabación');
    }
  } catch (error) {
    console.error('Error al iniciar Grabación:', error);
    showToast('Error al iniciar Grabación: ' + error.message, 'error');
  }
}

// Detener Grabación
async function stopRecording() {
  try {
    showLoadingOverlay(true);
    const useLlm = !!(elements.useLlmCheckbox && elements.useLlmCheckbox.checked);
    const response = await fetch('/api/stop_recording', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ use_llm: useLlm })
    });
    const data = await response.json();
    if (response.ok) {
      if (data.result && data.result.success) {
        showCurrentTranscription(data.result.text);
        await loadRecentDictations();
        showToast('Transcripción completada', 'success');
      } else {
        throw new Error((data.result && data.result.error) || 'Error al procesar audio');
      }
    } else {
      throw new Error(data.error || 'Error al detener Grabación');
    }
  } catch (error) {
    console.error('Error al detener Grabación:', error);
    showToast('Error al procesar audio: ' + error.message, 'error');
  } finally {
    appState.isRecording = false;
    updateRecordingUI(false);
    stopRecordingTimer();
    showLoadingOverlay(false);
  }
}

// Generar resumen bajo demanda
async function generateSummary() {
  if (!appState.currentText) return showToast('No hay Transcripción disponible', 'warning');
  if (!(appState.systemStatus && appState.systemStatus.llm_available)) return showToast('LLM no está disponible', 'warning');
  try {
    elements.summaryBtn && (elements.summaryBtn.disabled = true);
    const resp = await fetch('/api/postprocess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: appState.currentText, do_summary: true, do_translate_en: false })
    });
    const data = await resp.json();
    if (resp.ok && data.result && data.result.summary) {
      showSummary(data.result.summary);
    } else {
      throw new Error(data.error || 'No fue posible generar el resumen');
    }
  } catch (e) {
    console.error('Error al generar resumen:', e);
    showToast('Error al generar resumen', 'error');
  } finally {
    elements.summaryBtn && (elements.summaryBtn.disabled = false);
  }
}

// Traducir al inglés bajo demanda
async function translateCurrentText() {
  if (!appState.currentText) return showToast('No hay Transcripción disponible', 'warning');
  if (!(appState.systemStatus && appState.systemStatus.llm_available)) return showToast('LLM no está disponible', 'warning');
  try {
    elements.translateBtn && (elements.translateBtn.disabled = true);
    const resp = await fetch('/api/postprocess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: appState.currentText, do_summary: false, do_translate_en: true })
    });
    const data = await resp.json();
    if (resp.ok && data.result && data.result.translation_en) {
      showTranslation(data.result.translation_en);
    } else {
      throw new Error(data.error || 'No fue posible traducir');
    }
  } catch (e) {
    console.error('Error al traducir:', e);
    showToast('Error al traducir', 'error');
  } finally {
    elements.translateBtn && (elements.translateBtn.disabled = false);
  }
}

// UI Grabación
function updateRecordingUI(isRecording) {
  const btn = elements.recordBtn;
  const indicator = elements.recordingIndicator;
  const status = elements.recordingStatus;
  const timer = elements.recordingTimer;
  if (!btn || !indicator || !status || !timer) return;
  if (isRecording) {
    btn.classList.add('recording');
    btn.innerHTML = '<i class="fas fa-stop"></i><span>Detener Grabación</span>';
    indicator.classList.add('recording');
    status.textContent = 'Grabando...';
    timer.style.display = 'flex';
  } else {
    btn.classList.remove('recording');
    btn.innerHTML = '<i class="fas fa-microphone"></i><span>Iniciar Grabación</span>';
    indicator.classList.remove('recording');
    status.textContent = 'Listo';
    timer.style.display = 'none';
  }
}

function startRecordingTimer() {
  appState.recordingTimer = setInterval(() => {
    if (appState.recordingStartTime) {
      const elapsed = Date.now() - appState.recordingStartTime;
      const minutes = Math.floor(elapsed / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);
      elements.timerText.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
  }, 1000);
}

function stopRecordingTimer() {
  if (appState.recordingTimer) {
    clearInterval(appState.recordingTimer);
    appState.recordingTimer = null;
    appState.recordingStartTime = null;
  }
}

// Transcripción actual con animación
function showCurrentTranscription(text) {
  const box = elements.currentTranscription;
  const safe = (text || '').toString();
  
  // Animación de aparición
  box.style.opacity = '0';
  box.style.transform = 'translateY(20px)';
  
  setTimeout(() => {
    box.innerHTML = `<p>${escapeHtml(safe)}</p>`;
    box.classList.add('has-content');
    appState.currentText = safe;
    
    // Animación de entrada
    box.style.transition = 'all 0.4s ease';
    box.style.opacity = '1';
    box.style.transform = 'translateY(0)';
  }, 100);
}

// Dictados
async function loadRecentDictations() {
  try {
    const response = await fetch('/api/dictations');
    const data = await response.json();
    if (response.ok) {
      displayDictations(data.dictations || []);
    } else {
      throw new Error(data.error || 'Error al cargar dictados');
    }
  } catch (error) {
    console.error('Error al cargar dictados:', error);
    showToast('Error al cargar dictados', 'error');
  }
}

function displayDictations(dictations) {
  const container = elements.dictationsList;
  if (!Array.isArray(dictations) || dictations.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-microphone-slash"></i>
        <p>No hay dictados recientes</p>
      </div>
    `;
    return;
  }
  container.innerHTML = dictations
    .map((dictation) => `
      <div class="dictation-item">
        <div class="dictation-header">
          <span class="dictation-time">${formatTimestamp(dictation.timestamp)}</span>
        </div>
        <div class="dictation-text">${dictation.text}</div>
        <div class="dictation-actions">
          <button class="action-btn copy" onclick="copyToClipboard('${escapeHtml(dictation.text)}')" title="Copiar">
            <i class="fas fa-copy"></i>
          </button>
          <button class="action-btn delete" onclick="deleteDictation('${dictation.id}')" title="Eliminar">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    `)
    .join('');
}

function formatTimestamp(timestamp) {
  const date = new Date((timestamp || 0) * 1000);
  return date.toLocaleString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Texto copiado al portapapeles', 'success');
  } catch (error) {
    console.error('Error al copiar:', error);
    showToast('Error al copiar texto', 'error');
  }
}

function downloadText(filename, text) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Archivo descargado', 'success');
}

async function deleteDictation(id) {
  if (!confirm('¿estás seguro de que quieres eliminar este dictado?')) return;
  try {
    const response = await fetch(`/api/dictations/${id}`, { method: 'DELETE' });
    const data = await response.json();
    if (response.ok) {
      showToast('Dictado eliminado', 'success');
      await loadRecentDictations();
    } else {
      throw new Error(data.error || 'Error al eliminar dictado');
    }
  } catch (error) {
    console.error('Error al eliminar dictado:', error);
    showToast('Error al eliminar dictado', 'error');
  }
}

// Overlay y toasts
function showLoadingOverlay(show) {
  if (show) elements.loadingOverlay.classList.add('show');
  else elements.loadingOverlay.classList.remove('show');
}

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  elements.toastContainer.appendChild(toast);
  
  // Animación de entrada
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';
    setTimeout(() => toast.remove(), 300);
  }, 2700);
}

// Tema mejorado
function initTheme() {
  try {
    const pref = localStorage.getItem('theme') || 'auto';
    const isDark = pref === 'dark' || (pref === 'auto' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    setTheme(isDark ? 'dark' : 'light');
  } catch (e) { /* ignore */ }
}

function toggleTheme() {
  const isDark = document.documentElement.classList.contains('theme-dark');
  setTheme(isDark ? 'light' : 'dark');
  
  // Animación suave del toggle
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.style.transform = 'scale(0.9)';
    setTimeout(() => {
      toggle.style.transform = 'scale(1)';
    }, 150);
  }
}

function setTheme(mode) {
  const html = document.documentElement;
  
  if (mode === 'dark') {
    html.classList.add('theme-dark');
    try { localStorage.setItem('theme', 'dark'); } catch (e) {}
    const t = document.getElementById('theme-toggle');
    if (t) t.innerHTML = '<i class="fas fa-sun"></i>';
  } else {
    html.classList.remove('theme-dark');
    try { localStorage.setItem('theme', 'light'); } catch (e) {}
    const t = document.getElementById('theme-toggle');
    if (t) t.innerHTML = '<i class="fas fa-moon"></i>';
  }
  
  // Actualizar meta theme-color
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    metaThemeColor.content = mode === 'dark' ? '#0f172a' : '#6366f1';
  }
}

// Errores globales
window.addEventListener('error', function (event) {
  console.error('Error global:', event.error);
  showToast('Ha ocurrido un error inesperado', 'error');
});

window.addEventListener('unhandledrejection', function (event) {
  console.error('Promise rechazada:', event.reason);
  showToast('Error de conexión', 'error');
});

// Mostrar resumen
function showSummary(text) {
  if (!elements.summarySection || !elements.summaryBox) return;
  elements.summaryBox.innerHTML = `<p>${escapeHtml(text)}</p>`;
  elements.summarySection.style.display = 'block';
  
  // Animación de entrada
  elements.summarySection.style.opacity = '0';
  elements.summarySection.style.transform = 'translateY(20px)';
  setTimeout(() => {
    elements.summarySection.style.transition = 'all 0.4s ease';
    elements.summarySection.style.opacity = '1';
    elements.summarySection.style.transform = 'translateY(0)';
  }, 100);
}

// Mostrar traducción
function showTranslation(text) {
  if (!elements.translationSection || !elements.translationBox) return;
  elements.translationBox.innerHTML = `<p>${escapeHtml(text)}</p>`;
  elements.translationSection.style.display = 'block';
  
  // Animación de entrada
  elements.translationSection.style.opacity = '0';
  elements.translationSection.style.transform = 'translateY(20px)';
  setTimeout(() => {
    elements.translationSection.style.transition = 'all 0.4s ease';
    elements.translationSection.style.opacity = '1';
    elements.translationSection.style.transform = 'translateY(0)';
  }, 100);
}