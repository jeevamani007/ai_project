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

async function upload() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const resultDiv = document.getElementById("result");
  const button = document.querySelector("button");
  
  // Validate file selection
  if (!file) {
    resultDiv.textContent = "Error: Please select a file first.";
    resultDiv.style.color = "red";
    return;
  }
  
  // Validate file type
  const validExtensions = ['.csv', '.xls', '.xlsx'];
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
  if (!validExtensions.includes(fileExtension)) {
    resultDiv.textContent = "Error: Please upload a CSV, XLS, or XLSX file.";
    resultDiv.style.color = "red";
    return;
  }
  
  // Show loading state
  button.disabled = true;
  button.textContent = "Analyzing...";
  resultDiv.textContent = "Processing your file, please wait...";
  resultDiv.style.color = "black";
  
  try {
    const formData = new FormData();
    formData.append("file", file);

    // Use relative URL if served from FastAPI, or absolute if standalone
    const apiUrl = window.location.origin === "file://" 
      ? "http://127.0.0.1:8000/analyze" 
      : "/analyze";
    
    const res = await fetch(apiUrl, {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || `Server error: ${res.status}`);
    }

    const data = await res.json();
    resultDiv.innerHTML = formatResults(data);
    resultDiv.style.color = "black";
  } catch (error) {
    resultDiv.textContent = `Error: ${error.message}`;
    resultDiv.style.color = "red";
  } finally {
    button.disabled = false;
    button.textContent = "Analyze";
  }
}
