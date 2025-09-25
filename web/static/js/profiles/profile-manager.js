/**
 * AudioLetra Profile Management JavaScript
 * Handles profile dropdown integration and processing
 */
class ProfileManager {
    constructor() {
        this.profiles = [];
        this.currentProfile = null;
        this.results = new Map();
        this.isProcessing = false;
        this.apiBaseUrl = '/llm';
        
        this.init();
    }
    
    async init() {
        await this.loadProfiles();
        this.setupEventListeners();
        this.updateUI();
    }
    
    async loadProfiles() {
        try {
            const response = await fetch(${this.apiBaseUrl}/profiles);
            if (!response.ok) {
                throw new Error(HTTP error! status: );
            }
            
            const data = await response.json();
            this.profiles = data.profiles;
            console.log('Profiles loaded:', this.profiles);
            
        } catch (error) {
            console.error('Error loading profiles:', error);
            this.showError('Error al cargar los perfiles disponibles');
        }
    }
    
    setupEventListeners() {
        // Profile dropdown change
        const profileSelect = document.getElementById('profile-select');
        if (profileSelect) {
            profileSelect.addEventListener('change', (e) => {
                this.selectProfile(e.target.value);
            });
        }
        
        // Process button click
        const processBtn = document.getElementById('process-btn');
        if (processBtn) {
            processBtn.addEventListener('click', () => {
                this.processText();
            });
        }
        
        // Download buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('download-btn')) {
                const resultId = e.target.dataset.resultId;
                const format = e.target.dataset.format;
                this.downloadResult(resultId, format);
            }
        });
        
        // Result tab switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('result-tab')) {
                const profileId = e.target.dataset.profileId;
                this.showResult(profileId);
            }
        });
    }
    
    selectProfile(profileId) {
        this.currentProfile = this.profiles.find(p => p.id === profileId);
        this.updateUI();
        
        // Show/hide language selector for translate profile
        this.toggleLanguageSelector(profileId === 'translate');
    }
    
    toggleLanguageSelector(show) {
        const langSelector = document.getElementById('language-selector');
        if (langSelector) {
            langSelector.style.display = show ? 'block' : 'none';
        }
    }
    
    async processText() {
        if (this.isProcessing) return;
        
        const text = this.getInputText();
        if (!text.trim()) {
            this.showError('Por favor, ingresa texto para procesar');
            return;
        }
        
        if (!this.currentProfile) {
            this.showError('Por favor, selecciona un perfil');
            return;
        }
        
        this.isProcessing = true;
        this.showProcessingIndicator();
        
        try {
            const parameters = this.getParameters();
            const result = await this.callProcessAPI(text, parameters);
            
            if (result.success) {
                this.addResult(result);
                this.showResult(this.currentProfile.id);
                this.showSuccess('Texto procesado exitosamente');
            } else {
                this.showError(result.error?.message || 'Error al procesar el texto');
            }
            
        } catch (error) {
            console.error('Processing error:', error);
            this.showError('Error de conexión. Por favor, intenta nuevamente.');
        } finally {
            this.isProcessing = false;
            this.hideProcessingIndicator();
        }
    }
    
    async callProcessAPI(text, parameters) {
        const response = await fetch(${this.apiBaseUrl}/process, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                profile_id: this.currentProfile.id,
                text: text,
                parameters: parameters
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error?.message || 'Error del servidor');
        }
        
        return await response.json();
    }
    
    getInputText() {
        // Usar el texto de la transcripción actual de AudioLetra
        const currentTranscription = document.getElementById('current-transcription');
        if (currentTranscription && currentTranscription.textContent) {
            return currentTranscription.textContent.trim();
        }
        
        // Fallback al textarea si existe
        const textArea = document.getElementById('transcription-text');
        return textArea ? textArea.value : '';
    }
    
    getParameters() {
        const parameters = {};
        
        // Add language parameter for translate profile
        if (this.currentProfile.id === 'translate') {
            const langSelect = document.getElementById('target-language');
            if (langSelect) {
                parameters.target_language = langSelect.value;
            }
        }
        
        return parameters;
    }
    
    addResult(result) {
        this.results.set(result.profile_id, result);
        this.updateResultTabs();
    }
    
    showResult(profileId) {
        const result = this.results.get(profileId);
        if (!result) return;
        
        // Hide all result panels
        document.querySelectorAll('.result-panel').forEach(panel => {
            panel.style.display = 'none';
        });
        
        // Show selected result panel
        const resultPanel = document.getElementById(
esult-);
        if (resultPanel) {
            resultPanel.style.display = 'block';
            resultPanel.querySelector('.result-content').textContent = result.output;
        }
        
        // Update active tab
        document.querySelectorAll('.result-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const activeTab = document.querySelector([data-profile-id=""]);
        if (activeTab) {
            activeTab.classList.add('active');
        }
    }
    
    updateResultTabs() {
        const tabsContainer = document.getElementById('result-tabs');
        if (!tabsContainer) return;
        
        tabsContainer.innerHTML = '';
        
        this.results.forEach((result, profileId) => {
            const profile = this.profiles.find(p => p.id === profileId);
            const tab = document.createElement('button');
            tab.className = 'result-tab';
            tab.dataset.profileId = profileId;
            tab.textContent = profile ? profile.name : profileId;
            
            if (profileId === this.currentProfile?.id) {
                tab.classList.add('active');
            }
            
            tabsContainer.appendChild(tab);
        });
    }
    
    async downloadResult(resultId, format) {
        try {
            const response = await fetch(${this.apiBaseUrl}/download/, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    format: format,
                    filename: 
esultado.
                })
            });
            
            if (!response.ok) {
                throw new Error('Error al descargar el archivo');
            }
            
            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 
