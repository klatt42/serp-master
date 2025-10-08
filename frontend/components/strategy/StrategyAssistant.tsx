/**
 * Strategy Assistant with CopilotKit
 * AI assistant for content strategy guidance
 */

'use client';

import React from 'react';
import { useCopilotAction, useCopilotReadable } from '@copilotkit/react-core';
import { CopilotChat } from '@copilotkit/react-ui';
import { ContentStrategy, ContentItem, ContentPillar } from '@/types/strategy';

interface StrategyAssistantProps {
  strategy?: ContentStrategy;
  onUpdateStrategy?: (updates: Partial<ContentStrategy>) => void;
}

export default function StrategyAssistant({ strategy, onUpdateStrategy }: StrategyAssistantProps) {
  // Make strategy data readable by the AI
  useCopilotReadable({
    description: 'The current content strategy data',
    value: strategy ? {
      seed_keyword: strategy.seed_keyword,
      total_pieces: strategy.total_pieces,
      timeline_weeks: strategy.timeline_weeks,
      pillars: strategy.pillars.map(p => ({
        name: p.name,
        description: p.description,
        keywords: p.keywords,
        priority: p.priority
      })),
      quick_wins: strategy.quick_wins,
      implementation_notes: strategy.implementation_notes
    } : null
  });

  // Action: Suggest content optimizations
  useCopilotAction({
    name: 'suggestOptimizations',
    description: 'Suggest optimizations for content items based on SEO best practices',
    parameters: [
      {
        name: 'itemId',
        type: 'string',
        description: 'The ID of the content item to optimize',
        required: true
      }
    ],
    handler: async ({ itemId }) => {
      const item = strategy?.content_items.find(i => i.id === itemId);
      if (!item) return 'Content item not found';

      return `Optimization suggestions for "${item.title}":

1. **Keyword Optimization**: Target "${item.target_keyword}" in:
   - Title (H1)
   - First paragraph
   - At least 2 subheadings
   - Meta description

2. **Content Structure**:
   - Recommended length: ${item.estimated_difficulty === 'easy' ? '1000-1500' : item.estimated_difficulty === 'medium' ? '1500-2500' : '2500+'} words
   - Include ${item.content_type === 'guide' ? '8-12' : '5-8'} sections
   - Add visual elements (images, charts)

3. **SEO Elements**:
   - Internal links to related content
   - External links to authoritative sources
   - Schema markup for ${item.content_type}
   - Optimized images with alt text

4. **Supporting Keywords to Include**: ${item.supporting_keywords.join(', ')}`;
    }
  });

  // Action: Generate content brief
  useCopilotAction({
    name: 'generateContentBrief',
    description: 'Generate a detailed content brief for a specific content item',
    parameters: [
      {
        name: 'itemId',
        type: 'string',
        description: 'The ID of the content item',
        required: true
      }
    ],
    handler: async ({ itemId }) => {
      const item = strategy?.content_items.find(i => i.id === itemId);
      if (!item) return 'Content item not found';

      const pillar = strategy?.pillars.find(p => p.name === item.pillar_name);

      return `# Content Brief: ${item.title}

## Overview
- **Content Type**: ${item.content_type}
- **Target Keyword**: ${item.target_keyword}
- **Content Pillar**: ${item.pillar_name}
- **Priority**: ${item.priority}
- **Difficulty**: ${item.estimated_difficulty}
- **Estimated Time**: ${item.estimated_hours} hours
- **Publish Date**: ${new Date(item.scheduled_date).toLocaleDateString()}

## Objectives
${pillar ? pillar.description : 'Support the content strategy goals'}

## Target Keywords
- Primary: ${item.target_keyword}
- Secondary: ${item.supporting_keywords.join(', ')}

## Optimization Tips
${item.optimization_tips.map(tip => `- ${tip}`).join('\n')}

## Recommended Outline
1. Introduction (addressing search intent)
2. Main Content Sections (3-5 sections)
3. Practical Examples/Case Studies
4. Key Takeaways
5. Call to Action

## Success Metrics
- Target ranking: Top 10 for "${item.target_keyword}"
- Estimated traffic: Based on keyword volume
- Engagement: Time on page > 3 minutes
- Conversions: Track relevant actions`;
    }
  });

  // Action: Analyze content gaps
  useCopilotAction({
    name: 'analyzeContentGaps',
    description: 'Analyze content gaps in the current strategy',
    parameters: [],
    handler: async () => {
      if (!strategy) return 'No strategy available';

      const pillarCoverage = strategy.pillars.map(pillar => {
        const itemCount = strategy.content_items.filter(i => i.pillar_name === pillar.name).length;
        return { name: pillar.name, itemCount };
      });

      const underservedPillars = pillarCoverage.filter(p => p.itemCount < 3);

      return `Content Gap Analysis:

**Pillar Coverage:**
${pillarCoverage.map(p => `- ${p.name}: ${p.itemCount} pieces`).join('\n')}

${underservedPillars.length > 0 ? `
**Underserved Pillars** (< 3 pieces):
${underservedPillars.map(p => `- ${p.name}: Add ${3 - p.itemCount} more pieces`).join('\n')}

**Recommendations:**
Focus on creating more content for underserved pillars to establish topical authority.
` : '**All pillars are well-covered!**'}

**Quick Wins:**
${strategy.quick_wins.map(w => `- ${w}`).join('\n')}`;
    }
  });

  // Action: Suggest content calendar adjustments
  useCopilotAction({
    name: 'suggestCalendarAdjustments',
    description: 'Suggest adjustments to the content calendar for better distribution',
    parameters: [],
    handler: async () => {
      if (!strategy) return 'No strategy available';

      // Group items by week
      const itemsByWeek = new Map<number, number>();
      const baseDate = new Date(strategy.content_items[0]?.scheduled_date);

      strategy.content_items.forEach(item => {
        const weekNum = Math.floor(
          (new Date(item.scheduled_date).getTime() - baseDate.getTime()) / (7 * 24 * 60 * 60 * 1000)
        ) + 1;
        itemsByWeek.set(weekNum, (itemsByWeek.get(weekNum) || 0) + 1);
      });

      const overloadedWeeks = Array.from(itemsByWeek.entries()).filter(([_, count]) => count > 3);

      return `Calendar Analysis:

**Total Content Pieces**: ${strategy.total_pieces}
**Timeline**: ${strategy.timeline_weeks} weeks
**Average per Week**: ${(strategy.total_pieces / strategy.timeline_weeks).toFixed(1)}

${overloadedWeeks.length > 0 ? `
**Overloaded Weeks** (>3 pieces):
${overloadedWeeks.map(([week, count]) => `- Week ${week}: ${count} pieces`).join('\n')}

**Recommendation**: Redistribute content to maintain 2-3 pieces per week for consistent output.
` : '**Calendar is well-balanced!**'}

**Best Practices**:
- Start with quick wins in Week 1-2
- Maintain consistent publishing schedule
- Allow time for promotion and optimization`;
    }
  });

  return (
    <div className="h-full">
      <CopilotChat
        labels={{
          title: 'Content Strategy Assistant',
          initial: strategy
            ? `Hi! I'm your content strategy assistant. I can help you with:

• Optimize content items for SEO
• Generate detailed content briefs
• Analyze content gaps
• Suggest calendar adjustments

Ask me anything about your strategy for "${strategy.seed_keyword}"!`
            : 'Generate a content strategy first to get personalized assistance.'
        }}
        className="h-full"
      />
    </div>
  );
}
