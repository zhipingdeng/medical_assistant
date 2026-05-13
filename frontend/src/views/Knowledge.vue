<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 标题和搜索 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">知识图谱</h1>
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="输入疾病名称，查看其知识图谱..."
              class="input"
              @keyup.enter="handleSearch"
            />
          </div>
          <div class="flex gap-2">
            <select v-model="depth" class="input w-32">
              <option :value="1">深度 1</option>
              <option :value="2">深度 2</option>
              <option :value="3">深度 3</option>
            </select>
            <button @click="handleSearch" class="btn-primary" :disabled="!searchQuery.trim() || loading">
              <span v-if="!loading">查询</span>
              <div v-else class="loading-spinner w-5 h-5"></div>
            </button>
          </div>
        </div>
      </div>

      <!-- 热门节点 -->
      <div class="mb-6">
        <h3 class="text-sm font-medium text-gray-500 mb-3">热门节点</h3>
        <div class="flex flex-wrap gap-2">
          <button v-for="node in hotNodes" :key="node"
                  @click="searchNode(node)"
                  class="px-4 py-2 bg-white rounded-full text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-all shadow-sm">
            {{ node }}
          </button>
        </div>
      </div>

      <!-- 图谱容器 - 始终存在，使用 id 而非 ref -->
      <div class="card p-4" style="height: 600px; position: relative;">
        <div v-if="loading" class="flex items-center justify-center h-full">
          <div class="text-center">
            <div class="loading-spinner w-12 h-12 mx-auto mb-4"></div>
            <p class="text-gray-500">正在加载知识图谱...</p>
          </div>
        </div>
        
        <div v-show="!loading && hasData" id="graph-container" style="width: 100%; height: 100%;"></div>
        
        <div v-show="!loading && !hasData" class="flex items-center justify-center h-full text-center">
          <div>
            <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <p class="text-gray-500 text-lg">输入疾病名称查看知识图谱</p>
            <p class="text-gray-400 text-sm mt-2">探索疾病、症状、药物之间的关联关系</p>
          </div>
        </div>
      </div>

      <!-- 图例 -->
      <div v-if="hasData" class="mt-4 card p-4">
        <h3 class="text-sm font-medium text-gray-500 mb-3">图例</h3>
        <div class="flex flex-wrap gap-4">
          <div v-for="(color, type) in nodeColors" :key="type" class="flex items-center">
            <div class="w-4 h-4 rounded-full mr-2" :style="{ backgroundColor: color }"></div>
            <span class="text-sm text-gray-700">{{ nodeLabels[type] || type }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { knowledgeApi } from '@/api/knowledge'
import * as d3 from 'd3'

interface GraphNode {
  id: string
  name: string
  label: string
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

interface GraphEdge {
  source: string | GraphNode
  target: string | GraphNode
  type?: string
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

const searchQuery = ref('')
const depth = ref(2)
const loading = ref(false)
const hasData = ref(false)
let graphData: GraphData | null = null

const hotNodes = ['感冒', '高血压', '糖尿病', '肺炎', '冠心病', '胃炎']

const nodeColors: Record<string, string> = {
  'Disease': '#3B82F6',
  'Symptom': '#EF4444',
  'Department': '#10B981',
  'Drug': '#8B5CF6',
  'Check': '#F59E0B'
}

const nodeLabels: Record<string, string> = {
  'Disease': '疾病',
  'Symptom': '症状',
  'Department': '科室',
  'Drug': '药物',
  'Check': '检查'
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    fetchGraph(searchQuery.value)
  }
}

const searchNode = (node: string) => {
  searchQuery.value = node
  fetchGraph(node)
}

const fetchGraph = async (center: string) => {
  loading.value = true
  hasData.value = false
  try {
    const data = await knowledgeApi.getGraph(center, depth.value)
    graphData = data
    if (data && data.nodes && data.nodes.length > 0) {
      hasData.value = true
      // Wait for DOM to update, then render
      await nextTick()
      // Use requestAnimationFrame to ensure DOM is painted
      requestAnimationFrame(() => {
        renderGraph()
      })
    }
  } catch (error) {
    console.error('Failed to fetch graph:', error)
    graphData = null
    hasData.value = false
  } finally {
    loading.value = false
  }
}

const renderGraph = () => {
  const container = document.getElementById('graph-container')
  if (!container || !graphData) {
    console.warn('renderGraph: container or data not ready', { container, graphData })
    return
  }
  
  // Clear container
  container.innerHTML = ''
  
  const width = container.clientWidth || 800
  const height = container.clientHeight || 500
  
  console.log('Rendering graph:', { width, height, nodes: graphData.nodes.length, edges: graphData.edges.length })
  
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .style('background', '#fafafa')
    .style('border-radius', '8px')
  
  const { nodes, edges } = graphData
  
  // Create simulation
  const simulation = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(edges as any).id((d: any) => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(40))
  
  // Draw edges
  const link = svg.append('g')
    .selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('stroke', '#CBD5E1')
    .attr('stroke-width', 2)
    .attr('stroke-opacity', 0.6)
  
  // Edge labels
  const linkLabel = svg.append('g')
    .selectAll('text')
    .data(edges)
    .enter()
    .append('text')
    .text((d: any) => d.type || '')
    .attr('font-size', '10px')
    .attr('fill', '#94A3B8')
    .attr('text-anchor', 'middle')
  
  // Create node groups
  const node = svg.append('g')
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .style('cursor', 'pointer')
    .call(d3.drag<any, any>()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended) as any)
  
  // Node circles
  node.append('circle')
    .attr('r', 24)
    .attr('fill', (d: any) => nodeColors[d.label] || '#6B7280')
    .attr('stroke', '#fff')
    .attr('stroke-width', 3)
    .on('mouseover', function(this: SVGCircleElement) {
      d3.select(this).transition().duration(200).attr('r', 30)
    })
    .on('mouseout', function(this: SVGCircleElement) {
      d3.select(this).transition().duration(200).attr('r', 24)
    })
  
  // Node labels (name inside circle)
  node.append('text')
    .text((d: any) => d.name.length > 4 ? d.name.substring(0, 4) + '..' : d.name)
    .attr('text-anchor', 'middle')
    .attr('dy', 4)
    .attr('font-size', '11px')
    .attr('font-weight', 'bold')
    .attr('fill', '#fff')
    .style('pointer-events', 'none')
  
  // Tooltip (full name below circle)
  node.append('title')
    .text((d: any) => `${d.name} (${nodeLabels[d.label] || d.label})`)
  
  // Update positions on tick
  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y)
    
    linkLabel
      .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
      .attr('y', (d: any) => (d.source.y + d.target.y) / 2)
    
    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
  })
  
  // Drag functions
  function dragstarted(event: any, d: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    d.fx = d.x
    d.fy = d.y
  }
  
  function dragged(event: any, d: any) {
    d.fx = event.x
    d.fy = event.y
  }
  
  function dragended(event: any, d: any) {
    if (!event.active) simulation.alphaTarget(0)
    d.fx = null
    d.fy = null
  }
  
  console.log('Graph rendered successfully')
}
</script>
