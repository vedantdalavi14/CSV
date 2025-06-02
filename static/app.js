// Smart CSV Cleaner - Frontend JavaScript
class CSVCleaner {
    constructor() {
        this.currentFile = null;
        this.fileData = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File upload handlers
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');

        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop handlers
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFile(files[0]);
            }
        });

        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // Clean button handler
        document.getElementById('clean-btn').addEventListener('click', () => this.cleanData());

        // Natural language command input
        document.getElementById('natural-command').addEventListener('input', (e) => {
            this.parseNaturalCommand(e.target.value);
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showError('Please select a CSV file.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        this.showLoading('upload-loading');
        this.hideSection('analysis-section');
        this.hideSection('options-section');
        this.hideSection('results-section');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentFile = result.data.filename;
                this.fileData = result.data;
                this.displayDataAnalysis(result.data);
                this.showSection('analysis-section');
                this.showSection('options-section');
                this.showSuccess(result.message);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to upload file: ' + error.message);
        } finally {
            this.hideLoading('upload-loading');
        }
    }

    displayDataAnalysis(data) {
        // Display statistics
        const statsContainer = document.getElementById('data-stats');
        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${data.rows}</div>
                <div class="text-muted">Rows</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${data.columns}</div>
                <div class="text-muted">Columns</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${Object.values(data.missing_data).reduce((sum, val) => sum + val, 0)}</div>
                <div class="text-muted">Missing Values</div>
            </div>
        `;

        // Display preview table
        this.displayTable(data.preview, data.column_names, 'preview-header', 'preview-body');

        // Show missing data details if any
        const missingCount = Object.values(data.missing_data).reduce((sum, val) => sum + val, 0);
        if (missingCount > 0) {
            const missingInfo = Object.entries(data.missing_data)
                .filter(([col, count]) => count > 0)
                .map(([col, count]) => `${col}: ${count}`)
                .join(', ');
            
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-warning mt-3';
            alertDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i><strong>Missing Data Found:</strong> ${missingInfo}`;
            document.getElementById('analysis-section').querySelector('.card-body').appendChild(alertDiv);
        }
    }

    displayTable(data, columns, headerId, bodyId) {
        const header = document.getElementById(headerId);
        const body = document.getElementById(bodyId);

        // Clear existing content
        header.innerHTML = '';
        body.innerHTML = '';

        if (data.length === 0) {
            body.innerHTML = '<tr><td colspan="100%" class="text-center text-muted">No data to display</td></tr>';
            return;
        }

        // Create header
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            headerRow.appendChild(th);
        });
        header.appendChild(headerRow);

        // Create body rows
        data.slice(0, 10).forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                const value = row[col];
                td.textContent = value !== null && value !== undefined ? value : 'null';
                if (value === null || value === undefined || value === '') {
                    td.classList.add('text-muted');
                    td.style.fontStyle = 'italic';
                }
                tr.appendChild(td);
            });
            body.appendChild(tr);
        });

        // Add "more rows" indicator if needed
        if (data.length > 10) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = columns.length;
            td.className = 'text-center text-muted';
            td.innerHTML = `<i class="fas fa-ellipsis-h me-2"></i>... and ${data.length - 10} more rows`;
            tr.appendChild(td);
            body.appendChild(tr);
        }
    }

    async parseNaturalCommand(command) {
        if (!command.trim()) return;

        try {
            const response = await fetch('/api/parse-command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });

            const result = await response.json();

            if (result.success) {
                this.updateFormFromParsedFlags(result.parsed_flags);
            }
        } catch (error) {
            console.error('Failed to parse command:', error);
        }
    }

    updateFormFromParsedFlags(flags) {
        // Update form controls based on parsed flags
        document.getElementById('fix-names').checked = flags.fix_names || false;
        document.getElementById('standardize-types').checked = flags.standardize_types || false;
        
        if (flags.fix_missing) {
            document.getElementById('fix-missing').value = flags.fix_missing;
        }
        
        if (flags.drop_outliers) {
            document.getElementById('drop-outliers').value = flags.drop_outliers;
        }
    }

    async cleanData() {
        if (!this.currentFile) {
            this.showError('No file uploaded');
            return;
        }

        const naturalCommand = document.getElementById('natural-command').value;
        const fixNames = document.getElementById('fix-names').checked;
        const fixMissing = document.getElementById('fix-missing').value || null;
        const dropOutliers = document.getElementById('drop-outliers').value || null;
        const standardizeTypes = document.getElementById('standardize-types').checked;
        const excelExport = document.getElementById('excel-export').checked;
        const zscoreThreshold = parseFloat(document.getElementById('zscore-threshold').value);

        const requestData = {
            filename: this.currentFile,
            natural_command: naturalCommand,
            fix_names: fixNames,
            fix_missing: fixMissing,
            drop_outliers: dropOutliers,
            standardize_types: standardizeTypes,
            excel_export: excelExport,
            zscore_threshold: zscoreThreshold
        };

        this.showSection('results-section');
        this.showLoading('clean-loading');
        this.hideElement('results-content');

        try {
            const response = await fetch('/api/clean', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                this.displayResults(result);
                this.showElement('results-content');
                this.showSuccess('Data cleaning completed successfully!');
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to clean data: ' + error.message);
        } finally {
            this.hideLoading('clean-loading');
        }
    }

    displayResults(result) {
        // Display success message
        document.getElementById('success-message').innerHTML = 
            `<i class="fas fa-check-circle me-2"></i>${result.message}`;

        // Display result statistics
        const cleanedData = result.cleaned_data;
        const originalRows = this.fileData.rows;
        const cleanedRows = cleanedData.rows;
        const rowsChanged = originalRows - cleanedRows;

        const statsContainer = document.getElementById('results-stats');
        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${cleanedRows}</div>
                <div class="text-muted">Final Rows</div>
                ${rowsChanged > 0 ? `<small class="text-warning">(-${rowsChanged})</small>` : ''}
            </div>
            <div class="stat-card">
                <div class="stat-number">${cleanedData.columns}</div>
                <div class="text-muted">Columns</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${Object.values(cleanedData.preview).length}</div>
                <div class="text-muted">Preview Rows</div>
            </div>
        `;

        // Display cleaned data preview
        this.displayTable(cleanedData.preview, cleanedData.column_names, 'results-header', 'results-body');

        // Create download buttons
        const downloadContainer = document.getElementById('download-buttons');
        downloadContainer.innerHTML = `
            <a href="/api/download/${result.output_filename}" class="btn btn-primary btn-lg me-3" download>
                <i class="fas fa-download me-2"></i>Download CSV
            </a>
            ${result.excel_filename ? 
                `<a href="/api/download/${result.excel_filename}" class="btn btn-success btn-lg" download>
                    <i class="fas fa-file-excel me-2"></i>Download Excel
                </a>` : ''
            }
        `;
    }

    showSection(sectionId) {
        const section = document.getElementById(sectionId);
        section.classList.remove('hidden');
        section.classList.add('fade-in');
    }

    hideSection(sectionId) {
        document.getElementById(sectionId).classList.add('hidden');
    }

    showElement(elementId) {
        document.getElementById(elementId).classList.remove('hidden');
    }

    hideElement(elementId) {
        document.getElementById(elementId).classList.add('hidden');
    }

    showLoading(loadingId) {
        document.getElementById(loadingId).style.display = 'block';
    }

    hideLoading(loadingId) {
        document.getElementById(loadingId).style.display = 'none';
    }

    showError(message) {
        // Remove existing alerts
        document.querySelectorAll('.alert-danger').forEach(alert => alert.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of content
        const content = document.querySelector('.content');
        content.insertBefore(alertDiv, content.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    showSuccess(message) {
        // Remove existing success alerts
        document.querySelectorAll('.alert-success').forEach(alert => {
            if (!alert.id) alert.remove();
        });

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of content
        const content = document.querySelector('.content');
        content.insertBefore(alertDiv, content.firstChild);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new CSVCleaner();
});