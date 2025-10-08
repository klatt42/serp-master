/**
 * Export utilities for audit results
 * Supports Markdown and PDF export formats
 */

import { AuditResults, Issue } from './api';

/**
 * Generate Markdown report from audit results
 */
export function generateMarkdownReport(results: AuditResults): string {
  const { url, timestamp, score, issues } = results;

  const date = new Date(timestamp);
  const formattedDate = date.toLocaleDateString();
  const formattedTime = date.toLocaleTimeString();

  // Calculate total issues
  const totalIssues = (issues?.critical?.length || 0) +
                      (issues?.warnings?.length || 0) +
                      (issues?.info?.length || 0);

  const md = `# SEO Audit Report

**Website:** ${url}
**Date:** ${formattedDate} at ${formattedTime}
**Audit ID:** ${results.task_id || 'N/A'}

---

## Executive Summary

### Overall Score: ${score.total_score}/${score.max_score} (${score.grade})

**Percentage:** ${score.percentage.toFixed(1)}%

| Category | Score | Percentage | Status |
|----------|-------|------------|--------|
| Traditional SEO | ${score.component_scores.seo.score}/${score.component_scores.seo.max} | ${score.component_scores.seo.percentage.toFixed(1)}% | ${getScoreStatus(score.component_scores.seo.percentage)} |
| AEO (Answer Engine) | ${score.component_scores.aeo.score}/${score.component_scores.aeo.max} | ${score.component_scores.aeo.percentage.toFixed(1)}% | ${getScoreStatus(score.component_scores.aeo.percentage)} |
| GEO (Generative Engine) | ${score.component_scores.geo.score}/${score.component_scores.geo.max} | ${score.component_scores.geo.percentage.toFixed(1)}% | ${getScoreStatus(score.component_scores.geo.percentage)} |

### Issue Summary
- **Critical Issues:** ${issues?.critical?.length || 0}
- **Warning Issues:** ${issues?.warnings?.length || 0}
- **Info Issues:** ${issues?.info?.length || 0}
- **Quick Wins Available:** ${issues?.quick_wins?.length || 0}
- **Total Issues Found:** ${totalIssues}

---

## Issues Found

### 🔴 Critical Issues (${issues?.critical?.length || 0})

${issues?.critical && issues.critical.length > 0 ? issues.critical.map((issue, i) => `
${i + 1}. **${issue.title}**
   - **Severity:** ${issue.severity}
   - **Category:** ${issue.category}
   - **Description:** ${issue.description}
   - **Impact Score:** ${issue.impact}/10
   - **Pages Affected:** ${issue.pages_affected}
   - **Effort:** ${issue.effort}
   - **Recommendation:** ${issue.recommendation}
${issue.details ? `
   **Explanation:** ${issue.details.explanation}

   **Fix Steps:**
${issue.details.fix_steps.map((step, idx) => `   ${idx + 1}. ${step}`).join('\n')}
${issue.details.code_example ? `
   **Code Example:**
   \`\`\`
   ${issue.details.code_example}
   \`\`\`
` : ''}` : ''}
`).join('\n') : '_No critical issues found._'}

---

### ⚠️ Warning Issues (${issues?.warnings?.length || 0})

${issues?.warnings && issues.warnings.length > 0 ? issues.warnings.map((issue, i) => `
${i + 1}. **${issue.title}**
   - **Severity:** ${issue.severity}
   - **Category:** ${issue.category}
   - **Description:** ${issue.description}
   - **Impact Score:** ${issue.impact}/10
   - **Pages Affected:** ${issue.pages_affected}
   - **Effort:** ${issue.effort}
   - **Recommendation:** ${issue.recommendation}
${issue.details ? `
   **Explanation:** ${issue.details.explanation}

   **Fix Steps:**
${issue.details.fix_steps.map((step, idx) => `   ${idx + 1}. ${step}`).join('\n')}
${issue.details.code_example ? `
   **Code Example:**
   \`\`\`
   ${issue.details.code_example}
   \`\`\`
` : ''}` : ''}
`).join('\n') : '_No warning issues found._'}

---

### ℹ️ Info Issues (${issues?.info?.length || 0})

