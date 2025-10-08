"use client";

import { KeywordCluster } from '@/types/cluster';
import { ClusterCard } from './ClusterCard';
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ClusterVisualizationProps {
  clusters: KeywordCluster[];
}

// Color palette for clusters
const CLUSTER_COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#06B6D4', // cyan
  '#F97316', // orange
  '#14B8A6', // teal
  '#6366F1', // indigo
];

export function ClusterVisualization({ clusters }: ClusterVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || clusters.length === 0) return;

    // Clear previous visualization
    d3.select(svgRef.current).selectAll('*').remove();

    const width = 800;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create bubble data
    const bubbleData = clusters.map((cluster, i) => ({
      id: cluster.cluster_id,
      name: cluster.cluster_name,
      value: cluster.total_search_volume,
      keywords: cluster.total_keywords,
      difficulty: cluster.avg_difficulty,
      color: CLUSTER_COLORS[i % CLUSTER_COLORS.length],
    }));

    // Create pack layout
    const pack = d3.pack()
      .size([width - margin.left - margin.right, height - margin.top - margin.bottom])
      .padding(10);

    const root = d3.hierarchy({ children: bubbleData } as any)
      .sum(d => (d as any).value);

    const nodes = pack(root).leaves();

    // Create bubbles
    const bubble = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('transform', d => `translate(${d.x},${d.y})`);

    // Add circles
    bubble.append('circle')
      .attr('r', d => d.r)
      .attr('fill', d => (d.data as any).color)
      .attr('fill-opacity', 0.6)
      .attr('stroke', d => (d.data as any).color)
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('mouseover', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('fill-opacity', 0.8);
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('fill-opacity', 0.6);
      });

    // Add text labels
    bubble.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '-0.3em')
      .style('font-size', d => `${Math.min(d.r / 4, 16)}px`)
      .style('font-weight', 'bold')
      .style('fill', 'white')
      .style('pointer-events', 'none')
      .text(d => (d.data as any).name);

    // Add keyword count
    bubble.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '1em')
      .style('font-size', d => `${Math.min(d.r / 5, 12)}px`)
      .style('fill', 'white')
      .style('pointer-events', 'none')
      .text(d => `${(d.data as any).keywords} keywords`);

  }, [clusters]);

  return (
    <div className="space-y-6">
      {/* Bubble Chart */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Cluster Map</h2>
        <p className="text-sm text-gray-600 mb-4">
          Bubble size represents total search volume. Click to explore keywords.
        </p>

        <div className="flex justify-center">
          <svg ref={svgRef} className="max-w-full"></svg>
        </div>
      </div>

      {/* Cluster Cards */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-gray-900">All Clusters</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {clusters.map((cluster, index) => (
            <ClusterCard
              key={cluster.cluster_id}
              cluster={cluster}
              color={CLUSTER_COLORS[index % CLUSTER_COLORS.length]}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
