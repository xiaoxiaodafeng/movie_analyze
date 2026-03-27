/**
 * 电影数据分析图表渲染模块
 */

// 图表颜色配置
const CHART_COLORS = {
    PIE: [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#C9CBCF', '#45B7D1', '#FF6B6B', '#4ECDC4',
        '#45B7D1', '#F9CA24', '#EB4D4B', '#686DE0', '#6AB04C'
    ],
    BAR: {
        REGIONS: '#36A2EB',
        YEARS: '#FF6384',
        GENRES: '#4BC0C0',
        DURATION_BUCKETS: '#FF9F40'
    },
    SCATTER: {
        POINTS: '#9966FF',
        TRENDLINE: '#FF6384',
        OUTLIERS: '#FFCE56',
        GENRE_RATINGS: '#F9CA24'
    }
};

/**
 * 初始化语言分布饼图
 */
function initLanguagesChart() {
    const canvas = document.getElementById('languagesChart');
    if (!canvas) {
        console.error('找不到languagesChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.languages;
    
    if (!chartData || !chartData.labels || !chartData.data) {
        console.error('语言分布数据不完整');
        return;
    }
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: CHART_COLORS.PIE
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((context.raw / total) * 100);
                            return `${context.label}: ${context.raw} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 初始化地区分布条形图
 */
function initRegionsChart() {
    const canvas = document.getElementById('regionsChart');
    if (!canvas) {
        console.error('找不到regionsChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.regions;
    
    if (!chartData || !chartData.labels || !chartData.data) {
        console.error('地区分布数据不完整');
        return;
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: '电影数量',
                data: chartData.data,
                backgroundColor: CHART_COLORS.BAR.REGIONS
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw} 部电影`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '电影数量'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '地区'
                    }
                }
            }
        }
    });
}

/**
 * 初始化年份分布柱形图
 */
function initYearsChart() {
    const canvas = document.getElementById('yearsChart');
    if (!canvas) {
        console.error('找不到yearsChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.years;
    
    if (!chartData || !chartData.labels || !chartData.data) {
        console.error('年份分布数据不完整');
        return;
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: '电影数量',
                data: chartData.data,
                backgroundColor: CHART_COLORS.BAR.YEARS
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}年: ${context.raw} 部电影`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '电影数量'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '年份'
                    }
                }
            }
        }
    });
}

/**
 * 初始化电影评分与电影时长关系散点图
 */
function initScoreDurationChart() {
    const canvas = document.getElementById('scoreDurationChart');
    if (!canvas) {
        console.error('找不到scoreDurationChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.scoreDuration;
    
    if (!chartData || !chartData.points) {
        console.error('评分与时长数据不完整');
        return;
    }
    
    // 准备数据集
    const datasets = [{
        label: '电影评分与时长',
        data: chartData.points,
        backgroundColor: CHART_COLORS.SCATTER.POINTS,
        hoverBackgroundColor: CHART_COLORS.SCATTER.POINTS,
        pointRadius: 5,
        pointHoverRadius: 7
    }];
    
    // 添加异常值数据集
    if (chartData.outliers && chartData.outliers.length > 0) {
        datasets.push({
            label: '异常值电影',
            data: chartData.outliers.map(outlier => ({
                x: outlier.duration,
                y: outlier.score,
                name: outlier.name
            })),
            backgroundColor: CHART_COLORS.SCATTER.OUTLIERS,
            hoverBackgroundColor: CHART_COLORS.SCATTER.OUTLIERS,
            pointRadius: 7,
            pointHoverRadius: 9
        });
    }
    
    // 添加趋势线数据集
    if (chartData.trendLine && chartData.trendLine.points) {
        datasets.push({
            label: '趋势线',
            data: chartData.trendLine.points,
            type: 'line',
            backgroundColor: 'transparent',
            borderColor: CHART_COLORS.SCATTER.TRENDLINE,
            borderWidth: 2,
            fill: false,
            tension: 0,
            pointRadius: 0,
            pointHoverRadius: 0
        });
    }
    
    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return `${point.name}: 时长 ${point.x} 分钟, 评分 ${point.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: '电影评分'
                    }
                },
                x: {
                    beginAtZero: true,
                    max: 600,
                    title: {
                        display: true,
                        text: '电影时长（分钟）'
                    }
                }
            }
        }
    });
}

/**
 * 初始化时长区间平均评分柱状图
 */
function initDurationBucketsChart() {
    const canvas = document.getElementById('durationBucketsChart');
    if (!canvas) {
        console.error('找不到durationBucketsChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.durationBuckets;
    
    if (!chartData || chartData.length === 0) {
        console.error('时长区间数据不完整');
        return;
    }
    
    // 处理数据
    const labels = chartData.map(bucket => bucket.bucket);
    const avgScores = chartData.map(bucket => bucket.avg_score);
    const counts = chartData.map(bucket => bucket.count);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '平均评分',
                data: avgScores,
                backgroundColor: CHART_COLORS.BAR.DURATION_BUCKETS,
                yAxisID: 'y'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            return `平均评分: ${context.raw}\n电影数量: ${counts[index]}部`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: '平均评分'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '电影时长区间'
                    }
                }
            }
        }
    });
}

/**
 * 初始化电影评分与电影类型关系柱状图
 */
