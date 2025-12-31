<template>
  <div class="admin-page">
    <!-- Chart Section -->
    <section class="chart-section">
      <div class="container">
        <h2>Access Analytics</h2>
        <div class="charts-grid">
          <div class="chart-container">
            <h3>Statistics Overview</h3>
            <div ref="chartRef" class="chart"></div>
          </div>
          <div class="chart-container">
            <h3>Activity Timeline</h3>
            <div ref="timelineChartRef" class="chart"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Logs Section -->
    <section class="logs-section">
      <div class="container">
        <h2>Recent Logs</h2>

        <div v-if="isLoading" class="loading-placeholder">
          <span>Loading logs...</span>
        </div>

        <div v-else-if="logs.length > 0" class="logs-list">
          <div
            v-for="log in logs"
            :key="log.id"
            class="log-item"
          >
            <div class="log-content">
              <div class="log-info">
                <span class="log-user">{{ log.username }}</span>
                <span class="log-action">{{ log.action }}</span>
              </div>
              <div class="log-time">{{ formatDateTime(log.created_at) }}</div>
            </div>
          </div>
        </div>

        <div v-else class="no-data">
          <span>No logs found</span>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMoreLogs && logs.length > 0" class="load-more-container">
          <button
            class="load-more-btn"
            @click="loadMoreLogs"
            :disabled="loadingMore"
            :class="{ loading: loadingMore }"
          >
            {{ loadingMore ? 'Loading...' : 'Load More Logs' }}
          </button>
        </div>
      </div>
    </section>
  </div>

  <!-- Toast Component -->
  <Toast />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { getRecentLogs, getLogsStats } from '@/api/admin.js'
import Toast from '@/components/Toast.vue'
import * as echarts from 'echarts'

const authStore = useAuthStore()
const router = useRouter()

// Chart refs
const chartRef = ref(null)
const timelineChartRef = ref(null)
let chartInstance = null
let timelineChartInstance = null

// Data state
const logs = ref([])
const isLoading = ref(false)
const loadingMore = ref(false)
const hasMoreLogs = ref(true)
const currentPage = ref(0)
const pageSize = 50

// Stats data for chart
const statsData = ref({
  today: 0,
  week: 0,
  month: 0,
  year: 0
})

// Initialize chart
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const option = {
    title: {
      text: 'Access Statistics',
      left: 'center',
      textStyle: {
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1a1a',
      borderColor: '#333333',
      textStyle: {
        color: '#ffffff'
      }
    },
    legend: {
      data: ['Access Count'],
      textStyle: {
        color: '#cccccc'
      },
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['Today', 'This Week', 'This Month', 'This Year'],
      axisLine: {
        lineStyle: {
          color: '#555555'
        }
      },
      axisLabel: {
        color: '#cccccc'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#555555'
        }
      },
      axisLabel: {
        color: '#cccccc'
      },
      splitLine: {
        lineStyle: {
          color: '#333333'
        }
      }
    },
    series: [{
      name: 'Access Count',
      type: 'bar',
      data: [statsData.value.today, statsData.value.week, statsData.value.month, statsData.value.year],
      itemStyle: {
        color: '#3552b0'
      },
      emphasis: {
        itemStyle: {
          color: '#f5c518'
        }
      }
    }]
  }

  chartInstance.setOption(option)
}

// Update chart data
const updateChart = () => {
  if (chartInstance) {
    chartInstance.setOption({
      series: [{
        data: [statsData.value.today, statsData.value.week, statsData.value.month, statsData.value.year]
      }]
    })
  }
}

