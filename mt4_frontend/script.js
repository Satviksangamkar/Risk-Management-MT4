// MT4 Frontend Application
class MT4Frontend {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5501/api/v1';
        this.selectedFile = null;
        this.isAnalyzing = false;
        this.isCalculating = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkServerStatus();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // File upload elements
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');

        // Risk calculator elements
        const calculateRiskBtn = document.getElementById('calculateRiskBtn');
        const newAnalysisBtn = document.getElementById('newAnalysisBtn');
        const exportBtn = document.getElementById('exportBtn');

        // Event listeners
        uploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        analyzeBtn.addEventListener('click', () => this.analyzeFile());
        calculateRiskBtn.addEventListener('click', () => this.calculateRisk());
        newAnalysisBtn.addEventListener('click', () => this.resetAnalysis());
        exportBtn.addEventListener('click', () => this.exportResults());

        // Form validation for risk calculator
        const formInputs = ['entryPrice', 'stopLoss', 'takeProfit', 'accountBalance'];
        formInputs.forEach(id => {
            const input = document.getElementById(id);
            input.addEventListener('input', () => this.validateRiskForm());
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');

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
                this.handleFileSelect({ target: { files } });
            }
        });

        uploadArea.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
    }

    async checkServerStatus() {
        const statusElement = document.getElementById('serverStatus');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/mt4/health`);
            
            if (response.ok) {
                statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Server Online</span>';
                statusElement.className = 'status-indicator online';
            } else {
                throw new Error('Server responded with error');
            }
        } catch (error) {
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Server Offline</span>';
            statusElement.className = 'status-indicator offline';
            this.showToast('Server connection failed. Please check if the backend is running on port 5501.', 'error');
        }
    }

    handleFileSelect(event) {
        const files = event.target.files;
        const uploadArea = document.getElementById('uploadArea');
        const analyzeBtn = document.getElementById('analyzeBtn');

        if (files.length > 0) {
            const file = files[0];
            
            // Validate file type
            if (!file.name.toLowerCase().endsWith('.htm') && !file.name.toLowerCase().endsWith('.html')) {
                this.showToast('Please select an .htm or .html file', 'error');
                return;
            }

            // Validate file size (50MB limit)
            if (file.size > 50 * 1024 * 1024) {
                this.showToast('File size must be less than 50MB', 'error');
                return;
            }

            this.selectedFile = file;
            
            // Update UI
            uploadArea.classList.add('has-file');
            uploadArea.innerHTML = `
                <div class="upload-icon">
                    <i class="fas fa-file-code"></i>
                </div>
                <div class="upload-text">
                    <h3>${file.name}</h3>
                    <p>File size: ${this.formatFileSize(file.size)}</p>
                    <p class="file-info">Ready for analysis</p>
                </div>
            `;
            
            analyzeBtn.disabled = false;
            this.showToast('File selected successfully', 'success');
        }
    }

    async analyzeFile() {
        if (!this.selectedFile || this.isAnalyzing) return;

        this.isAnalyzing = true;
        this.showProgressSection();

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        const calculateRMultiple = document.getElementById('calculateRMultiple').checked;
        const includeOpenTrades = document.getElementById('includeOpenTrades').checked;

        try {
            this.updateProgress(20, 'Uploading file...');

            const response = await fetch(
                `${this.apiBaseUrl}/mt4/analyze/file-simple`,
                {
                    method: 'POST',
                    body: formData
                }
            );

            this.updateProgress(60, 'Processing MT4 statement...');

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const data = await response.json();
            
            this.updateProgress(90, 'Generating results...');
            
            setTimeout(() => {
                this.updateProgress(100, 'Analysis complete!');
                this.displayResults(data);
                this.hideProgressSection();
                this.showToast('Analysis completed successfully!', 'success');
            }, 500);

        } catch (error) {
            console.error('Analysis error:', error);
            this.hideProgressSection();
            this.showToast(`Analysis failed: ${error.message}`, 'error');
        } finally {
            this.isAnalyzing = false;
        }
    }

    async calculateRisk() {
        if (this.isCalculating) return;

        const entryPrice = parseFloat(document.getElementById('entryPrice').value);
        const stopLoss = parseFloat(document.getElementById('stopLoss').value);
        const takeProfit = parseFloat(document.getElementById('takeProfit').value);
        const tradeType = document.getElementById('tradeType').value;
        const accountBalance = parseFloat(document.getElementById('accountBalance').value) || 0;
        const riskPercentage = parseFloat(document.getElementById('riskPercentage').value) || 2;
        const positionSize = parseFloat(document.getElementById('positionSize').value) || null;

        if (!entryPrice || !stopLoss || !takeProfit) {
            this.showToast('Please fill in Entry Price, Stop Loss, and Take Profit', 'warning');
            return;
        }

        this.isCalculating = true;
        this.showLoadingOverlay();

        const requestData = {
            entry_price: entryPrice,
            stop_loss: stopLoss,
            take_profit: takeProfit,
            trade_type: tradeType.toLowerCase(), // Ensure lowercase for API
            account_balance: accountBalance,
            risk_percentage: riskPercentage,
            position_size: positionSize
        };

        try {
            const response = await fetch(`${this.apiBaseUrl}/mt4/risk-calculator`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Risk calculation failed');
            }

            const data = await response.json();
            this.displayRiskResults(data.data);
            this.showToast('Risk calculation completed!', 'success');

        } catch (error) {
            console.error('Risk calculation error:', error);
            this.showToast(`Risk calculation failed: ${error.message}`, 'error');
        } finally {
            this.isCalculating = false;
            this.hideLoadingOverlay();
        }
    }

    displayResults(response) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsGrid = document.getElementById('resultsGrid');
        
        resultsGrid.innerHTML = '';

        // Extract data from response
        const data = response.data || response;

        // Account Information
        if (data.account_info) {
            const accountCard = this.createResultCard('Account Information', 'fas fa-user', [
                { label: 'Account Name', value: data.account_info.account_name || 'N/A' },
                { label: 'Account Number', value: data.account_info.account_number || 'N/A' },
                { label: 'Currency', value: data.account_info.currency || 'N/A' },
                { label: 'Leverage', value: data.account_info.leverage || 'N/A' },
                { label: 'Report Date', value: data.account_info.report_date || 'N/A' }
            ]);
            resultsGrid.appendChild(accountCard);
        }

        // Trading Summary from trade_statistics
        if (data.trade_statistics) {
            const summaryCard = this.createResultCard('Trading Summary', 'fas fa-chart-bar', [
                { label: 'Total Trades', value: data.trade_statistics.total_trades || 0 },
                { label: 'Profitable Trades', value: data.trade_statistics.profit_trades_count || 0 },
                { label: 'Loss Trades', value: data.trade_statistics.loss_trades_count || 0 },
                { label: 'Win Rate', value: data.trade_statistics.profit_trades_percentage ? `${data.trade_statistics.profit_trades_percentage.toFixed(2)}%` : 'N/A' },
                { label: 'Long Positions', value: data.trade_statistics.long_positions_count || 0 },
                { label: 'Short Positions', value: data.trade_statistics.short_positions_count || 0 }
            ]);
            resultsGrid.appendChild(summaryCard);
        }

        // Financial Summary
        if (data.financial_summary) {
            const financialCard = this.createResultCard('Financial Summary', 'fas fa-dollar-sign', [
                { label: 'Balance', value: this.formatCurrency(data.financial_summary.balance) || 'N/A' },
                { label: 'Equity', value: this.formatCurrency(data.financial_summary.equity) || 'N/A' },
                { label: 'Closed Trade P/L', value: this.formatCurrency(data.financial_summary.closed_trade_pnl) || 'N/A', className: this.getProfitClass(data.financial_summary.closed_trade_pnl) },
                { label: 'Floating P/L', value: this.formatCurrency(data.financial_summary.floating_pnl) || 'N/A', className: this.getProfitClass(data.financial_summary.floating_pnl) },
                { label: 'Free Margin', value: this.formatCurrency(data.financial_summary.free_margin) || 'N/A' }
            ]);
            resultsGrid.appendChild(financialCard);
        }

        // Performance Metrics from calculated_metrics
        if (data.calculated_metrics) {
            const performanceCard = this.createResultCard('Performance Metrics', 'fas fa-trophy', [
                { label: 'Total Net Profit', value: this.formatCurrency(data.calculated_metrics.total_net_profit) || 'N/A', className: this.getProfitClass(data.calculated_metrics.total_net_profit) },
                { label: 'Profit Factor', value: data.calculated_metrics.profit_factor?.toFixed(2) || 'N/A' },
                { label: 'Win Rate', value: data.calculated_metrics.win_rate ? `${data.calculated_metrics.win_rate.toFixed(2)}%` : 'N/A' },
                { label: 'Expected Payoff', value: this.formatCurrency(data.calculated_metrics.expected_payoff) || 'N/A' },
                { label: 'Max Drawdown', value: data.calculated_metrics.maximum_drawdown_percentage ? `${data.calculated_metrics.maximum_drawdown_percentage.toFixed(2)}%` : 'N/A', className: 'negative' },
                { label: 'Recovery Factor', value: data.calculated_metrics.recovery_factor?.toFixed(2) || 'N/A' }
            ]);
            resultsGrid.appendChild(performanceCard);
        }

        // Risk Analysis from calculated_metrics
        if (data.calculated_metrics) {
            const riskCard = this.createResultCard('Risk Analysis', 'fas fa-shield-alt', [
                { label: 'Risk/Reward Ratio', value: data.calculated_metrics.risk_reward_ratio?.toFixed(2) || 'N/A' },
                { label: 'Kelly Percentage', value: data.calculated_metrics.kelly_percentage ? `${data.calculated_metrics.kelly_percentage.toFixed(2)}%` : 'N/A' },
                { label: 'Standard Deviation', value: data.calculated_metrics.standard_deviation?.toFixed(4) || 'N/A' },
                { label: 'Skewness', value: data.calculated_metrics.skewness?.toFixed(4) || 'N/A' },
                { label: 'Kurtosis', value: data.calculated_metrics.kurtosis?.toFixed(4) || 'N/A' }
            ]);
            resultsGrid.appendChild(riskCard);
        }

        // R-Multiple Analysis (if available)
        if (data.r_multiple_statistics) {
            const rMultipleCard = this.createResultCard('R-Multiple Analysis', 'fas fa-calculator', [
                { label: 'Valid R-Trades', value: data.r_multiple_statistics.total_valid_r_trades || 'N/A' },
                { label: 'R Win Rate', value: data.r_multiple_statistics.r_win_rate ? `${data.r_multiple_statistics.r_win_rate.toFixed(2)}%` : 'N/A' },
                { label: 'Average R-Multiple', value: data.r_multiple_statistics.average_r_multiple?.toFixed(2) || 'N/A' },
                { label: 'Best R-Multiple', value: data.r_multiple_statistics.best_r_multiple?.toFixed(2) || 'N/A' },
                { label: 'Worst R-Multiple', value: data.r_multiple_statistics.worst_r_multiple?.toFixed(2) || 'N/A' },
                { label: 'R Expectancy', value: data.r_multiple_statistics.r_expectancy?.toFixed(4) || 'N/A' }
            ]);
            resultsGrid.appendChild(rMultipleCard);
        }

        // Enhanced R-Multiple Analysis
        if (data.r_multiple_statistics) {
            const enhancedRCard = this.createResultCard('Enhanced R-Multiple Matrix', 'fas fa-chart-line', [
                { label: 'Valid R-Trades', value: data.r_multiple_statistics.total_valid_r_trades || 'N/A' },
                { label: 'Winning R-Trades', value: data.r_multiple_statistics.winning_r_trades || 'N/A' },
                { label: 'Losing R-Trades', value: data.r_multiple_statistics.losing_r_trades || 'N/A' },
                { label: 'R Win Rate', value: data.r_multiple_statistics.r_win_rate ? `${data.r_multiple_statistics.r_win_rate.toFixed(2)}%` : 'N/A' },
                { label: 'Average R-Multiple', value: data.r_multiple_statistics.average_r_multiple?.toFixed(3) || 'N/A' },
                { label: 'Average Winning R', value: data.r_multiple_statistics.average_winning_r?.toFixed(3) || 'N/A', className: 'positive' },
                { label: 'Average Losing R', value: data.r_multiple_statistics.average_losing_r?.toFixed(3) || 'N/A', className: 'negative' },
                { label: 'Best R-Multiple', value: data.r_multiple_statistics.best_r_multiple?.toFixed(3) || 'N/A', className: 'positive' },
                { label: 'Worst R-Multiple', value: data.r_multiple_statistics.worst_r_multiple?.toFixed(3) || 'N/A', className: 'negative' },
                { label: 'R Expectancy', value: data.r_multiple_statistics.r_expectancy?.toFixed(4) || 'N/A' }
            ]);
            resultsGrid.appendChild(enhancedRCard);
        }

        // Individual Trade Analysis (R-Multiple Details)
        if (data.closed_trades && data.closed_trades.length > 0) {
            const tradesCard = this.createTradeDetailsCard('Individual Trade Analysis', data.closed_trades);
            resultsGrid.appendChild(tradesCard);
        }

        // Open Trades Info (if available)
        if (data.open_trades && data.open_trades.length > 0) {
            const openTradesCard = this.createResultCard('Open Trades', 'fas fa-clock', [
                { label: 'Open Trades Count', value: data.open_trades.length },
                { label: 'Total Open Size', value: data.open_trades.reduce((sum, trade) => sum + trade.size, 0).toFixed(2) },
                { label: 'Open Trades P/L', value: this.formatCurrency(data.open_trades.reduce((sum, trade) => sum + trade.profit, 0)), className: this.getProfitClass(data.open_trades.reduce((sum, trade) => sum + trade.profit, 0)) }
            ]);
            resultsGrid.appendChild(openTradesCard);
        }

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    displayRiskResults(data) {
        const riskResults = document.getElementById('riskResults');
        riskResults.innerHTML = '';

        // Trade Setup
        const setupCard = this.createRiskCard('Trade Setup', [
            { label: 'Entry Price', value: data.trade_setup.entry_price },
            { label: 'Stop Loss', value: data.trade_setup.stop_loss },
            { label: 'Take Profit', value: data.trade_setup.take_profit },
            { label: 'Trade Type', value: data.trade_setup.trade_type },
            { label: 'Valid Setup', value: data.trade_setup.is_valid_setup ? 'Yes' : 'No' }
        ]);
        riskResults.appendChild(setupCard);

        // Risk Metrics
        const riskCard = this.createRiskCard('Risk Metrics', [
            { label: 'Risk per Share', value: data.risk_metrics.risk_per_share?.toFixed(5) || 'N/A' },
            { label: 'Reward per Share', value: data.risk_metrics.reward_per_share?.toFixed(5) || 'N/A' },
            { label: 'Total Risk', value: this.formatCurrency(data.risk_metrics.total_risk) },
            { label: 'Total Reward', value: this.formatCurrency(data.risk_metrics.total_reward) },
            { label: 'R-Multiple', value: data.risk_metrics.r_multiple?.toFixed(2) || 'N/A' },
            { label: 'Risk/Reward Ratio', value: data.risk_metrics.risk_reward_ratio || 'N/A' },
            { label: 'Required Win Rate', value: data.risk_metrics.required_win_rate ? `${data.risk_metrics.required_win_rate.toFixed(2)}%` : 'N/A' }
        ]);
        riskResults.appendChild(riskCard);

        // Position Analysis
        const positionCard = this.createRiskCard('Position Analysis', [
            { label: 'Position Size', value: data.position_analysis.position_size || 'N/A' },
            { label: 'Optimal Position Size', value: data.position_analysis.optimal_position_size?.toFixed(2) || 'N/A' },
            { label: 'Max Position Size', value: data.position_analysis.max_position_size?.toFixed(2) || 'N/A' },
            { label: 'Position Value', value: this.formatCurrency(data.position_analysis.position_value) },
            { label: 'Risk Level', value: data.position_analysis.risk_level || 'N/A' }
        ]);
        riskResults.appendChild(positionCard);

        // Account Analysis
        const accountCard = this.createRiskCard('Account Analysis', [
            { label: 'Account Balance', value: this.formatCurrency(data.account_analysis.account_balance) },
            { label: 'Risk Percentage', value: `${data.account_analysis.risk_percentage}%` },
            { label: 'Recommendations', value: data.account_analysis.recommendations?.join(', ') || 'None' }
        ]);
        riskResults.appendChild(accountCard);

        riskResults.style.display = 'grid';
    }

    createResultCard(title, icon, metrics) {
        const card = document.createElement('div');
        card.className = 'result-card fade-in';
        
        let metricsHtml = metrics.map(metric => `
            <div class="metric-row">
                <span class="metric-label">${metric.label}</span>
                <span class="metric-value ${metric.className || ''}">${metric.value}</span>
            </div>
        `).join('');

        card.innerHTML = `
            <h3><i class="${icon}"></i> ${title}</h3>
            ${metricsHtml}
        `;

        return card;
    }

    createRiskCard(title, metrics) {
        const card = document.createElement('div');
        card.className = 'risk-card fade-in';
        
        let metricsHtml = metrics.map(metric => `
            <div class="metric-row">
                <span class="metric-label">${metric.label}</span>
                <span class="metric-value">${metric.value}</span>
            </div>
        `).join('');

        card.innerHTML = `
            <h4>${title}</h4>
            ${metricsHtml}
        `;

        return card;
    }

    createTradeDetailsCard(title, trades) {
        const card = document.createElement('div');
        card.className = 'result-card trade-details-card fade-in';
        
        // Create table for trade details
        let tableHtml = `
            <div class="trade-table-container">
                <table class="trade-table">
                    <thead>
                        <tr>
                            <th>Ticket</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Entry</th>
                            <th>SL</th>
                            <th>TP</th>
                            <th>Profit</th>
                            <th>Risk/R</th>
                            <th>R-Multiple</th>
                            <th>Theoretical R</th>
                            <th>Risk Amount</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        trades.forEach(trade => {
            const rMultipleClass = trade.r_multiple > 0 ? 'positive' : trade.r_multiple < 0 ? 'negative' : 'neutral';
            const profitClass = trade.profit > 0 ? 'positive' : trade.profit < 0 ? 'negative' : 'neutral';
            const riskSetup = trade.is_valid_r_setup ? '✓' : '✗';
            const riskSetupClass = trade.is_valid_r_setup ? 'positive' : 'neutral';
            
            tableHtml += `
                <tr class="trade-row">
                    <td class="trade-ticket">${trade.ticket || 'N/A'}</td>
                    <td class="trade-type ${trade.type}">${(trade.type || 'N/A').toUpperCase()}</td>
                    <td class="trade-size">${trade.size?.toFixed(2) || 'N/A'}</td>
                    <td class="trade-entry">${trade.entry_price?.toFixed(5) || 'N/A'}</td>
                    <td class="trade-sl">${trade.stop_loss?.toFixed(5) || 'N/A'}</td>
                    <td class="trade-tp">${trade.take_profit?.toFixed(5) || 'N/A'}</td>
                    <td class="trade-profit ${profitClass}">${this.formatCurrency(trade.profit) || 'N/A'}</td>
                    <td class="trade-risk-setup ${riskSetupClass}">${riskSetup}</td>
                    <td class="trade-r-multiple ${rMultipleClass}">${trade.r_multiple?.toFixed(3) || 'N/A'}</td>
                    <td class="trade-theoretical-r">${trade.theoretical_r_multiple?.toFixed(3) || 'N/A'}</td>
                    <td class="trade-risk-amount">${this.formatCurrency(trade.risk_amount) || 'N/A'}</td>
                </tr>
            `;
        });
        
        tableHtml += `
                    </tbody>
                </table>
            </div>
        `;
        
        // Add summary statistics
        const validRTrades = trades.filter(t => t.is_valid_r_setup && t.r_multiple !== 0);
        const avgR = validRTrades.length > 0 ? validRTrades.reduce((sum, t) => sum + t.r_multiple, 0) / validRTrades.length : 0;
        const bestR = validRTrades.length > 0 ? Math.max(...validRTrades.map(t => t.r_multiple)) : 0;
        const worstR = validRTrades.length > 0 ? Math.min(...validRTrades.map(t => t.r_multiple)) : 0;
        
        const summaryHtml = `
            <div class="trade-summary">
                <div class="summary-stats">
                    <div class="stat-item">
                        <span class="stat-label">Valid R-Setups:</span>
                        <span class="stat-value">${validRTrades.length}/${trades.length}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Average R:</span>
                        <span class="stat-value ${avgR > 0 ? 'positive' : avgR < 0 ? 'negative' : 'neutral'}">${avgR.toFixed(3)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Best R:</span>
                        <span class="stat-value positive">${bestR.toFixed(3)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Worst R:</span>
                        <span class="stat-value negative">${worstR.toFixed(3)}</span>
                    </div>
                </div>
            </div>
        `;

        card.innerHTML = `
            <h3><i class="fas fa-table"></i> ${title}</h3>
            ${summaryHtml}
            ${tableHtml}
        `;

        return card;
    }

    showProgressSection() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'block';
        progressSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideProgressSection() {
        const progressSection = document.getElementById('progressSection');
        setTimeout(() => {
            progressSection.style.display = 'none';
        }, 1000);
    }

    updateProgress(percent, message) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progressFill.style.width = `${percent}%`;
        progressText.textContent = message;
    }

    showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'flex';
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
    }

    resetAnalysis() {
        // Reset file upload
        this.selectedFile = null;
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const analyzeBtn = document.getElementById('analyzeBtn');

        fileInput.value = '';
        uploadArea.classList.remove('has-file');
        uploadArea.innerHTML = `
            <div class="upload-icon">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <div class="upload-text">
                <h3>Drag & Drop your MT4 file here</h3>
                <p>or <button class="upload-btn" id="uploadBtn">Browse Files</button></p>
                <p class="file-info">Supports .htm and .html files up to 50MB</p>
            </div>
        `;
        analyzeBtn.disabled = true;

        // Re-setup upload button event listener
        const newUploadBtn = document.getElementById('uploadBtn');
        newUploadBtn.addEventListener('click', () => fileInput.click());

        // Hide results
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'none';

        this.showToast('Ready for new analysis', 'success');
    }

    exportResults() {
        const resultsGrid = document.getElementById('resultsGrid');
        if (!resultsGrid.children.length) {
            this.showToast('No results to export', 'warning');
            return;
        }

        // Simple text export
        let exportText = 'MT4 Analysis Results\n';
        exportText += '===================\n\n';

        Array.from(resultsGrid.children).forEach(card => {
            const title = card.querySelector('h3').textContent;
            exportText += `${title}\n`;
            exportText += '-'.repeat(title.length) + '\n';

            const metrics = card.querySelectorAll('.metric-row');
            metrics.forEach(metric => {
                const label = metric.querySelector('.metric-label').textContent;
                const value = metric.querySelector('.metric-value').textContent;
                exportText += `${label}: ${value}\n`;
            });
            exportText += '\n';
        });

        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mt4-analysis-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Results exported successfully', 'success');
    }

    validateRiskForm() {
        const calculateBtn = document.getElementById('calculateRiskBtn');
        const entryPrice = document.getElementById('entryPrice').value;
        const stopLoss = document.getElementById('stopLoss').value;
        const takeProfit = document.getElementById('takeProfit').value;

        calculateBtn.disabled = !entryPrice || !stopLoss || !takeProfit;
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <i class="toast-icon ${iconMap[type]}"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        toastContainer.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatCurrency(value) {
        if (value === null || value === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(value);
    }

    getProfitClass(value) {
        if (value === null || value === undefined) return '';
        return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MT4Frontend();
});

// Add some utility functions for better UX
window.addEventListener('beforeunload', (e) => {
    const mt4App = window.mt4App;
    if (mt4App && (mt4App.isAnalyzing || mt4App.isCalculating)) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    document.querySelector('.mt4-frontend')?.checkServerStatus();
});

window.addEventListener('offline', () => {
    const statusElement = document.getElementById('serverStatus');
    if (statusElement) {
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Offline</span>';
        statusElement.className = 'status-indicator offline';
    }
});
