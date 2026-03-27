const chartInstances = {};

function renderLineChart(canvasId, title, labels, values, lineColor, fillColor) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }

    chartInstances[canvasId] = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "评论数量",
                data: values,
                borderColor: lineColor,
                backgroundColor: fillColor,
                tension: 0.2,
                pointRadius: 2,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title
                },
                tooltip: {
                    mode: "index",
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 24,
                        maxRotation: 45,
                        minRotation: 0
                    }
                }
            }
        }
    });
}

function initYearChart(labels, values) {
    renderLineChart(
        "yearChart",
        "按年份评论时间段统计",
        labels,
        values,
        "rgba(75, 192, 192, 1)",
        "rgba(75, 192, 192, 0.2)"
    );
}

function initMonthChart(labels, values) {
    renderLineChart(
        "monthChart",
        "按月份评论时间段统计",
        labels,
        values,
        "rgba(153, 102, 255, 1)",
        "rgba(153, 102, 255, 0.2)"
    );
}

function initMonthHourChart(labels, values) {
    renderLineChart(
        "monthHourChart",
        "按月小时评论时间段统计",
        labels,
        values,
        "rgba(255, 99, 132, 1)",
        "rgba(255, 99, 132, 0.2)"
    );
}

function initYearHourChart(labels, values) {
    renderLineChart(
        "yearHourChart",
        "按年小时评论时间段统计",
        labels,
        values,
        "rgba(54, 162, 235, 1)",
        "rgba(54, 162, 235, 0.2)"
    );
}

function initCharts(yearChartData, monthChartData, _pieChartData, _pieMonthData, monthHourChartData, yearHourChartData) {
    initYearChart(yearChartData.labels || [], yearChartData.values || []);
    initMonthChart(monthChartData.labels || [], monthChartData.values || []);
    initMonthHourChart(monthHourChartData.labels || [], monthHourChartData.values || []);
    initYearHourChart(yearHourChartData.labels || [], yearHourChartData.values || []);
}

window.initCharts = initCharts;