esultado.;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Error al descargar el archivo');
        }
    }
    
    updateUI() {
        this.updateProfileDropdown();
        this.updateProcessButton();
        this.updateResultPanels();
    }
    
    updateProfileDropdown() {
        const profileSelect = document.getElementById('profile-select');
        if (!profileSelect) return;
        
        profileSelect.innerHTML = '<option value="">Selecciona un perfil...</option>';
        
        this.profiles.forEach(profile => {
            const option = document.createElement('option');
            option.value = profile.id;
            option.textContent = profile.name;
            profileSelect.appendChild(option);
        });
    }
    
    updateProcessButton() {
        const processBtn = document.getElementById('process-btn');
        if (processBtn) {
            processBtn.disabled = !this.currentProfile || this.isProcessing;
            processBtn.textContent = this.isProcessing ? 'Procesando...' : 'Procesar';
        }
    }
    
    updateResultPanels() {
        const resultsContainer = document.getElementById('results-container');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = '';
        
        this.results.forEach((result, profileId) => {
            const profile = this.profiles.find(p => p.id === profileId);
            const panel = document.createElement('div');
            panel.id = 
esult-;
            panel.className = 'result-panel';
            panel.style.display = 'none';
            
            panel.innerHTML = 
                <div class="result-header">
                    <h3></h3>
                    <div class="result-actions">
                        <button class="download-btn" data-result-id="" data-format="txt">TXT</button>
                        <button class="download-btn" data-result-id="" data-format="docx">DOCX</button>
                        <button class="download-btn" data-result-id="" data-format="pdf">PDF</button>
                    </div>
                </div>
                <div class="result-content"></div>
            ;
            
            resultsContainer.appendChild(panel);
        });
    }
    
    showProcessingIndicator() {
        const indicator = document.getElementById('processing-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }
    
    hideProcessingIndicator() {
        const indicator = document.getElementById('processing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    showSuccess(message) {
        this.showMessage(message, 'success');
    }
    
    showMessage(message, type) {
        // Create or update message element
        let messageEl = document.getElementById('message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'message';
            document.body.appendChild(messageEl);
        }
        
        messageEl.textContent = message;
        messageEl.className = message ;
        messageEl.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.profileManager = new ProfileManager();
});
