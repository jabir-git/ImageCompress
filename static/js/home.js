// Home page unified form handler

// Utility function to format bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Utility function to download file from response
async function downloadFile(response, filename) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function replaceExtension(filename, newExt) {
    const lastDot = filename.lastIndexOf('.');
    const base = lastDot > -1 ? filename.slice(0, lastDot) : filename;
    return `${base}.${newExt}`;
}

// UI State Manager
class FormUIManager {
    constructor() {
        this.imageFilesInput = document.getElementById('imageFiles');
        this.fileCountDisplay = document.getElementById('fileCountDisplay');
        this.fileCountText = document.getElementById('fileCountText');
        this.processingLoading = document.getElementById('processingLoading');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsList = document.getElementById('resultsList');
        this.downloadBtn = document.getElementById('downloadBtn');
    }

    setupFileCountDisplay() {
        if (this.imageFilesInput) {
            this.imageFilesInput.addEventListener('change', () => {
                const count = this.imageFilesInput.files.length;
                if (count > 0) {
                    this.fileCountDisplay.style.display = 'flex';
                    this.fileCountText.textContent = count === 1 ? `1 file selected` : `${count} files selected`;
                } else {
                    this.fileCountDisplay.style.display = 'none';
                }
            });
        }
    }

    showLoading() {
        this.processingLoading.classList.remove('hidden');
        this.resultsSection.classList.add('hidden');
    }

    hideLoading() {
        this.processingLoading.classList.add('hidden');
    }

    displayResults(resultItems, filename, isBatch) {
        this.resultsList.innerHTML = '';
        resultItems.forEach(item => this.resultsList.appendChild(item));

        this.downloadBtn.textContent = isBatch ? '↓ Download All Images (ZIP)' : '↓ Download Image';
        this.downloadBtn.onclick = () => downloadFile(null, filename);
        this.resultsSection.classList.remove('hidden');
    }
}

// Form Handler
class FormHandler {
    constructor(uiManager) {
        this.uiManager = uiManager;
        this.form = document.getElementById('unifiedForm');
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        const files = this.uiManager.imageFilesInput.files;

        if (!files || files.length === 0) {
            alert('Please select at least one image');
            return;
        }

        const isBatch = files.length > 1;
        const outputFormat = document.getElementById('outputFormat').value;
        const endpoint = isBatch ? '/api/batch-convert' : '/api/convert';

        const formData = this.buildFormData(files, outputFormat, isBatch);

        this.uiManager.showLoading();

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                await this.handleSuccess(response, files, isBatch, outputFormat);
            } else {
                const error = await response.json();
                alert('Error: ' + error.detail);
            }
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            this.uiManager.hideLoading();
        }
    }

    buildFormData(files, outputFormat, isBatch) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            if (isBatch) {
                formData.append('files', files[i]);
            } else {
                formData.append('file', files[i]);
            }
        }
        formData.append('output_format', outputFormat);
        return formData;
    }

    async handleSuccess(response, files, isBatch, outputFormat) {
        const fileData = JSON.parse(response.headers.get('X-File-Data'));

        if (isBatch) {
            this.displayBatchResults(fileData.results, response);
        } else {
            this.displaySingleResult(fileData, response, files[0].name, outputFormat);
        }
    }

    displayBatchResults(results, response) {
        const resultItems = results.map(result => {
            const item = document.createElement('div');
            item.className = 'text-sm p-3 rounded bg-base-100 border border-base-300';

            if (result.error) {
                item.innerHTML = `
                    <div class="flex justify-between items-center">
                        <span class="truncate font-medium">${result.filename}</span>
                        <span class="badge badge-error">Error</span>
                    </div>
                    <span class="text-xs opacity-70">${result.error}</span>
                `;
            } else {
                item.innerHTML = `
                    <div class="flex justify-between items-center">
                        <span class="truncate font-medium">${result.filename}</span>
                        <span class="badge badge-info">${result.format}</span>
                    </div>
                `;
            }
            return item;
        });

        this.uiManager.displayResults(resultItems, 'converted_images.zip', true);
        this.uiManager.downloadBtn.onclick = () => downloadFile(response, 'converted_images.zip');
    }

    displaySingleResult(fileData, response, filename, outputFormat) {
        const resultItem = document.createElement('div');
        resultItem.className = 'text-sm p-3 rounded bg-base-100 border border-base-300';
        resultItem.innerHTML = `
            <div class="flex justify-between items-center">
                <span class="font-bold">Format:</span>
                <span class="badge badge-info">${fileData.format}</span>
            </div>
            <div class="text-xs opacity-70 mt-2">Successfully converted to ${fileData.format}</div>
        `;

        const outputFilename = replaceExtension(filename, outputFormat);
        this.uiManager.displayResults([resultItem], outputFilename, false);
        this.uiManager.downloadBtn.onclick = () => downloadFile(response, outputFilename);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const uiManager = new FormUIManager();
    uiManager.setupFileCountDisplay();

    const formHandler = new FormHandler(uiManager);
    formHandler.init();
});
