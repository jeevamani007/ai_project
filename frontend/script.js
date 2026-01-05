function formatResults(data) {
  let html = '<div class="results-container">';
  
  // Summary Section
  if (data.summary) {
    html += `<div class="section summary-section">
      <h3>📊 Analysis Summary</h3>`;
    
    if (data.summary.small_dataset_warning) {
      html += `<div class="warning-box">
        <strong>⚠️ Warning:</strong> Small dataset detected (${data.summary.total_rows} rows). Statistical reliability may be limited.
      </div>`;
    }
    
    html += `<div class="summary-grid">
        <div class="summary-item">
          <span class="label">Domain Detected:</span>
          <span class="value domain-badge">${data.summary.domain_detected}</span>
          <span class="confidence-badge ${data.summary.domain_confidence?.toLowerCase() || 'medium'}">${data.summary.domain_confidence || 'Medium'} Confidence</span>
        </div>
        <div class="summary-item">
          <span class="label">Total Rows:</span>
          <span class="value">${data.summary.total_rows}</span>
        </div>
        <div class="summary-item">
          <span class="label">Total Columns:</span>
          <span class="value">${data.summary.total_columns}</span>
        </div>
        <div class="summary-item">
          <span class="label">Total Business Rules:</span>
          <span class="value">${data.summary.total_business_rules}</span>
        </div>
        <div class="summary-item">
          <span class="label">Rules Requiring Approval:</span>
          <span class="value approval-needed">${data.summary.rules_requiring_approval}</span>
        </div>
      </div>`;
    
    if (data.summary.domain_description) {
      html += `<p class="domain-description"><strong>Domain:</strong> ${data.summary.domain_description}</p>`;
    }
    
    if (data.summary.domain_reasoning && data.summary.domain_reasoning.length > 0) {
      html += `<div class="reasoning-box">
        <strong>Domain Detection Reasoning:</strong>
        <ul>`;
      data.summary.domain_reasoning.forEach(reason => {
        html += `<li>${reason}</li>`;
      });
      html += `</ul></div>`;
    }
    
    html += `</div>`;
  }
  
  // Strict Mode Information
  if (data.strict_mode && data.strict_mode.enabled) {
    html += `<div class="section strict-mode-section">
      <h3>🔒 Strict Mode Active</h3>
      <p class="section-note">Only policy-valid business rules are extracted. Statistical correlations and data coincidences are excluded.</p>
      <div class="exclusions-list">
        <strong>Exclusions Applied:</strong>
        <ul>`;
    data.strict_mode.exclusions.forEach(exclusion => {
      html += `<li>${exclusion}</li>`;
    });
    html += `</ul></div></div>`;
  }
  
  // Dataset Profile
  if (data.dataset_profile) {
    html += `<div class="section profile-section">
      <h3>📈 Dataset Profile</h3>
      <div class="profile-grid">`;
    
    data.dataset_profile.columns.forEach(col => {
      html += `<div class="profile-card">
        <h4>${col.name}</h4>
        <p><strong>Type:</strong> ${col.type}</p>
        <p><strong>Nulls:</strong> ${col.null_count} (${col.null_percentage.toFixed(1)}%)</p>
        <p><strong>Unique Values:</strong> ${col.unique_count}</p>`;
      
      if (col.statistics) {
        html += `<div class="stats-box">
          <strong>Statistics:</strong>`;
        if (col.statistics.min !== null) html += `<span>Min: ${col.statistics.min.toFixed(2)}</span>`;
        if (col.statistics.max !== null) html += `<span>Max: ${col.statistics.max.toFixed(2)}</span>`;
        if (col.statistics.mean !== null) html += `<span>Mean: ${col.statistics.mean.toFixed(2)}</span>`;
        if (col.statistics.median !== null) html += `<span>Median: ${col.statistics.median.toFixed(2)}</span>`;
        html += `</div>`;
      }
      
      html += `</div>`;
    });
    
    html += `</div></div>`;
  }
  
  // Validation Rules
  if (data.validation_rules && data.validation_rules.rules && data.validation_rules.rules.length > 0) {
    html += `<div class="section validation-section">
      <h3>✅ Validation Rules (${data.validation_rules.count})</h3>
      <p class="section-note">${data.validation_rules.note || 'Universal validation rules - ready for implementation'}</p>`;
    
    data.validation_rules.rules.forEach((rule, index) => {
      html += `<div class="rule-card">
        <div class="rule-header">
          <span class="rule-number">Rule ${index + 1}</span>
          <span class="rule-type validation">Validation Rule</span>
        </div>
        <div class="rule-content">
          <h4>${rule.rule}</h4>
          <p class="rule-description"><strong>Description:</strong> ${rule.description}</p>
          <p class="rule-meaning"><strong>Business Meaning:</strong> ${rule.business_meaning}</p>
          <div class="rule-code">
            <div class="code-block">
              <strong>SQL:</strong>
              <code>${rule.sql}</code>
            </div>
            <div class="code-block">
              <strong>Pseudo Code:</strong>
              <code>${rule.pseudo_code}</code>
            </div>
          </div>
          <p class="confidence"><strong>Confidence:</strong> <span class="confidence-badge ${rule.confidence.toLowerCase()}">${rule.confidence}</span></p>
          <p class="approval-status"><strong>Requires Approval:</strong> <span class="${rule.requires_approval ? 'yes-approval' : 'no-approval'}">${rule.requires_approval ? 'Yes' : 'No'}</span></p>
          <p class="hr-usable"><strong>HR Usable:</strong> <span class="hr-badge">${rule.hr_usable ? 'Yes' : 'Review Required'}</span></p>
        </div>
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Business Rule Candidates
  if (data.business_rule_candidates && data.business_rule_candidates.rules && data.business_rule_candidates.rules.length > 0) {
    html += `<div class="section business-rules-section">
      <h3>💼 Business Rule Candidates (${data.business_rule_candidates.count})</h3>
      <p class="section-note warning-note">⚠️ ${data.business_rule_candidates.note}</p>`;
    
    data.business_rule_candidates.rules.forEach((rule, index) => {
      html += `<div class="rule-card">
        <div class="rule-header">
          <span class="rule-number">Candidate ${index + 1}</span>
          <span class="rule-type candidate">Business Rule Candidate</span>
        </div>
        <div class="rule-content">
          <h4>${rule.rule}</h4>
          <p class="rule-description"><strong>Description:</strong> ${rule.description}</p>
          <p class="rule-logic"><strong>IF-THEN Logic:</strong> ${rule.if_then}</p>
          <p class="rule-meaning"><strong>Business Meaning:</strong> ${rule.business_meaning}</p>
          <div class="rule-code">
            <div class="code-block">
              <strong>SQL:</strong>
              <code>${rule.sql}</code>
            </div>
            <div class="code-block">
              <strong>Pseudo Code:</strong>
              <code>${rule.pseudo_code}</code>
            </div>
          </div>`;
      
      if (rule.threshold !== undefined) {
        html += `<p class="rule-threshold"><strong>Threshold:</strong> ${rule.threshold}</p>`;
      }
      
      html += `          <p class="confidence"><strong>Confidence:</strong> <span class="confidence-badge ${rule.confidence.toLowerCase()}">${rule.confidence}</span></p>
          <p class="approval-status"><strong>Requires Approval:</strong> <span class="${rule.requires_approval ? 'yes-approval' : 'no-approval'}">${rule.requires_approval ? 'Yes - Review with HR' : 'No'}</span></p>
          <p class="hr-usable"><strong>HR Usable:</strong> <span class="hr-badge">${rule.hr_usable ? 'Yes' : 'Review Required'}</span></p>
        </div>
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Decision Rules
  if (data.decision_rules && data.decision_rules.rules && data.decision_rules.rules.length > 0) {
    html += `<div class="section decision-rules-section">
      <h3>🎯 Decision Rules (${data.decision_rules.count})</h3>
      <p class="section-note">${data.decision_rules.note}</p>`;
    
    data.decision_rules.rules.forEach((rule, index) => {
      html += `<div class="rule-card">
        <div class="rule-header">
          <span class="rule-number">Decision Rule ${index + 1}</span>
          <span class="rule-type decision">Decision Rule</span>
        </div>
        <div class="rule-content">
          <h4>${rule.column}</h4>
          <p class="rule-description"><strong>Description:</strong> ${rule.description}</p>
          <p class="rule-logic"><strong>IF-ELSE Logic:</strong></p>
          <pre class="logic-block">${rule.if_else}</pre>
          <p class="rule-meaning"><strong>Business Meaning:</strong> ${rule.business_meaning}</p>
          <div class="bands-container">
            <strong>Decision Bands:</strong>`;
      
      rule.bands.forEach(band => {
        html += `<div class="band-item">
          <span class="band-name">${band.name}:</span>
          <span class="band-range">${band.min.toFixed(2)} - ${band.max.toFixed(2)}</span>
        </div>`;
      });
      
      html += `</div>
          <div class="rule-code">
            <div class="code-block">
              <strong>SQL:</strong>
              <code>${rule.sql}</code>
            </div>
            <div class="code-block">
              <strong>Pseudo Code:</strong>
              <code>${rule.pseudo_code}</code>
            </div>
          </div>
          <p class="confidence"><strong>Confidence:</strong> <span class="confidence-badge ${rule.confidence.toLowerCase()}">${rule.confidence}</span></p>
          <p class="approval-status"><strong>Requires Approval:</strong> <span class="${rule.requires_approval ? 'yes-approval' : 'no-approval'}">${rule.requires_approval ? 'Yes - Review with HR' : 'No'}</span></p>
          <p class="hr-usable"><strong>HR Usable:</strong> <span class="hr-badge">${rule.hr_usable ? 'Yes' : 'Review Required'}</span></p>
        </div>
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Constraints
  if (data.constraints && data.constraints.rules && data.constraints.rules.length > 0) {
    html += `<div class="section constraints-section">
      <h3>🔒 Constraints (${data.constraints.count})</h3>
      <p class="section-note">${data.constraints.note}</p>`;
    
    data.constraints.rules.forEach((rule, index) => {
      html += `<div class="rule-card">
        <div class="rule-header">
          <span class="rule-number">Constraint ${index + 1}</span>
          <span class="rule-type constraint">Constraint</span>
        </div>
        <div class="rule-content">
          <h4>${rule.column}</h4>
          <p class="rule-description"><strong>Constraint:</strong> ${rule.constraint}</p>
          <p class="rule-meaning"><strong>Business Meaning:</strong> ${rule.business_meaning}</p>`;
      
      if (rule.observed_range) {
        html += `<div class="range-box">
          <strong>Observed Range:</strong> ${rule.observed_range.min.toFixed(2)} - ${rule.observed_range.max.toFixed(2)}<br>
          <strong>Recommended Range:</strong> ${rule.recommended_range.min.toFixed(2)} - ${rule.recommended_range.max.toFixed(2)}
        </div>`;
      }
      
      html += `<div class="rule-code">
            <div class="code-block">
              <strong>SQL:</strong>
              <code>${rule.sql}</code>
            </div>
            <div class="code-block">
              <strong>Pseudo Code:</strong>
              <code>${rule.pseudo_code}</code>
            </div>
          </div>
          <p class="confidence"><strong>Confidence:</strong> <span class="confidence-badge ${rule.confidence.toLowerCase()}">${rule.confidence}</span></p>
          <p class="approval-status"><strong>Requires Approval:</strong> <span class="${rule.requires_approval ? 'yes-approval' : 'no-approval'}">${rule.requires_approval ? 'Yes - Validate with HR' : 'No'}</span></p>
          <p class="hr-usable"><strong>HR Usable:</strong> <span class="hr-badge">${rule.hr_usable ? 'Yes' : 'Review Required'}</span></p>
        </div>
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Derivations
  if (data.derivations && data.derivations.rules && data.derivations.rules.length > 0) {
    html += `<div class="section derivations-section">
      <h3>🧮 Calculated Fields / Derivations (${data.derivations.count})</h3>
      <p class="section-note">${data.derivations.note}</p>`;
    
    data.derivations.rules.forEach((rule, index) => {
      html += `<div class="rule-card">
        <div class="rule-header">
          <span class="rule-number">Derivation ${index + 1}</span>
          <span class="rule-type derivation">Derivation</span>
        </div>
        <div class="rule-content">
          <h4>${rule.derived_field}</h4>
          <p class="rule-description"><strong>Formula:</strong> ${rule.formula}</p>
          <p class="rule-meaning"><strong>Business Meaning:</strong> ${rule.business_meaning}</p>
          <div class="rule-code">
            <div class="code-block">
              <strong>SQL:</strong>
              <code>${rule.sql}</code>
            </div>
            <div class="code-block">
              <strong>Pseudo Code:</strong>
              <code>${rule.pseudo_code}</code>
            </div>
          </div>
          <p class="confidence"><strong>Confidence:</strong> <span class="confidence-badge ${rule.confidence.toLowerCase()}">${rule.confidence}</span></p>
          <p class="approval-status"><strong>Requires Approval:</strong> <span class="${rule.requires_approval ? 'yes-approval' : 'no-approval'}">${rule.requires_approval ? 'Yes - Confirm with HR' : 'No'}</span></p>
          <p class="hr-usable"><strong>HR Usable:</strong> <span class="hr-badge">${rule.hr_usable ? 'Yes' : 'Review Required'}</span></p>
        </div>
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Associations
  if (data.associations && data.associations.rules && data.associations.rules.length > 0) {
    html += `<div class="section associations-section">
      <h3>🔗 Associations (${data.associations.count})</h3>`;
    
    data.associations.rules.forEach((rule, index) => {
      html += `<div class="rule-card">
        <div class="rule-header">
          <span class="rule-number">Association ${index + 1}</span>
          <span class="rule-type association">${rule.type}</span>
        </div>
        <div class="rule-content">
          <h4>${rule.columns.join(' ↔ ')}</h4>
          <p class="rule-description"><strong>Description:</strong> ${rule.description}</p>`;
      
      if (rule.correlation !== undefined) {
        html += `<p class="correlation-info">
          <strong>Correlation:</strong> ${rule.correlation.toFixed(3)} 
          <span class="strength-badge ${rule.strength.toLowerCase()}">${rule.strength}</span>
          <span class="direction-badge">${rule.direction}</span>
        </p>`;
      }
      
      html += `<p class="rule-meaning"><strong>Business Meaning:</strong> ${rule.business_meaning}</p>
          <div class="rule-code">
            <div class="code-block">
              <strong>SQL:</strong>
              <code>${rule.sql}</code>
            </div>
            <div class="code-block">
              <strong>Pseudo Code:</strong>
              <code>${rule.pseudo_code}</code>
            </div>
          </div>
          <p class="confidence"><strong>Confidence:</strong> <span class="confidence-badge ${rule.confidence.toLowerCase()}">${rule.confidence}</span></p>
          ${rule.hr_usable !== undefined ? `<p class="hr-usable"><strong>HR Usable:</strong> <span class="hr-badge">${rule.hr_usable ? 'Yes' : 'Review Required'}</span></p>` : ''}
        </div>
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Data Quality Warnings
  if (data.data_quality_warnings && data.data_quality_warnings.items && data.data_quality_warnings.items.length > 0) {
    html += `<div class="section warnings-section">
      <h3>⚠️ Data Quality Warnings (${data.data_quality_warnings.count})</h3>
      <p class="section-note warning-note">${data.data_quality_warnings.note}</p>`;
    
    data.data_quality_warnings.items.forEach((warning, index) => {
      html += `<div class="warning-card">
        <div class="warning-header">
          <span class="warning-type">${warning.type}</span>
          <span class="warning-impact ${warning.impact.toLowerCase()}">${warning.impact} Impact</span>
        </div>
        <h4>${warning.title}</h4>
        <p class="warning-description">${warning.description}</p>
        ${warning.recommendation ? `<p class="warning-recommendation"><strong>Recommendation:</strong> ${warning.recommendation}</p>` : ''}
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Statistical Insights (Clearly marked as NOT business rules)
  if (data.statistical_insights && data.statistical_insights.items && data.statistical_insights.items.length > 0) {
    html += `<div class="section statistical-insights-section">
      <h3>📊 Statistical Insights (${data.statistical_insights.count})</h3>
      <div class="statistical-warning-box">
        <strong>⚠️ IMPORTANT:</strong> ${data.statistical_insights.note}
      </div>`;
    
    data.statistical_insights.items.forEach((insight, index) => {
      const typeClass = insight.type.toLowerCase().replace(' ', '-');
      html += `<div class="insight-card ${typeClass} statistical">
        <div class="insight-header">
          <span class="insight-type">${insight.type}</span>
          <span class="insight-impact ${insight.impact.toLowerCase()}">${insight.impact} Impact</span>
        </div>
        <h4>${insight.title}</h4>
        <p class="insight-description">${insight.description}</p>
        ${insight.note ? `<p class="statistical-note"><strong>Note:</strong> ${insight.note}</p>` : ''}
      </div>`;
    });
    
    html += `</div>`;
  }
  
  // Recommendations
  if (data.recommendations && data.recommendations.length > 0) {
    html += `<div class="section recommendations-section">
      <h3>💼 Recommendations</h3>
      <ul class="recommendations-list">`;
    data.recommendations.forEach(rec => {
      html += `<li>${rec}</li>`;
    });
    html += `</ul></div>`;
  }
  
  // Raw JSON toggle
  html += `<div class="section raw-section">
    <button onclick="toggleRawData()" class="toggle-btn">Show/Hide Raw JSON</button>
    <pre id="rawData" style="display:none;">${JSON.stringify(data, null, 2)}</pre>
  </div>`;
  
  html += '</div>';
  return html;
}

function toggleRawData() {
  const rawData = document.getElementById('rawData');
  rawData.style.display = rawData.style.display === 'none' ? 'block' : 'none';
}

// File input handler
document.getElementById("fileInput").addEventListener("change", function(e) {
  const fileName = e.target.files[0]?.name || "Choose File";
  document.getElementById("fileName").textContent = fileName;
});

async function upload() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const resultDiv = document.getElementById("result");
  const button = document.getElementById("analyzeBtn");
  const loading = document.getElementById("loading");
  const analysisMode = document.querySelector('input[name="analysisMode"]:checked').value;
  const useML = document.getElementById("useML").checked;
  
  // Validate file selection
  if (!file) {
    resultDiv.innerHTML = '<div class="error-message">⚠️ Error: Please select a file first.</div>';
    return;
  }
  
  // Validate file type
  const validExtensions = ['.csv', '.xls', '.xlsx'];
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
  if (!validExtensions.includes(fileExtension)) {
    resultDiv.innerHTML = '<div class="error-message">⚠️ Error: Please upload a CSV, XLS, or XLSX file.</div>';
    return;
  }
  
  // Show loading state
  button.disabled = true;
  button.querySelector(".btn-text").textContent = "Analyzing...";
  loading.style.display = "block";
  resultDiv.innerHTML = "";
  
  try {
    const formData = new FormData();
    formData.append("file", file);
    
    // Determine API endpoint based on analysis mode
    let apiUrl;
    if (analysisMode === "prediction") {
      apiUrl = window.location.origin === "file://" 
        ? "http://127.0.0.1:8000/analyze-prediction" 
        : "/analyze-prediction";
    } else if (analysisMode === "decision-tree") {
      apiUrl = window.location.origin === "file://" 
        ? `http://127.0.0.1:8000/analyze-decision-tree?use_ml=${useML}` 
        : `/analyze-decision-tree?use_ml=${useML}`;
    } else {
      apiUrl = window.location.origin === "file://" 
        ? "http://127.0.0.1:8000/analyze" 
        : "/analyze";
    }
    
    const res = await fetch(apiUrl, {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || `Server error: ${res.status}`);
    }

    const data = await res.json();
    
    // Format results based on analysis mode
    if (analysisMode === "prediction") {
      resultDiv.innerHTML = formatPredictionResults(data);
    } else if (analysisMode === "decision-tree") {
      resultDiv.innerHTML = formatDecisionTreeResults(data);
    } else {
      resultDiv.innerHTML = formatResults(data);
    }
    
    // Scroll to results
    resultDiv.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    resultDiv.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
  } finally {
    button.disabled = false;
    button.querySelector(".btn-text").textContent = "Analyze Dataset";
    loading.style.display = "none";
  }
}

function formatPredictionResults(data) {
  let html = '<div class="results-container prediction-results">';
  
  // Header
  html += `<div class="section header-section">
    <h2>🎯 Comprehensive HR Prediction Results</h2>
    <div class="summary-badges">
      <span class="domain-badge-header">Domain: ${data.domain || "Unknown"}</span>
      <span class="confidence-badge ${(data.domain_confidence || "Low").toLowerCase()}">${data.domain_confidence || "Low"} Confidence</span>
      <span class="purpose-badge">Records: ${data.total_records || 0}</span>
    </div>`;
  
  // Keyword Matches with Detailed Logic Flow
  if (data.keyword_matches) {
    html += `<div class="keywords-summary">
      <strong>Matched Keywords:</strong> ${data.keyword_matches.total_matches || 0} keywords found in ${data.keyword_matches.total_columns || 0} columns
      <div class="keyword-categories">`;
    
    if (data.keyword_matches.categorized) {
      Object.entries(data.keyword_matches.categorized).forEach(([category, info]) => {
        html += `<div class="category-badge">
          <span class="category-name">${category}</span>
          <span class="category-count">${info.keywords.length} keywords</span>
        </div>`;
      });
    }
    
    html += `</div>`;
    
    // Show keyword to column mapping
    if (data.keyword_matches.keyword_to_column_mapping) {
      html += `<div class="keyword-mapping-section">
        <h4>🔗 Keyword → Column Mapping</h4>
        <div class="mapping-table-container">
          <table class="mapping-table">
            <thead>
              <tr>
                <th>Matched Keyword</th>
                <th>Column(s) Found</th>
                <th>Match Type</th>
              </tr>
            </thead>
            <tbody>`;
      
      Object.entries(data.keyword_matches.keyword_to_column_mapping).forEach(([keyword, columns]) => {
        columns.forEach((colInfo, idx) => {
          html += `<tr>
            <td><strong>${keyword}</strong></td>
            <td>${colInfo.column}</td>
            <td><span class="match-type-badge ${colInfo.match_type}">${colInfo.match_type}</span></td>
          </tr>`;
        });
      });
      
      html += `</tbody></table></div></div>`;
    }
    
    html += `</div>`;
  }
  
  // Logic Summary - Show complete flow
  if (data.logic_summary && data.logic_summary.length > 0) {
    html += `<div class="section logic-flow-section">
      <h3>🔀 Complete Logic Flow</h3>
      <p class="section-note">Shows how keywords trigger rules and generate predictions</p>`;
    
    data.logic_summary.forEach((logic, idx) => {
      html += `<div class="logic-flow-card">
        <div class="logic-header">
          <span class="logic-category">${logic.category.toUpperCase()}</span>
          <span class="logic-index">Flow ${idx + 1}</span>
        </div>
        <div class="logic-steps">
          <div class="logic-step">
            <span class="step-number">1</span>
            <div class="step-content">
              <strong>Keywords Matched:</strong>
              <div class="step-keywords">${logic.triggered_by.map(k => `<span class="keyword-badge">${k}</span>`).join(" ")}</div>
            </div>
          </div>
          <div class="logic-step">
            <span class="step-number">2</span>
            <div class="step-content">
              <strong>Columns Used:</strong>
              <div class="step-columns">${logic.columns_used.map(c => `<span class="column-badge">${c}</span>`).join(" ")}</div>
            </div>
          </div>
          <div class="logic-step">
            <span class="step-number">3</span>
            <div class="step-content">
              <strong>Business Rule Applied:</strong>
              <div class="rule-display">${logic.rule_applied}</div>
            </div>
          </div>
          <div class="logic-step">
            <span class="step-number">4</span>
            <div class="step-content">
              <strong>Result:</strong>
              <div class="result-display">Predictions generated for all records based on data values</div>
            </div>
          </div>
        </div>
      </div>`;
    });
    
    html += `</div>`;
  }
  
  html += `</div>`;
  
  // Predictions for each category
  if (data.predictions) {
    // Salary Predictions
    if (data.predictions.salary && !data.predictions.salary.error) {
      const salary = data.predictions.salary;
      html += `<div class="section prediction-section salary-section">
        <h3>💰 Salary Level Predictions</h3>
        <p class="business-rule">${salary.business_rule}</p>`;
      
      // Statistics
      if (salary.statistics) {
        html += `<div class="prediction-stats">
          <div class="stat-card">
            <div class="stat-value">${salary.statistics.high_count || 0}</div>
            <div class="stat-label">High Salary</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${salary.statistics.medium_count || 0}</div>
            <div class="stat-label">Medium Salary</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${salary.statistics.low_count || 0}</div>
            <div class="stat-label">Low Salary</div>
          </div>
        </div>`;
        
        if (salary.statistics.highest_record) {
          const hr = salary.statistics.highest_record;
          html += `<div class="highlight-record">
            <h4>🏆 Highest Salary Record</h4>
            <div class="record-details">
              <div class="detail-row">
                <span class="detail-label">Employee:</span>
                <span class="detail-value">${hr.employee_name || "N/A"}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Salary:</span>
                <span class="detail-value highlight-value">${hr.salary ? hr.salary.toLocaleString() : "N/A"}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Prediction:</span>
                <span class="detail-value">${hr.prediction}</span>
              </div>
            </div>
          </div>`;
        }
      }
      
      // Show matched keywords and logic flow
      if (salary.matched_keywords) {
        html += `<div class="matched-info">
          <strong>Triggered by Keywords:</strong> ${salary.matched_keywords.map(k => `<span class="keyword-tag">${k}</span>`).join(" ")}
          <br><strong>Using Columns:</strong> ${salary.matched_columns.map(c => `<span class="column-tag">${c}</span>`).join(" ")}
        </div>`;
      }
      
      if (salary.logic_flow) {
        html += `<div class="logic-flow-box">
          <h5>Logic Flow:</h5>
          <div class="flow-steps">
            <div class="flow-step">Keyword: <strong>${salary.logic_flow.triggered_by}</strong> → Column: <strong>${salary.logic_flow.column_used}</strong></div>
            <div class="flow-step">Rule: <strong>${salary.logic_flow.rule_applied}</strong></div>
            <div class="flow-step">Thresholds: High ≥ ${salary.logic_flow.thresholds.high.toLocaleString()}, Medium ≥ ${salary.logic_flow.thresholds.medium.toLocaleString()}</div>
          </div>
        </div>`;
      }
      
      // Predictions Table
      html += `<div class="predictions-table-container">
        <h4>All Salary Predictions (with Logic Steps)</h4>
        <table class="predictions-table">
          <thead>
            <tr>
              <th>Record</th>
              <th>Employee Name</th>
              <th>Salary</th>
              <th>Prediction</th>
              <th>Logic Steps</th>
              <th>Explanation</th>
            </tr>
          </thead>
          <tbody>`;
      
      salary.predictions.forEach(pred => {
        html += `<tr>
          <td>#${pred.record_index + 1}</td>
          <td><strong>${pred.employee_name || "Unknown"}</strong></td>
          <td>${pred.salary ? pred.salary.toLocaleString() : "N/A"}</td>
          <td><span class="prediction-badge ${pred.prediction.toLowerCase()}">${pred.prediction}</span></td>
          <td class="logic-steps-cell">`;
        
        if (pred.logic_steps) {
          pred.logic_steps.forEach(step => {
            html += `<div class="logic-step-item">${step}</div>`;
          });
        }
        
        html += `</td>
          <td class="explanation-cell">${pred.explanation}</td>
        </tr>`;
      });
      
      html += `</tbody></table></div></div>`;
    }
    
    // Attendance Predictions
    if (data.predictions.attendance) {
      const attendance = data.predictions.attendance;
      html += `<div class="section prediction-section attendance-section">
        <h3>⏰ Attendance Status Predictions</h3>
        <p class="business-rule">${attendance.business_rule}</p>`;
      
      // Statistics
      if (attendance.statistics) {
        html += `<div class="prediction-stats">
          <div class="stat-card normal">
            <div class="stat-value">${attendance.statistics.normal_count || 0}</div>
            <div class="stat-label">Normal</div>
          </div>
          <div class="stat-card warning">
            <div class="stat-value">${attendance.statistics.warning_count || 0}</div>
            <div class="stat-label">Warning</div>
          </div>
          <div class="stat-card worst">
            <div class="stat-value">${attendance.statistics.worst_count || 0}</div>
            <div class="stat-label">Worst</div>
          </div>
        </div>`;
        
        if (attendance.statistics.best_record) {
          const br = attendance.statistics.best_record;
          html += `<div class="highlight-record best">
            <h4>✅ Best Attendance Record</h4>
            <div class="record-details">
              <div class="detail-row">
                <span class="detail-label">Employee:</span>
                <span class="detail-value">${br.employee_name || "N/A"}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Attendance:</span>
                <span class="detail-value highlight-value">${br.attendance_percentage ? br.attendance_percentage.toFixed(1) + "%" : "N/A"}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="detail-value">${br.status} (${br.category})</span>
              </div>
            </div>
          </div>`;
        }
        
        if (attendance.statistics.worst_record) {
          const wr = attendance.statistics.worst_record;
          html += `<div class="highlight-record worst">
            <h4>⚠️ Worst Attendance Record</h4>
            <div class="record-details">
              <div class="detail-row">
                <span class="detail-label">Employee:</span>
                <span class="detail-value">${wr.employee_name || "N/A"}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Attendance:</span>
                <span class="detail-value highlight-value">${wr.attendance_percentage ? wr.attendance_percentage.toFixed(1) + "%" : "N/A"}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="detail-value">${wr.status} (${wr.category})</span>
              </div>
            </div>
          </div>`;
        }
      }
      
      // Predictions Table
      html += `<div class="predictions-table-container">
        <h4>All Attendance Predictions</h4>
        <table class="predictions-table">
          <thead>
            <tr>
              <th>Record</th>
              <th>Employee Name</th>
              <th>Attendance %</th>
              <th>Status</th>
              <th>Category</th>
              <th>Explanation</th>
            </tr>
          </thead>
          <tbody>`;
      
      attendance.predictions.forEach(pred => {
        html += `<tr>
          <td>#${pred.record_index + 1}</td>
          <td><strong>${pred.employee_name || "Unknown"}</strong></td>
          <td>${pred.attendance_percentage ? pred.attendance_percentage.toFixed(1) + "%" : "N/A"}</td>
          <td><span class="prediction-badge ${pred.status.toLowerCase()}">${pred.status}</span></td>
          <td><span class="category-badge-small ${pred.category.toLowerCase()}">${pred.category}</span></td>
          <td class="explanation-cell">${pred.explanation}</td>
        </tr>`;
      });
      
      html += `</tbody></table></div></div>`;
    }
    
    // Leave Predictions
    if (data.predictions.leave) {
      const leave = data.predictions.leave;
      html += `<div class="section prediction-section leave-section">
        <h3>📅 Leave Analysis Predictions</h3>
        <p class="business-rule">${leave.business_rule}</p>`;
      
      // Statistics
      if (leave.statistics) {
        html += `<div class="prediction-stats">
          <div class="stat-card">
            <div class="stat-value">${leave.statistics.approved_count || 0}</div>
            <div class="stat-label">Approved</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${leave.statistics.rejected_count || 0}</div>
            <div class="stat-label">Rejected</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${leave.statistics.lop_count || 0}</div>
            <div class="stat-label">LOP</div>
          </div>
        </div>`;
      }
      
      // Predictions Table with Person Names
      html += `<div class="predictions-table-container">
        <h4>All Leave Predictions (with Person Names)</h4>
        <table class="predictions-table">
          <thead>
            <tr>
              <th>Record</th>
              <th>Employee Name</th>
              <th>Leave Type</th>
              <th>Days</th>
              <th>Status</th>
              <th>Explanation</th>
            </tr>
          </thead>
          <tbody>`;
      
      leave.predictions.forEach(pred => {
        html += `<tr>
          <td>#${pred.record_index + 1}</td>
          <td><strong>${pred.employee_name || "Unknown"}</strong></td>
          <td>${pred.leave_type || "N/A"}</td>
          <td>${pred.leave_days || "N/A"}</td>
          <td><span class="prediction-badge">${pred.status}</span></td>
          <td class="explanation-cell">${pred.explanation}</td>
        </tr>`;
      });
      
      html += `</tbody></table></div></div>`;
    }
    
    // Performance Predictions
    if (data.predictions.performance && !data.predictions.performance.error) {
      const perf = data.predictions.performance;
      html += `<div class="section prediction-section performance-section">
        <h3>⭐ Performance Level Predictions</h3>
        <p class="business-rule">${perf.business_rule}</p>`;
      
      // Statistics
      if (perf.statistics) {
        html += `<div class="prediction-stats">
          <div class="stat-card">
            <div class="stat-value">${perf.statistics.excellent_count || 0}</div>
            <div class="stat-label">Excellent</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${perf.statistics.good_count || 0}</div>
            <div class="stat-label">Good</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${perf.statistics.needs_improvement_count || 0}</div>
            <div class="stat-label">Needs Improvement</div>
          </div>
        </div>`;
      }
      
      // Predictions Table
      html += `<div class="predictions-table-container">
        <h4>All Performance Predictions</h4>
        <table class="predictions-table">
          <thead>
            <tr>
              <th>Record</th>
              <th>Employee Name</th>
              <th>Rating</th>
              <th>Performance</th>
              <th>Increment %</th>
              <th>Explanation</th>
            </tr>
          </thead>
          <tbody>`;
      
      perf.predictions.forEach(pred => {
        html += `<tr>
          <td>#${pred.record_index + 1}</td>
          <td><strong>${pred.employee_name || "Unknown"}</strong></td>
          <td>${pred.rating || "N/A"}</td>
          <td><span class="prediction-badge ${pred.performance_level.toLowerCase().replace(' ', '-')}">${pred.performance_level}</span></td>
          <td>${pred.increment_percentage}%</td>
          <td class="explanation-cell">${pred.explanation}</td>
        </tr>`;
      });
      
      html += `</tbody></table></div></div>`;
    }
  }
  
  // Raw JSON toggle
  html += `<div class="section raw-section">
    <button onclick="toggleRawData()" class="toggle-btn">Show/Hide Raw JSON</button>
    <pre id="rawData" style="display:none;">${JSON.stringify(data, null, 2)}</pre>
  </div>`;
  
  html += '</div>';
  return html;
}

function formatDecisionTreeResults(data) {
  let html = '<div class="results-container decision-tree-results">';
  
  // Header Section
  html += `<div class="section header-section">
    <h2>🎯 Decision Tree Analysis Results</h2>
    <div class="summary-badges">
      <span class="domain-badge-header">Domain: ${data.detected_domain || "Unknown"}</span>
      <span class="purpose-badge">Purpose: ${data.detected_purpose || "Unknown"}</span>
      <span class="confidence-badge ${(data.purpose_confidence || "Low").toLowerCase()}">${data.purpose_confidence || "Low"} Confidence</span>
      <span class="confidence-badge ${(data.confidence_level || "Low").toLowerCase()}">Overall: ${data.confidence_level || "Low"}</span>
    </div>`;
  
  // Show matched keywords
  if (data.matched_keywords && data.matched_keywords.length > 0) {
    html += `<div class="keywords-header">
      <strong>Matched Keywords:</strong> ${data.matched_keywords.slice(0, 10).map(k => `<span class="keyword-tag-small">${k}</span>`).join(" ")}
    </div>`;
  }
  
  if (data.domain_keywords_matched && data.domain_keywords_matched.length > 0) {
    html += `<div class="keywords-header">
      <strong>Domain Keywords:</strong> ${data.domain_keywords_matched.slice(0, 10).map(k => `<span class="keyword-tag-small">${k}</span>`).join(" ")}
    </div>`;
  }
  
  html += `</div>`;
  
  // Step-by-Step Reasoning
  if (data.step_by_step_reasoning && data.step_by_step_reasoning.length > 0) {
    html += `<div class="section reasoning-section">
      <h3>📋 Step-by-Step Reasoning</h3>`;
    
    data.step_by_step_reasoning.forEach(step => {
      html += `<div class="reasoning-step">
        <div class="step-number">Step ${step.step}</div>
        <div class="step-content">
          <p class="step-description">${step.description}</p>`;
      
      if (step.keywords_matched && step.keywords_matched.length > 0) {
        html += `<div class="keywords-list">
          <strong>Matched Keywords:</strong> ${step.keywords_matched.map(k => `<span class="keyword-tag">${k}</span>`).join(" ")}
        </div>`;
      }
      
      if (step.ml_rules_count) {
        html += `<div class="ml-info">
          <strong>ML Rules Discovered:</strong> ${step.ml_rules_count}
        </div>`;
      }
      
      if (step.feature_importance) {
        html += `<div class="feature-importance">
          <strong>Top Features:</strong>`;
        Object.entries(step.feature_importance).slice(0, 5).forEach(([feat, imp]) => {
          html += `<span class="feature-tag">${feat} (${imp.toFixed(1)}%)</span>`;
        });
        html += `</div>`;
      }
      
      html += `</div></div>`;
    });
    
    html += `</div>`;
  }
  
  // Applied Rules Summary
  if (data.applied_rules) {
    const rules = data.applied_rules;
    html += `<div class="section rules-summary-section">
      <h3>⚙️ Applied Rules Summary</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">${rules.total_records_analyzed || 0}</div>
          <div class="stat-label">Records Analyzed</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${rules.total_rules_applied || 0}</div>
          <div class="stat-label">Total Rules Applied</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${(rules.average_rules_per_record || 0).toFixed(1)}</div>
          <div class="stat-label">Avg Rules/Record</div>
        </div>
      </div>
    </div>`;
  }
  
  // Business Rules Applied
  if (data.business_rules_applied && data.business_rules_applied.length > 0) {
    html += `<div class="section business-rules-section">
      <h3>🔧 Business Rules Applied</h3>
      <div class="rules-list">`;
    
    data.business_rules_applied.forEach((rule, idx) => {
      html += `<div class="rule-item">
        <span class="rule-index">${idx + 1}</span>
        <span class="rule-text">${rule}</span>
      </div>`;
    });
    
    html += `</div></div>`;
  }
  
  // Record Analyses (Sample)
  if (data.applied_rules && data.applied_rules.record_analyses && data.applied_rules.record_analyses.length > 0) {
    html += `<div class="section records-section">
      <h3>📊 Sample Record Analyses</h3>
      <p class="section-note">Showing first ${Math.min(5, data.applied_rules.record_analyses.length)} records</p>`;
    
    data.applied_rules.record_analyses.slice(0, 5).forEach(record => {
      html += `<div class="record-analysis-card">
        <div class="record-header">
          <span class="record-id">Record #${record.record_index + 1}</span>
        </div>`;
      
      if (record.applied_rules && record.applied_rules.length > 0) {
        html += `<div class="applied-rules-list">`;
        record.applied_rules.forEach(rule => {
          html += `<div class="applied-rule-item">
            <div class="rule-name">${rule.rule || "Rule"}</div>
            <div class="rule-decision">${rule.decision || ""}</div>
            <div class="rule-explanation">${rule.explanation || ""}</div>
            <div class="rule-confidence">
              <span class="confidence-badge ${(rule.confidence || "Medium").toLowerCase()}">${rule.confidence || "Medium"}</span>
            </div>
          </div>`;
        });
        html += `</div>`;
      }
      
      if (record.decisions) {
        html += `<div class="record-decisions">
          <strong>Final Decisions:</strong>`;
        Object.entries(record.decisions).forEach(([key, value]) => {
          html += `<div class="decision-item">
            <span class="decision-key">${key}:</span>
            <span class="decision-value">${value}</span>
          </div>`;
        });
        html += `</div>`;
      }
      
      html += `</div>`;
    });
    
    html += `</div>`;
  }
  
  // Final Decisions Summary
  if (data.final_decisions_summary) {
    html += `<div class="section decisions-summary-section">
      <h3>✅ Final Decisions Summary</h3>`;
    
    Object.entries(data.final_decisions_summary).forEach(([key, summary]) => {
      html += `<div class="decision-summary-card">
        <h4>${key}</h4>`;
      
      if (summary.distribution) {
        html += `<div class="distribution-chart">`;
        Object.entries(summary.distribution).forEach(([value, count]) => {
          const percentage = (count / summary.total_count * 100).toFixed(1);
          html += `<div class="distribution-item">
            <div class="dist-label">${value}</div>
            <div class="dist-bar-container">
              <div class="dist-bar" style="width: ${percentage}%"></div>
            </div>
            <div class="dist-count">${count} (${percentage}%)</div>
          </div>`;
        });
        html += `</div>`;
      }
      
      html += `</div>`;
    });
    
    html += `</div>`;
  }
  
  // ML Pattern Recognition
  if (data.ml_pattern_recognition && !data.ml_pattern_recognition.error) {
    html += `<div class="section ml-section">
      <h3>🤖 ML Pattern Recognition</h3>`;
    
    if (data.ml_pattern_recognition.ml_discovered_rules && data.ml_pattern_recognition.ml_discovered_rules.length > 0) {
      html += `<div class="ml-rules">
        <h4>ML-Discovered Rules</h4>`;
      data.ml_pattern_recognition.ml_discovered_rules.slice(0, 5).forEach((rule, idx) => {
        html += `<div class="ml-rule-item">${idx + 1}. ${rule}</div>`;
      });
      html += `</div>`;
    }
    
    if (data.ml_pattern_recognition.apriori_patterns && data.ml_pattern_recognition.apriori_patterns.length > 0) {
      html += `<div class="apriori-patterns">
        <h4>Hidden Patterns (Apriori)</h4>`;
      data.ml_pattern_recognition.apriori_patterns.forEach(pattern => {
        html += `<div class="pattern-item">${pattern}</div>`;
      });
      html += `</div>`;
    }
    
    html += `</div>`;
  }
  
  // Data Insights (Highest Values, Statistics)
  if (data.data_insights && Object.keys(data.data_insights).length > 0) {
    html += `<div class="section insights-section">
      <h3>📊 Data Insights & Statistics</h3>`;
    
    if (data.data_insights.salary) {
      const salary = data.data_insights.salary;
      html += `<div class="insight-card salary-insight">
        <h4>💰 Salary Analysis</h4>
        <div class="insight-stats">
          <div class="stat-item">
            <span class="stat-label">Highest Salary:</span>
            <span class="stat-value highlight">${salary.highest.toLocaleString()}</span>
            <span class="stat-note">(Record #${salary.highest_record_index + 1})</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Lowest Salary:</span>
            <span class="stat-value">${salary.lowest.toLocaleString()}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Average Salary:</span>
            <span class="stat-value">${salary.average.toFixed(2).toLocaleString()}</span>
          </div>
        </div>`;
      
      if (salary.highest_record_data && Object.keys(salary.highest_record_data).length > 0) {
        html += `<div class="highest-record-details">
          <strong>Highest Salary Record Details:</strong>
          <div class="record-details-grid">`;
        Object.entries(salary.highest_record_data).slice(0, 5).forEach(([key, value]) => {
          html += `<div class="detail-item">
            <span class="detail-key">${key}:</span>
            <span class="detail-value">${value}</span>
          </div>`;
        });
        html += `</div></div>`;
      }
      html += `</div>`;
    }
    
    if (data.data_insights.attendance) {
      const attendance = data.data_insights.attendance;
      html += `<div class="insight-card attendance-insight">
        <h4>⏰ Attendance Analysis</h4>
        <div class="insight-stats">
          <div class="stat-item">
            <span class="stat-label">Punch-In Column:</span>
            <span class="stat-value">${attendance.punch_in_column}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Records:</span>
            <span class="stat-value">${attendance.total_records}</span>
          </div>
        </div>`;
      if (attendance.sample_times && attendance.sample_times.length > 0) {
        html += `<div class="sample-times">
          <strong>Sample Times:</strong> ${attendance.sample_times.slice(0, 5).join(", ")}
        </div>`;
      }
      html += `</div>`;
    }
    
    if (data.data_insights.working_hours) {
      const hours = data.data_insights.working_hours;
      html += `<div class="insight-card hours-insight">
        <h4>⏱️ Working Hours Analysis</h4>
        <div class="insight-stats">
          <div class="stat-item">
            <span class="stat-label">Maximum Hours:</span>
            <span class="stat-value">${hours.maximum}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Minimum Hours:</span>
            <span class="stat-value">${hours.minimum}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Average Hours:</span>
            <span class="stat-value">${hours.average.toFixed(2)}</span>
          </div>
        </div>
      </div>`;
    }
    
    if (data.data_insights.performance) {
      const perf = data.data_insights.performance;
      html += `<div class="insight-card performance-insight">
        <h4>⭐ Performance Analysis</h4>
        <div class="insight-stats">
          <div class="stat-item">
            <span class="stat-label">Highest Rating:</span>
            <span class="stat-value highlight">${perf.highest_rating}</span>
            <span class="stat-note">(Record #${perf.highest_record_index + 1})</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Average Rating:</span>
            <span class="stat-value">${perf.average_rating.toFixed(2)}</span>
          </div>
        </div>
      </div>`;
    }
    
    html += `</div>`;
  }
  
  // Table Format Data
  if (data.table_data && data.table_data.rows && data.table_data.rows.length > 0) {
    html += `<div class="section table-section">
      <h3>📋 Complete Results Table</h3>
      <p class="section-note">Showing all records with original data and applied business rule decisions</p>
      <div class="table-container">
        <table class="results-table">
          <thead>
            <tr>`;
    
    data.table_data.columns.forEach(col => {
      const isDecision = data.table_data.decision_columns.includes(col);
      html += `<th class="${isDecision ? 'decision-column' : ''}">${col}</th>`;
    });
    
    html += `</tr></thead><tbody>`;
    
    // Show all rows (or limit to 50 for performance)
    const rowsToShow = data.table_data.rows.slice(0, 50);
    rowsToShow.forEach((row, idx) => {
      html += `<tr>`;
      row.forEach((cell, cellIdx) => {
        const col = data.table_data.columns[cellIdx];
        const isDecision = data.table_data.decision_columns.includes(col);
        html += `<td class="${isDecision ? 'decision-cell' : ''}">${cell || '-'}</td>`;
      });
      html += `</tr>`;
    });
    
    html += `</tbody></table>`;
    
    if (data.table_data.rows.length > 50) {
      html += `<p class="table-note">Showing first 50 of ${data.table_data.total_records} records. Use export for full data.</p>`;
    }
    
    html += `</div></div>`;
  }
  
  // Column Mapping
  if (data.column_mapping && Object.keys(data.column_mapping).length > 0) {
    html += `<div class="section mapping-section">
      <h3>🗺️ Column Mapping</h3>
      <div class="mapping-grid">`;
    
    Object.entries(data.column_mapping).forEach(([ruleField, actualColumn]) => {
      html += `<div class="mapping-item">
        <span class="mapping-rule">${ruleField}</span>
        <span class="mapping-arrow">→</span>
        <span class="mapping-column">${actualColumn}</span>
      </div>`;
    });
    
    html += `</div></div>`;
  }
  
  // Raw JSON toggle
  html += `<div class="section raw-section">
    <button onclick="toggleRawData()" class="toggle-btn">Show/Hide Raw JSON</button>
    <pre id="rawData" style="display:none;">${JSON.stringify(data, null, 2)}</pre>
  </div>`;
  
  html += '</div>';
  return html;
}