${issues?.info && issues.info.length > 0 ? issues.info.map((issue, i) => `
${i + 1}. **${issue.title}**
   - **Severity:** ${issue.severity}
   - **Category:** ${issue.category}
   - **Description:** ${issue.description}
   - **Impact Score:** ${issue.impact}/10
   - **Pages Affected:** ${issue.pages_affected}
   - **Effort:** ${issue.effort}
   - **Recommendation:** ${issue.recommendation}
${issue.details ? `
   **Explanation:** ${issue.details.explanation}

   **Fix Steps:**
${issue.details.fix_steps.map((step, idx) => `   ${idx + 1}. ${step}`).join('\n')}
${issue.details.code_example ? `
   **Code Example:**
   \`\`\`
   ${issue.details.code_example}
   \`\`\`
` : ''}` : ''}
`).join('\n') : '_No info issues found._'}

---

## 🚀 Quick Wins (${issues?.quick_wins?.length || 0})

${issues?.quick_wins && issues.quick_wins.length > 0 ? issues.quick_wins.map((issue, i) => `
${i + 1}. **${issue.title}**
   - **Effort:** ${issue.effort}
   - **Impact Score:** ${issue.impact}/10
   - **Pages Affected:** ${issue.pages_affected}
   - **Category:** ${issue.category}
   - **Action:** ${issue.recommendation}
${issue.details ? `
   **Explanation:** ${issue.details.explanation}

   **Fix Steps:**
${issue.details.fix_steps.map((step, idx) => `   ${idx + 1}. ${step}`).join('\n')}
${issue.details.code_example ? `
   **Code Example:**
   \`\`\`
   ${issue.details.code_example}
   \`\`\`
` : ''}` : ''}
`).join('\n') : '_No quick wins identified._'}

---

## Next Steps

1. **Address Critical Issues First** - Focus on the ${issues?.critical?.length || 0} critical issues identified
2. **Implement Quick Wins** - ${issues?.quick_wins?.length || 0} easy improvements available
3. **Monitor Progress** - Re-run audit after implementing fixes
4. **Track Metrics** - Use this report to measure improvement over time

---

*Report generated by SERP-Master*
*For questions or support, refer to the SERP-Master documentation*

## AI Agent Instructions

This report contains structured SEO audit data optimized for automated processing.

**Issue Priority:**
1. Critical (${issues?.critical?.length || 0}) - Immediate attention required
2. Warnings (${issues?.warnings?.length || 0}) - Important optimizations
3. Quick Wins (${issues?.quick_wins?.length || 0}) - Low effort, high impact
4. Info (${issues?.info?.length || 0}) - Nice to have improvements

**Recommended Processing Order:**
1. Parse Quick Wins first for immediate improvements
2. Address Critical issues systematically
3. Implement Warnings based on impact score
4. Consider Info issues for long-term optimization

Each issue includes:
- Detailed explanation
- Step-by-step fix instructions
- Code examples where applicable
- Effort estimation (low/medium/high)
- Impact score (0-10)
`;

  return md;
}

function getScoreStatus(percentage: number): string {
  if (percentage >= 90) return '✅ Excellent';
  if (percentage >= 75) return '🟢 Good';
  if (percentage >= 60) return '🟡 Fair';
  if (percentage >= 40) return '🟠 Needs Work';
  return '🔴 Critical';
}

/**
 * Download markdown file
 */
export function downloadMarkdown(results: AuditResults) {
  const markdown = generateMarkdownReport(results);
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  const filename = `seo-audit-${sanitizeFilename(results.url)}-${new Date().toISOString().split('T')[0]}.md`;

  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Download PDF file
 */
export async function downloadPDF(results: AuditResults) {
  // For PDF, we'll convert markdown to a simple formatted text
  // This avoids adding jsPDF dependency
  const markdown = generateMarkdownReport(results);

  // Create a simple HTML version for print
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>SEO Audit Report - ${results.url}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
      line-height: 1.6;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      color: #333;
    }
    h1 { color: #1a1a1a; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
    h2 { color: #2563eb; margin-top: 30px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }
    h3 { color: #4b5563; margin-top: 20px; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid #d1d5db; padding: 12px; text-align: left; }
    th { background-color: #f3f4f6; font-weight: 600; }
    code { background-color: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
    pre { background-color: #f3f4f6; padding: 12px; border-radius: 6px; overflow-x: auto; }
    .issue { margin: 15px 0; padding: 15px; border-left: 4px solid #e5e7eb; background-color: #f9fafb; }
    .critical { border-left-color: #dc2626; }
    .warning { border-left-color: #f59e0b; }
    .info { border-left-color: #3b82f6; }
    .quick-win { border-left-color: #10b981; }
    @media print {
      body { margin: 0; padding: 15px; }
      .issue { page-break-inside: avoid; }
    }
  </style>
</head>
<body>
${markdownToHTML(markdown)}
</body>
</html>
`;

  // Open print dialog
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();

    // Wait for content to load, then print
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print();
      }, 250);
    };
  }
}

