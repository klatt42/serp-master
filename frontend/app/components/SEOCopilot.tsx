"use client";

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { Issue } from "../lib/api";

interface Scores {
  total_score: number;
  max_score: number;
  percentage: number;
  grade: string;
  component_scores: {
    seo: { score: number; max: number; percentage: number };
    aeo: { score: number; max: number; percentage: number };
    geo: { score: number; max: number; percentage: number };
  };
}

interface SEOCopilotProps {
  auditResults: {
    url: string;
    timestamp: string;
    score: Scores;
    issues?: {
      critical: Issue[];
      warnings: Issue[];
      info: Issue[];
      quick_wins: Issue[];
    };
  };
}

export default function SEOCopilot({ auditResults }: SEOCopilotProps) {
  // Make audit results available to Copilot
  useCopilotReadable({
    description: "Current website audit results including scores and issues",
    value: auditResults,
  });

  // Provide scores context separately for easier access
  useCopilotReadable({
    description: "Overall SEO, AEO, and GEO scores",
    value: {
      overall: {
        score: auditResults.score.total_score,
        max: auditResults.score.max_score,
        percentage: auditResults.score.percentage,
        grade: auditResults.score.grade,
      },
      seo: auditResults.score.component_scores.seo,
      aeo: auditResults.score.component_scores.aeo,
      geo: auditResults.score.component_scores.geo,
    },
  });

  // Provide issues context
  useCopilotReadable({
    description: "All SEO issues found in the audit, categorized by severity",
    value: auditResults.issues ? {
      critical_count: auditResults.issues.critical?.length || 0,
      warning_count: auditResults.issues.warnings?.length || 0,
      info_count: auditResults.issues.info?.length || 0,
      quick_wins_count: auditResults.issues.quick_wins?.length || 0,
      all_issues: [
        ...(auditResults.issues.critical || []),
        ...(auditResults.issues.warnings || []),
        ...(auditResults.issues.info || []),
      ],
    } : {
      critical_count: 0,
      warning_count: 0,
      info_count: 0,
      quick_wins_count: 0,
      all_issues: [],
    },
  });

  // Action 1: Explain Score
  useCopilotAction({
    name: "explainScore",
    description:
      "Explain what a specific score dimension (SEO, AEO, or GEO) means and provide detailed improvement suggestions",
    parameters: [
      {
        name: "dimension",
        type: "string",
        description: "The score dimension to explain: 'seo', 'aeo', or 'geo'",
        required: true,
      },
      {
        name: "current_score",
        type: "number",
        description: "The current score value for this dimension",
        required: true,
      },
    ],
    handler: async ({ dimension, current_score }) => {
      const dimensionData = auditResults.score.component_scores[dimension as keyof typeof auditResults.score.component_scores];

      const explanations = {
        seo: {
          name: "Traditional SEO",
          description: "Traditional SEO measures technical fundamentals like meta tags, headings, URLs, mobile optimization, and site structure. These are the classic ranking factors search engines use.",
          max: 30,
          key_factors: [
            "Title tags and meta descriptions",
            "Heading hierarchy (H1, H2, etc.)",
            "URL structure and keywords",
            "Mobile responsiveness",
            "Page load speed",
            "XML sitemap and robots.txt",
            "Internal linking structure",
          ],
        },
        aeo: {
          name: "Answer Engine Optimization (AEO)",
          description: "AEO optimizes for AI systems like ChatGPT, Perplexity, and Google's AI Overviews. It focuses on structured data, question-answer content, and entity relationships that AI can easily parse and cite.",
          max: 25,
          key_factors: [
            "FAQ schema and structured data",
            "Question-based headings and content",
            "Entity clarity and relationships",
            "Authoritative sources and citations",
            "Clear, concise answers",
            "Topic clustering and depth",
          ],
        },
        geo: {
          name: "Generative Engine Optimization (GEO)",
          description: "GEO is about being cited by AI-generated results. This emerging field focuses on citation-worthy content, authoritative signals, and formats that AI models prefer to reference.",
          max: 45,
          key_factors: [
            "Citation-worthy statistics and data",
            "Expert quotes and interviews",
            "Original research and insights",
            "Clear attribution and sources",
            "Content freshness and relevance",
            "Brand authority signals",
          ],
        },
      };

      const info = explanations[dimension as keyof typeof explanations];
      const percentage = dimensionData ? dimensionData.percentage : 0;
      const max = dimensionData ? dimensionData.max : info.max;
      const missing_points = max - current_score;

      return `
## ${info.name} Score Explanation

**Current Score:** ${current_score} / ${max} (${percentage.toFixed(1)}%)

### What is ${info.name}?
${info.description}

### Key Factors Measured:
${info.key_factors.map((f) => `- ${f}`).join('\n')}

### Your Performance:
You're scoring ${current_score} out of ${max} possible points, which is ${percentage >= 80 ? 'excellent' : percentage >= 60 ? 'good but has room for improvement' : 'needs significant improvement'}.

You're missing **${missing_points} points** in this dimension.

### Improvement Strategy:
${percentage < 60 ? `
**Priority: HIGH** - This dimension needs immediate attention.

1. Review the Critical issues in the ${info.name} category
2. Focus on quick wins first to boost your score rapidly
3. Implement the fundamental factors listed above
4. Re-audit after fixes to measure improvement
` : percentage < 80 ? `
**Priority: MEDIUM** - You have a solid foundation, now optimize for excellence.

1. Address remaining Warning-level issues
2. Fine-tune existing implementations
3. Look for advanced optimization opportunities
4. Monitor competitors to stay ahead
` : `
**Priority: LOW** - You're doing great! Maintain and monitor.

1. Keep content fresh and updated
2. Monitor for new issues regularly
3. Stay informed about algorithm updates
4. Focus on other score dimensions if needed
`}

💡 **Pro Tip:** Check the Issues tab for specific, actionable items to improve this score.
      `.trim();
    },
  });

  // Action 2: Prioritize Issues
  useCopilotAction({
    name: "prioritizeIssues",
    description:
      "Analyze all issues and provide a prioritized action plan based on the user's goal (quick wins, maximum impact, or easy fixes)",
    parameters: [
      {
        name: "goal",
        type: "string",
        description: "Prioritization strategy: 'quick_wins' (high impact, low effort), 'max_impact' (highest impact regardless of effort), or 'easy_fixes' (lowest effort regardless of impact)",
        required: true,
      },
    ],
    handler: async ({ goal }) => {
      if (!auditResults.issues) {
        return "No issues found in the audit results. Your site is in excellent shape!";
      }

      const allIssues = [
        ...auditResults.issues.critical,
        ...auditResults.issues.warnings,
        ...auditResults.issues.info,
      ];

      if (allIssues.length === 0) {
        return "No issues found in the audit results. Your site is in excellent shape!";
      }

      let sortedIssues: Issue[];
      let strategy: string;
      let reasoning: string;

      switch (goal) {
        case "quick_wins":
          // High impact, low effort
          sortedIssues = [...allIssues]
            .filter((issue) => issue.quick_win)
            .sort((a, b) => {
              // Sort by impact (descending), then effort (ascending)
              if (b.impact !== a.impact) return b.impact - a.impact;
              const effortOrder = { low: 1, medium: 2, high: 3 };
              return effortOrder[a.effort] - effortOrder[b.effort];
            })
            .slice(0, 10);

          strategy = "Quick Wins Strategy";
          reasoning = "These issues give you the best ROI: high impact improvements with low time investment. Perfect for getting fast results.";
          break;

        case "max_impact":
          // Highest impact first
          sortedIssues = [...allIssues]
            .sort((a, b) => {
              // Sort by impact (descending), then severity
              if (b.impact !== a.impact) return b.impact - a.impact;
              const severityOrder = { CRITICAL: 3, WARNING: 2, INFO: 1 };
              return severityOrder[b.severity] - severityOrder[a.severity];
            })
            .slice(0, 10);

          strategy = "Maximum Impact Strategy";
          reasoning = "These issues will improve your score the most. Some may require significant effort, but the payoff is worth it.";
          break;

        case "easy_fixes":
          // Lowest effort first
          sortedIssues = [...allIssues]
            .sort((a, b) => {
              // Sort by effort (ascending), then impact (descending)
              const effortOrder = { low: 1, medium: 2, high: 3 };
              if (effortOrder[a.effort] !== effortOrder[b.effort]) {
                return effortOrder[a.effort] - effortOrder[b.effort];
              }
              return b.impact - a.impact;
            })
            .slice(0, 10);

          strategy = "Easy Fixes Strategy";
          reasoning = "These issues are the easiest to fix. Great for building momentum and checking items off your list quickly.";
          break;

        default:
          sortedIssues = allIssues.slice(0, 10);
          strategy = "General Priority";
          reasoning = "Issues sorted by default priority.";
      }

      const issueList = sortedIssues
        .map((issue, index) => {
          const effortEmoji = { low: "🟢", medium: "🟡", high: "🔴" };
          const severityEmoji = { CRITICAL: "🚨", WARNING: "⚠️", INFO: "ℹ️" };

          return `
### ${index + 1}. ${severityEmoji[issue.severity]} ${issue.title}

**Category:** ${issue.category} | **Impact:** +${issue.impact} points | **Effort:** ${effortEmoji[issue.effort]} ${issue.effort}
${issue.quick_win ? "⚡ **Quick Win**" : ""}

${issue.description}

**Why fix this:** ${issue.recommendation}

**Pages affected:** ${issue.pages_affected}
          `.trim();
        })
        .join("\n\n---\n\n");

      return `
# ${strategy}

${reasoning}

## Your Prioritized Action Plan

${issueList}

---

## Next Steps

1. **Start with #1** - Begin working on the highest priority issue
2. **Fix incrementally** - Don't try to fix everything at once
3. **Re-audit regularly** - Check your progress after implementing fixes
4. **Track improvements** - Note which changes moved the needle most

💡 **Tip:** Ask me for detailed fix instructions for any specific issue using "How do I fix [issue title]?"
      `.trim();
    },
  });

  // Action 3: Generate Fix Instructions
  useCopilotAction({
    name: "generateFixInstructions",
    description:
      "Generate detailed, step-by-step instructions to fix a specific SEO issue, tailored to the user's technical skill level",
    parameters: [
      {
        name: "issue_title",
        type: "string",
        description: "The title of the issue to fix",
        required: true,
      },
      {
        name: "technical_level",
        type: "string",
        description: "User's technical skill level: 'beginner', 'intermediate', or 'expert'",
        required: false,
      },
    ],
    handler: async ({ issue_title, technical_level = "intermediate" }) => {
      if (!auditResults.issues) {
        return "No issues found in the audit results.";
      }

      const allIssues = [
        ...auditResults.issues.critical,
        ...auditResults.issues.warnings,
        ...auditResults.issues.info,
      ];

      // Find the issue by title (case-insensitive partial match)
      const issue = allIssues.find((i) =>
        i.title.toLowerCase().includes(issue_title.toLowerCase())
      );

      if (!issue) {
        return `I couldn't find an issue matching "${issue_title}". Please check the issue title and try again.

Available issues:
${allIssues.map((i) => `- ${i.title}`).join('\n')}`;
      }

      const effortEmoji = { low: "🟢", medium: "🟡", high: "🔴" };
      const severityEmoji = { CRITICAL: "🚨", WARNING: "⚠️", INFO: "ℹ️" };

      let instructions = `
# Fix Instructions: ${issue.title}

${severityEmoji[issue.severity]} **Severity:** ${issue.severity} | ${effortEmoji[issue.effort]} **Effort:** ${issue.effort} | **Impact:** +${issue.impact} points

## Problem

${issue.description}

## Why This Matters

${issue.recommendation}

## Step-by-Step Fix (${technical_level} level)

      `.trim();

      // Add detailed steps if available
      if (issue.details?.fix_steps && issue.details.fix_steps.length > 0) {
        instructions += "\n\n" + issue.details.fix_steps
          .map((step, index) => `${index + 1}. ${step}`)
          .join('\n');
      } else {
        // Generate generic steps based on technical level
        if (technical_level === "beginner") {
          instructions += `

1. **Understand the issue:** Read the description above carefully
2. **Find affected pages:** Check the ${issue.pages_affected} page(s) that need this fix
3. **Access your website editor:** Log into your CMS (WordPress, Shopify, etc.)
4. **Make the changes:** Follow the recommendation provided
5. **Save and publish:** Don't forget to save your changes
6. **Verify the fix:** Check the live page to ensure changes appear correctly
7. **Re-audit:** Run a new audit to confirm the issue is resolved

💡 **Need help?** Consider hiring a developer if you're unsure about any step.
          `.trim();
        } else if (technical_level === "intermediate") {
          instructions += `

1. Identify the ${issue.pages_affected} affected page(s)
2. Access your page templates or individual pages
3. Implement the fix according to the recommendation
4. Test changes in a staging environment if available
5. Deploy to production
6. Validate using browser dev tools or SEO tools
7. Re-audit to confirm resolution

**Estimated time:** ${issue.effort === 'low' ? '15-30 minutes' : issue.effort === 'medium' ? '1-2 hours' : '3+ hours'}
          `.trim();
        } else {
          // expert
          instructions += `

1. Audit scope: ${issue.pages_affected} page(s)
2. Root cause analysis: ${issue.category} optimization
3. Implementation approach: ${issue.recommendation}
4. Testing: Automated + manual validation
5. Deployment: CI/CD pipeline or direct deployment
6. Monitoring: Track score improvement and search visibility

**Technical context:** ${issue.category} optimization, ${issue.severity} priority
          `.trim();
        }
      }

      // Add code example if available
      if (issue.details?.code_example) {
        instructions += `

## Code Example

\`\`\`
${issue.details.code_example}
\`\`\`
        `.trim();
      }

      // Add explanation if available
      if (issue.details?.explanation) {
        instructions += `

## Additional Context

${issue.details.explanation}
        `.trim();
      }

      instructions += `

---

**Pages affected:** ${issue.pages_affected}
**Category:** ${issue.category}
**Expected improvement:** +${issue.impact} points

✅ After implementing this fix, run a new audit to verify the improvement!
      `.trim();

      return instructions;
    },
  });

  // Action 4: Compare to Competitors
  useCopilotAction({
    name: "compareToCompetitors",
    description:
      "Analyze how your SEO scores compare to competitors and provide a strategic catch-up plan",
    parameters: [
      {
        name: "competitor_scores",
        type: "object",
        description: "Array of competitor scores to compare against",
        required: false,
      },
    ],
    handler: async ({ competitor_scores }) => {
      const yourScore = auditResults.score;

      // If no competitor data provided, give general competitive analysis
      if (!competitor_scores || !Array.isArray(competitor_scores) || competitor_scores.length === 0) {
        return `
# Competitive Analysis: ${auditResults.url}

## Your Current Position

**Overall Score:** ${yourScore.total_score} / ${yourScore.max_score} (${yourScore.percentage.toFixed(1)}%)
**Grade:** ${yourScore.grade}

### Score Breakdown

- **Traditional SEO:** ${yourScore.component_scores.seo.score}/${yourScore.component_scores.seo.max} (${yourScore.component_scores.seo.percentage.toFixed(1)}%)
- **AEO (Answer Engine Optimization):** ${yourScore.component_scores.aeo.score}/${yourScore.component_scores.aeo.max} (${yourScore.component_scores.aeo.percentage.toFixed(1)}%)
- **GEO (Generative Engine Optimization):** ${yourScore.component_scores.geo.score}/${yourScore.component_scores.geo.max} (${yourScore.component_scores.geo.percentage.toFixed(1)}%)

## Competitive Positioning

${yourScore.percentage >= 80 ? `
🏆 **You're in the top tier!** Your score of ${yourScore.percentage.toFixed(1)}% puts you in an excellent competitive position.

**Strengths:**
- Strong foundation across all dimensions
- Well-optimized for both traditional and AI search
- Likely outperforming most competitors

**Strategy:** Focus on maintaining excellence and staying ahead of algorithm updates.
` : yourScore.percentage >= 60 ? `
📊 **You're competitive but have room to grow.** At ${yourScore.percentage.toFixed(1)}%, you're likely in the middle of the pack.

**Opportunity:**
- Fix critical issues to jump ahead of competitors
- Focus on AEO/GEO to differentiate (many competitors ignore this)
- Quick wins can rapidly improve your position

**Strategy:** Implement high-impact fixes to break into the top tier.
` : `
⚠️ **You're falling behind competitors.** At ${yourScore.percentage.toFixed(1)}%, you need immediate action.

**Critical gaps:**
- ${yourScore.component_scores.seo.percentage < 60 ? 'Traditional SEO fundamentals need work' : ''}
- ${yourScore.component_scores.aeo.percentage < 60 ? 'AEO optimization is lacking' : ''}
- ${yourScore.component_scores.geo.percentage < 60 ? 'GEO preparation is minimal' : ''}

**Strategy:** Focus on critical issues first, then quick wins for rapid improvement.
`}

## Recommended Competitive Actions

1. **Analyze top competitors** - Run audits on 3-5 direct competitors
2. **Identify gaps** - Compare your scores dimension by dimension
3. **Prioritize differentiation** - Focus on AEO/GEO where competitors are weak
4. **Monitor regularly** - Track changes in competitor performance
5. **Leverage quick wins** - Get fast improvements to close gaps

💡 **Tip:** To compare against specific competitors, provide their audit scores and I'll give you a detailed head-to-head analysis.
        `.trim();
      }

      // Detailed competitor comparison
      const competitors = competitor_scores as Array<{ name: string; score: Scores }>;
      const avgCompetitorScore = competitors.reduce((sum, c) => sum + c.score.percentage, 0) / competitors.length;
      const yourRank = competitors.filter((c) => c.score.total_score > yourScore.total_score).length + 1;
      const totalCompetitors = competitors.length + 1;

      return `
# Competitive Analysis: ${auditResults.url}

## Your Ranking

**Position:** #${yourRank} out of ${totalCompetitors} sites analyzed
**Your Score:** ${yourScore.total_score}/${yourScore.max_score} (${yourScore.percentage.toFixed(1)}%)
**Grade:** ${yourScore.grade}
**Competitor Average:** ${avgCompetitorScore.toFixed(1)}%
**Gap:** ${yourScore.percentage > avgCompetitorScore ? '+' : ''}${(yourScore.percentage - avgCompetitorScore).toFixed(1)}%

## Head-to-Head Comparison

| Site | Overall | SEO | AEO | GEO | Grade |
|------|---------|-----|-----|-----|-------|
| **You** | **${yourScore.percentage.toFixed(1)}%** | **${yourScore.component_scores.seo.percentage.toFixed(1)}%** | **${yourScore.component_scores.aeo.percentage.toFixed(1)}%** | **${yourScore.component_scores.geo.percentage.toFixed(1)}%** | **${yourScore.grade}** |
${competitors.map((c) => `| ${c.name} | ${c.score.percentage.toFixed(1)}% | ${c.score.component_scores.seo.percentage.toFixed(1)}% | ${c.score.component_scores.aeo.percentage.toFixed(1)}% | ${c.score.component_scores.geo.percentage.toFixed(1)}% | ${c.score.grade} |`).join('\n')}

## Competitive Insights

${yourRank === 1 ? `
🏆 **You're #1!** Congratulations, you're outperforming all analyzed competitors.

**Maintain your lead:**
- Keep monitoring competitor improvements
- Stay aggressive with SEO updates
- Don't let your guard down on AEO/GEO
` : `
📊 **Position #${yourRank}** - ${yourRank <= totalCompetitors / 2 ? 'Upper half' : 'Lower half'} of the pack

**To move up:**
${competitors
  .filter((c) => c.score.total_score > yourScore.total_score)
  .slice(0, 3)
  .map((c) => {
    const gap = c.score.total_score - yourScore.total_score;
    return `- **Beat ${c.name}:** Close ${gap}-point gap. Focus on ${
      c.score.component_scores.seo.score > yourScore.component_scores.seo.score ? 'SEO' :
      c.score.component_scores.aeo.score > yourScore.component_scores.aeo.score ? 'AEO' : 'GEO'
    }.`;
  })
  .join('\n')}
`}

## Strategic Recommendations

${
  yourScore.component_scores.aeo.percentage > avgCompetitorScore
    ? "✅ **AEO Advantage:** You're ahead on AI optimization - capitalize on this!"
    : "🎯 **AEO Opportunity:** Competitors are weak here. Big differentiation potential."
}

${
  yourScore.component_scores.seo.percentage > avgCompetitorScore
    ? "✅ **SEO Strength:** Your traditional SEO is strong - maintain it."
    : "⚠️ **SEO Gap:** Competitors are beating you on fundamentals. Priority fix."
}

${
  yourScore.component_scores.geo.percentage > avgCompetitorScore
    ? "✅ **GEO Leadership:** You're prepared for generative AI - rare advantage!"
    : "💡 **GEO Opportunity:** Most competitors aren't optimizing for this yet."
}

## Action Plan to Close Gaps

1. **Immediate** (This week): Fix ${auditResults.issues?.critical.length || 0} critical issues
2. **Short-term** (This month): Address ${auditResults.issues?.quick_wins.length || 0} quick wins
3. **Medium-term** (3 months): Close dimension gaps (focus on weakest area)
4. **Ongoing:** Monitor competitor changes monthly

💡 **Competitive Edge:** Focus on AEO/GEO where most competitors are still weak!
      `.trim();
    },
  });

  // This component doesn't render anything visible
  // It just registers actions and makes data available to CopilotKit
  return null;
}