// Initialize timeline chart
const initTimelineChart = () => {
  if (!timelineChartRef.value) return

  timelineChartInstance = echarts.init(timelineChartRef.value)

  const option = {
    title: {
      text: 'Activity Over Time',
      left: 'center',
      textStyle: {
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1a1a',
      borderColor: '#333333',
      textStyle: {
        color: '#ffffff'
      },
      formatter: function (params) {
        const date = params[0].name
        const count = params[0].value
        return `${date}<br/>Logs: ${count}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLine: {
        lineStyle: {
          color: '#555555'
        }
      },
      axisLabel: {
        color: '#cccccc',
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#555555'
        }
      },
      axisLabel: {
        color: '#cccccc'
      },
      splitLine: {
        lineStyle: {
          color: '#333333'
        }
      }
    },
    series: [{
      name: 'Activity',
      type: 'line',
      data: [],
      smooth: true,
      itemStyle: {
        color: '#f5c518'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(245, 197, 24, 0.3)'
          }, {
            offset: 1, color: 'rgba(245, 197, 24, 0.05)'
          }]
        }
      },
      emphasis: {
        itemStyle: {
          color: '#f5c518'
        }
      }
    }]
  }

  timelineChartInstance.setOption(option)
}

// Update timeline chart with logs data
const updateTimelineChart = (logs) => {
  if (!timelineChartInstance || !logs.length) return

  // Group logs by hour of day (0-23)
  const hourMap = new Map()

  logs.forEach(log => {
    const date = new Date(log.created_at)
    const hour = date.getHours() // 0-23
    hourMap.set(hour, (hourMap.get(hour) || 0) + 1)
  })

  // Create hour labels and data arrays (0 to 23)
  const hourLabels = Array.from({length: 24}, (_, i) => `${i}`)
  const data = hourLabels.map((_, index) => hourMap.get(index) || 0)

  timelineChartInstance.setOption({
    xAxis: {
      data: hourLabels
    },
    series: [{
      data: data
    }]
  })
}

// Load logs
const loadLogs = async (reset = false) => {
  try {
    if (reset) {
      isLoading.value = true
      currentPage.value = 0
    } else {
      loadingMore.value = true
    }

    const params = {
      page: currentPage.value + 1,
      per_page: pageSize
    }

    const response = await getRecentLogs(params)

    if (response.code === 1 && response.data) {
      if (reset) {
        logs.value = response.data.logs || []
      } else {
        logs.value.push(...(response.data.logs || []))
      }

      hasMoreLogs.value = (response.data.logs || []).length === pageSize
      currentPage.value = response.data.current_page || 1

      // Update timeline chart with current logs data
      if (reset) {
        updateTimelineChart(logs.value)
      }
    } else {
      if (reset) {
        logs.value = []
      }
      hasMoreLogs.value = false
    }
  } catch (error) {
    console.error('Failed to load logs:', error)
    if (reset) {
      logs.value = []
    }
    hasMoreLogs.value = false
  } finally {
    isLoading.value = false
    loadingMore.value = false
  }
}

const loadMoreLogs = () => {
  if (!hasMoreLogs.value || loadingMore.value) return
  loadLogs(false)
}

// Load stats for chart
const loadStats = async () => {
  try {
    const response = await getLogsStats()
    if (response.code === 1 && response.data) {
      statsData.value = {
        today: response.data.today || 0,
        week: response.data.week || 0,
        month: response.data.month || 0,
        year: response.data.year || 0
      }
      updateChart()
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// Format datetime
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Handle window resize for chart
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// Check admin access on mount
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  if (authStore.username !== 'admin') {
    router.push('/')
    return
  }

  // Load stats and initialize charts
  await loadStats()
  initChart()
  initTimelineChart()

  // Load logs
  await loadLogs(true)

  // Add resize listener
  window.addEventListener('resize', handleResize)
})

// Cleanup on unmount
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  if (timelineChartInstance) {
    timelineChartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* Chart Section */
.chart-section {
  background-color: #000000;
  padding: 2rem;
}

.chart-section h2 {
  color: #ffffff;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.chart-container {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 600px;
}

.chart-container h3 {
  color: #ffffff;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 350px;
}

/* Logs Section */
.logs-section {
  padding: 3rem 2rem;
}

.logs-section h2 {
  color: #ffffff;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 3rem;
}

.log-item {
  background-color: #1a1a1a;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #333333;
  transition: background-color 0.3s ease;
}

.log-item:hover {
  background-color: #232323;
}

.log-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.log-user {
  color: #f5c518;
  font-weight: 600;
  font-size: 1rem;
}

.log-action {
  color: #cccccc;
  font-size: 0.9rem;
}

.log-time {
  color: #888888;
  font-size: 0.8rem;
  white-space: nowrap;
}

/* Load More Button */
.load-more-container {
  text-align: center;
  margin-top: 2rem;
  padding-bottom: 2rem;
}

.load-more-btn {
  background: #3552b0;
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease, opacity 0.3s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: #2a4193;
}

.load-more-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.load-more-btn.loading {
  background: #555;
}

/* Loading and Empty States */
.loading-placeholder, .no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem 2rem;
  color: #666666;
  font-size: 1.2rem;
  text-align: center;
}

.loading-placeholder {
  color: #f5c518;
}

.no-data {
  color: #cccccc;
}

/* Responsive Design */
@media (max-width: 768px) {
  .chart-section,
  .logs-section {
    padding: 1.5rem 1rem;
  }

  .charts-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .chart-container {
    padding: 1rem;
    max-width: none;
  }

  .chart {
    height: 280px;
  }

  .log-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .log-time {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .chart-section,
  .logs-section {
    padding: 1rem 0.5rem;
  }

  .loading-placeholder, .no-data {
    padding: 2rem 1rem;
    font-size: 1rem;
  }

  .log-item {
    padding: 0.75rem;
  }
}
</style>