/**
 * Simple markdown to HTML converter (basic implementation)
 */
function markdownToHTML(markdown: string): string {
  let html = markdown
    // Headers
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Code blocks
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
    // Horizontal rules
    .replace(/^---$/gim, '<hr>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    // Lists
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>');

  // Wrap in paragraphs
  html = '<p>' + html + '</p>';

  // Clean up
  html = html.replace(/<p><h/g, '<h').replace(/<\/h([123])><\/p>/g, '</h$1>');
  html = html.replace(/<p><hr><\/p>/g, '<hr>');
  html = html.replace(/<p>(<li>.*<\/li>)<\/p>/g, '<ul>$1</ul>');

  return html;
}

/**
 * Sanitize filename for download
 */
function sanitizeFilename(url: string): string {
  return url
    .replace(/^https?:\/\//, '')
    .replace(/[^a-z0-9]/gi, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .toLowerCase()
    .slice(0, 50);
}

// ============================================================================
// Week 4: Competitor Comparison Export Functions
// ============================================================================

import { ComparisonResults } from './api';

/**
 * Generate Markdown report from comparison results
 */
export function generateComparisonMarkdownReport(results: ComparisonResults): string {
  const date = new Date(results.analysis_date);
  const formattedDate = date.toLocaleDateString();
  const formattedTime = date.toLocaleTimeString();

  const md = `# Competitor Comparison Report

**Your Website:** ${results.user_site.url}
**Analysis Date:** ${formattedDate} at ${formattedTime}
**Comparison ID:** ${results.comparison_id}
**Sites Analyzed:** ${results.sites_analyzed}

---

## 📊 Competitive Rankings

| Rank | Website | Total Score |
|------|---------|-------------|
${results.comparison.rankings.map(r =>
  `| ${r.rank} | ${r.url}${r.url === results.user_site.url ? ' **(YOUR SITE)**' : ''} | ${r.score} |`
).join('\n')}

### Your Performance
- **Your Rank:** #${results.comparison.user_rank} of ${results.comparison.total_sites}
- **Your Score:** ${results.comparison.user_score} points
- **Gap to #1:** ${results.comparison.score_gap_to_first} points
- **Highest Competitor:** ${results.comparison.highest_competitor_score} points
- **Average Competitor:** ${results.comparison.average_competitor_score.toFixed(1)} points

---

## 🎯 Competitive Gaps

${results.gaps.length > 0 ? results.gaps.map((gap, i) => `
### ${i + 1}. ${gap.issue} (**${gap.priority.toUpperCase()}** Priority)

- **Dimension:** ${gap.dimension}
- **Category:** ${gap.category}
- **Your Score:** ${gap.user_score}
- **Competitor Score:** ${gap.competitor_score} (${gap.competitor_url})
- **Gap:** ${gap.gap} points

`).join('\n') : '_No gaps identified - you\'re ahead of all competitors!_'}

---

## ⚡ Quick Wins vs Competitors

${results.quick_wins.length > 0 ? results.quick_wins.map((win, i) => `
### ${i + 1}. ${win.fix}

- **Description:** ${win.description}
- **Dimension:** ${win.dimension}
- **Impact:** +${win.impact} points
- **Effort:** ${win.effort}
- **Rank Improvement:** Up ${win.rank_improvement} position${win.rank_improvement > 1 ? 's' : ''}
${win.beats.length > 0 ? `- **Beats:** ${win.beats.join(', ')}` : ''}

`).join('\n') : '_No quick wins available at this time._'}

---

## 🚀 Competitive Strategy

${results.competitive_strategy.length > 0 ? results.competitive_strategy.map((action, i) => `
### ${i + 1}. ${action.action} (**${action.priority.toUpperCase()}** Priority)

**Description:** ${action.description}

- **Dimension:** ${action.dimension}
- **Impact:** +${action.impact} points
- **Effort:** ${action.effort}
- **Current Rank:** #${action.current_rank}
- **Potential Rank:** #${action.potential_rank}
${action.beats.length > 0 ? `- **Will Beat:** ${action.beats.join(', ')}` : ''}
- **Related Competitor:** ${action.related_competitor}

`).join('\n') : '_No strategic actions available._'}

---

## 📈 Detailed Score Breakdown

### Your Site: ${results.user_site.url}
**Total Score:** ${results.user_site.total_score} | **Rank:** #${results.user_site.rank}

### Competitors

${results.competitors.map(comp => `
#### ${comp.url}
**Total Score:** ${comp.total_score} | **Rank:** #${comp.rank}
`).join('\n')}

---

*Report generated by SERP-Master Competitor Analysis*
*Visit https://serp-master.com for more insights*
`;

  return md;
}

/**
 * Download comparison report as Markdown
 */
export function downloadComparisonMarkdown(results: ComparisonResults, filename?: string): void {
  const markdown = generateComparisonMarkdownReport(results);
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);

  const sanitizedName = filename || sanitizeFilename(results.user_site.url);
  const finalFilename = `comparison-${sanitizedName}-${new Date().toISOString().split('T')[0]}.md`;

  const link = document.createElement('a');
  link.href = url;
  link.download = finalFilename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Download comparison report as PDF
 */
export function downloadComparisonPDF(results: ComparisonResults, filename?: string): void {
  const markdown = generateComparisonMarkdownReport(results);

  // Create HTML content
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Competitor Comparison Report - ${results.user_site.url}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      line-height: 1.6;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 20px;
      color: #333;
    }
    h1 { color: #1a202c; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    h2 { color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 30px; }
    h3 { color: #4a5568; margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
    th { background-color: #f7fafc; font-weight: 600; }
    tr:hover { background-color: #f7fafc; }
    .priority-high { color: #e53e3e; font-weight: bold; }
    .priority-medium { color: #ed8936; font-weight: bold; }
    .priority-low { color: #48bb78; font-weight: bold; }
    ul { list-style-type: none; padding-left: 0; }
    li { padding: 5px 0; }
    strong { color: #2d3748; }
  </style>
</head>
<body>
${markdown
  .replace(/^# (.*)/gm, '<h1>$1</h1>')
  .replace(/^## (.*)/gm, '<h2>$1</h2>')
  .replace(/^### (.*)/gm, '<h3>$1</h3>')
  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  .replace(/\*(.*?)\*/g, '<em>$1</em>')
  .replace(/\n\n/g, '</p><p>')
  .replace(/^- (.*)/gm, '<li>$1</li>')
  .replace(/\|(.+)\|/g, (match, p1) => {
    const cells = p1.split('|').map((c: string) => c.trim());
    return '<tr>' + cells.map((c: string) => '<td>' + c + '</td>').join('') + '</tr>';
  })}
</body>
</html>
  `;

  const blob = new Blob([htmlContent], { type: 'text/html' });
  const url = URL.createObjectURL(blob);

  const sanitizedName = filename || sanitizeFilename(results.user_site.url);
  const finalFilename = `comparison-${sanitizedName}-${new Date().toISOString().split('T')[0]}.pdf`;

  const link = document.createElement('a');
  link.href = url;
  link.download = finalFilename;
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  // Note: For true PDF, would need jsPDF or similar library
  // This creates an HTML file that can be saved as PDF via browser print
  setTimeout(() => {
    alert('Click Print (Ctrl+P) and select "Save as PDF" to create the PDF file.');
  }, 500);
}