function initGenresScoreChart() {
    const canvas = document.getElementById('genresScoreChart');
    if (!canvas) {
        console.error('找不到genresScoreChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.genresScore;
    
    if (!chartData || !chartData.labels || !chartData.avgScores || !chartData.counts) {
        console.error('评分与类型数据不完整');
        return;
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: '平均评分',
                data: chartData.avgScores,
                backgroundColor: CHART_COLORS.BAR.GENRES,
                yAxisID: 'y'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            return `${context.dataset.label}: ${context.raw}\n电影数量: ${chartData.counts[index]}部`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: '电影评分'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '电影类型'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

/**
 * 初始化特定类型电影评分分布散点图
 */
function initGenreRatingsChart() {
    const canvas = document.getElementById('genreRatingsChart');
    if (!canvas) {
        console.error('找不到genreRatingsChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.genreRatings;
    
    if (!chartData || !chartData.points) {
        console.error('类型评分数据不完整');
        return;
    }
    
    // 如果没有选择类型，显示提示信息
    const points = chartData.points;
    const selectedGenre = chartData.selectedGenre;
    
    let chartConfig = {
        type: 'scatter',
        data: {
            datasets: [{
                label: selectedGenre ? `${selectedGenre}电影评分分布` : '请选择电影类型',
                data: points,
                backgroundColor: CHART_COLORS.SCATTER.GENRE_RATINGS,
                hoverBackgroundColor: CHART_COLORS.SCATTER.GENRE_RATINGS,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return `${point.name}: 评分 ${point.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: '电影评分'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '电影索引'
                    }
                }
            }
        }
    };
    
    new Chart(ctx, chartConfig);
}

/**
 * 初始化单一图表（用于独立页面）
 * @param {string} type - 图表类型 (pie, bar, column)
 * @param {Array} labels - 图表标签
 * @param {Array} data - 图表数据
 */
function initSingleChart(type, labels, data) {
    const canvas = document.getElementById('movieChart');
    if (!canvas) {
        console.error('找不到movieChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const isPieChart = type === 'pie';
    
    const chartConfig = {
        type: isPieChart ? 'pie' : 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '电影数量',
                data: data,
                backgroundColor: isPieChart ? CHART_COLORS.PIE : CHART_COLORS.BAR.REGIONS
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: isPieChart ? 'bottom' : 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (isPieChart) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((context.raw / total) * 100);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                            return `${context.label}: ${context.raw} 部电影`;
                        }
                    }
                }
            }
        }
    };
    
    // 为条形图和柱形图添加坐标轴配置
    if (!isPieChart) {
        chartConfig.options.scales = {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: '电影数量'
                }
            },
            x: {
                title: {
                    display: true,
                    text: window.chartType === 'column' ? '年份' : '地区'
                }
            }
        };
    }
    
    new Chart(ctx, chartConfig);
}

/**
 * 页面加载完成后初始化所有图表
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('电影数据分析模块加载完成');
    
    // 检查是否在电影数据分析主页面
    if (document.getElementById('languagesChart') && 
        document.getElementById('regionsChart') && 
        document.getElementById('yearsChart') && 
        document.getElementById('scoreDurationChart') &&
        document.getElementById('genresScoreChart') &&
        document.getElementById('genreRatingsChart')) {
        
        console.log('初始化主页面所有图表');
        initLanguagesChart();
        initRegionsChart();
        initYearsChart();
        initScoreDurationChart();
        initDurationBucketsChart();
        initGenresScoreChart();
        initGenreRatingsChart();
        
        // 为类型选择下拉框添加事件监听
        const genreSelect = document.getElementById('genreSelect');
        if (genreSelect) {
            genreSelect.addEventListener('change', function() {
                const selectedGenre = this.value;
                fetchGenreRatingsData(selectedGenre);
            });
        }
    }
    // 检查是否在单一图表页面
    else if (document.getElementById('movieChart')) {
        console.log('初始化单一图表页面');
        
        const chartType = window.chartType;
        if (chartType && window.labels && window.data) {
            initSingleChart(chartType, window.labels, window.data);
        } else {
            console.error('单一图表页面数据不完整');
        }
    }
});

/**
 * 异步获取特定类型电影的评分数据
 * @param {string} selectedGenre - 选择的电影类型
 */
function fetchGenreRatingsData(selectedGenre) {
    console.log('获取类型评分数据:', selectedGenre);
    
    // 发送AJAX请求
    fetch(`/api/movie_analysis/genre_ratings?selected_genre=${encodeURIComponent(selectedGenre)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('成功获取类型评分数据:', data);
                
                // 更新全局chartData对象
                if (window.chartData) {
                    window.chartData.genreRatings = data.data;
                    
                    // 重新初始化图表
                    updateGenreRatingsChart();
                }
            } else {
                console.error('获取类型评分数据失败:', data.error);
            }
        })
        .catch(error => {
            console.error('AJAX请求失败:', error);
        });
}

/**
 * 更新特定类型电影评分散点图
 */
function updateGenreRatingsChart() {
    const canvas = document.getElementById('genreRatingsChart');
    if (!canvas) {
        console.error('找不到genreRatingsChart画布');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartData = window.chartData?.genreRatings;
    
    if (!chartData || !chartData.points) {
        console.error('类型评分数据不完整');
        return;
    }
    
    // 销毁旧图表（如果存在）
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // 重新初始化图表
    initGenreRatingsChart();
}