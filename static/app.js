// Smart CSV Cleaner - Frontend JavaScript
document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');
    const uploadSection = document.getElementById('upload-section');
    const analysisSection = document.getElementById('analysis-section');
    const optionsSection = document.getElementById('options-section');
    const resultsSection = document.getElementById('results-section');
    const feedbackContainer = document.getElementById('feedback-container');
    const uploadLoading = document.getElementById('upload-loading');
    const cleanLoading = document.getElementById('clean-loading');
    const cleanBtn = document.getElementById('clean-btn');
    const toggleAdvancedBtn = document.getElementById('toggle-advanced');
    const advancedOptions = document.getElementById('advanced-options');

    let currentFilename = null;

    // --- Initial State ---
    const setInitialState = () => {
        analysisSection.classList.add('hidden');
        optionsSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        uploadArea.style.display = 'block';
        uploadLoading.style.display = 'none';
        feedbackContainer.innerHTML = '';
    };

    // --- Core Functions ---
    const showFeedback = (message, isError = false) => {
        feedbackContainer.innerHTML = `
            <div class="fade-in p-4 rounded-md ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}">
                ${message}
            </div>
        `;
        setTimeout(() => feedbackContainer.innerHTML = '', 5000);
    };

    const handleFileUpload = async (file) => {
        if (!file || !file.type.match('text/csv')) {
            showFeedback('Please select a valid CSV file.', true);
            return;
        }

        uploadLoading.style.display = 'block';
        uploadArea.style.display = 'none';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Upload failed');
            }
            
            showFeedback(result.message || `Successfully uploaded ${file.name}`);
            currentFilename = result.data.filename;
            displayAnalysis(result.data);
            
            uploadSection.classList.add('hidden');
            analysisSection.classList.remove('hidden');
            optionsSection.classList.remove('hidden');

        } catch (error) {
            showFeedback(`Error: ${error.message}`, true);
            setInitialState(); // Reset on error
        } finally {
            uploadLoading.style.display = 'none';
        }
    };

    const displayAnalysis = (data) => {
        const statsContainer = document.getElementById('data-stats');
        statsContainer.innerHTML = `
            <div class="bg-purple-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-purple-800">Filename</p><p class="text-xl font-bold truncate" title="${data.filename}">${data.filename}</p></div>
            <div class="bg-blue-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-blue-800">Rows</p><p class="text-xl font-bold">${data.rows.toLocaleString()}</p></div>
            <div class="bg-yellow-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-yellow-800">Columns</p><p class="text-xl font-bold">${data.columns}</p></div>
            <div class="bg-red-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-red-800">Missing Values</p><p class="text-xl font-bold">${data.missing_values.toLocaleString()}</p></div>
        `;

        const previewHeader = document.getElementById('preview-header');
        const previewBody = document.getElementById('preview-body');
        previewHeader.innerHTML = '<tr>' + data.column_names.map(name => `<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">${name}</th>`).join('') + '</tr>';
        previewBody.innerHTML = data.preview.map(row => 
            '<tr>' + data.column_names.map(col => `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${row[col] === null || row[col] === undefined ? '' : row[col]}</td>`).join('') + '</tr>'
        ).join('');
    };

    const cleanData = async () => {
        if (!currentFilename) {
            showFeedback('No file selected for cleaning.', true);
            return;
        }

        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        cleanLoading.style.display = 'block';
        document.getElementById('results-content').style.display = 'none';

        const findValue = document.getElementById('find-value').value;
        const replaceValue = document.getElementById('replace-value').value;

        const requestData = {
            filename: currentFilename,
            natural_command: document.getElementById('natural-command').value,
            fix_names: document.getElementById('fix-names').checked,
            standardize_types: document.getElementById('standardize-types').checked,
            excel: document.getElementById('excel-export').checked,
            fix_missing: document.getElementById('fix-missing').value,
            drop_outliers: document.getElementById('drop-outliers').value,
            remove_duplicates: document.getElementById('remove-duplicates').checked,
            trim_whitespace: document.getElementById('trim-whitespace').checked,
            change_case: document.getElementById('change-case').value,
            find_replace: findValue ? { find: findValue, replace: replaceValue } : null,
            drop_columns: document.getElementById('drop-columns').value
        };

        try {
            const response = await fetch('/api/clean', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Cleaning process failed.');
            }
            displayResults(result);

        } catch (error) {
            showFeedback(`Cleaning Error: ${error.message}`, true);
            resultsSection.classList.add('hidden');
        } finally {
            cleanLoading.style.display = 'none';
            document.getElementById('results-content').style.display = 'block';
        }
    };
    
    const displayResults = (data) => {
        // Display final stats
        const finalStatsContainer = document.getElementById('final-stats-container');
        if (data.final_stats) {
            finalStatsContainer.innerHTML = `
                <h3 class="text-2xl font-bold text-gray-800 mb-4">Final File Analysis</h3>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div class="bg-purple-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-purple-800">Filename</p><p class="text-xl font-bold truncate" title="${data.output_filename}">${data.output_filename}</p></div>
                    <div class="bg-blue-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-blue-800">Rows</p><p class="text-xl font-bold">${data.final_stats.rows.toLocaleString()}</p></div>
                    <div class="bg-yellow-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-yellow-800">Columns</p><p class="text-xl font-bold">${data.final_stats.columns}</p></div>
                    <div class="bg-red-100 p-4 rounded-lg text-center"><p class="text-sm font-medium text-red-800">Missing Values</p><p class="text-xl font-bold">${data.final_stats.missing_values.toLocaleString()}</p></div>
                </div>
            `;
            finalStatsContainer.classList.remove('hidden');
        } else {
            finalStatsContainer.classList.add('hidden');
        }

        const summaryContainer = document.getElementById('summary-section');
        const transformationsList = data.transformations.map(t => `<li class="flex items-center"><i class="fas fa-check-circle text-green-500 mr-2"></i>${t}</li>`).join('');
        summaryContainer.innerHTML = `
            <div class="bg-indigo-50 p-4 rounded-lg">
                <h4 class="font-bold text-lg text-indigo-800">Cleaning Summary</h4>
                <p class="text-gray-600 mb-2">Cleaned file: <strong>${data.output_filename}</strong></p>
                <ul class="space-y-1">${transformationsList || '<li>No transformations were applied.</li>'}</ul>
            </div>
        `;

        const resultsHeader = document.getElementById('results-header');
        const resultsBody = document.getElementById('results-body');
        resultsHeader.innerHTML = '<tr>' + data.preview.columns.map(name => `<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">${name}</th>`).join('') + '</tr>';
        resultsBody.innerHTML = data.preview.data.map(row => 
            '<tr>' + data.preview.columns.map(col => `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${row[col] === null || row[col] === undefined ? '' : row[col]}</td>`).join('') + '</tr>'
        ).join('');
        
        const downloadContainer = document.getElementById('download-buttons');
        let buttonsHTML = `<a href="/api/download/${data.output_filename}" class="inline-block bg-green-600 text-white font-bold py-2 px-6 rounded-lg hover:bg-green-700 transition-all shadow-md">
            <i class="fas fa-download mr-2"></i>Download CSV
        </a>`;
        if (data.excel_filename) {
            buttonsHTML += `<a href="/api/download/${data.excel_filename}" class="ml-4 inline-block bg-blue-600 text-white font-bold py-2 px-6 rounded-lg hover:bg-blue-700 transition-all shadow-md">
                <i class="fas fa-file-excel mr-2"></i>Download Excel
            </a>`;
    }
        downloadContainer.innerHTML = buttonsHTML;
    };

    const setupDragAndDrop = () => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, e => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.add('border-indigo-500', 'bg-indigo-50'));
        });
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('border-indigo-500', 'bg-indigo-50'));
        });
        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileUpload(files[0]);
            }
        });
    };
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
            }
    });

    cleanBtn.addEventListener('click', cleanData);

    toggleAdvancedBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const isHidden = advancedOptions.classList.toggle('hidden');
        if(isHidden) {
            toggleAdvancedBtn.innerHTML = '<i class="fas fa-cog mr-1"></i>Toggle Advanced Options';
        } else {
            toggleAdvancedBtn.innerHTML = '<i class="fas fa-cog mr-1"></i>Hide Advanced Options';
            }
    });
    
    setupDragAndDrop();
    setInitialState();
});