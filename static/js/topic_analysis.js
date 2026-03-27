// 重置搜索函数
function resetSearch() {
    document.getElementById('movieName').value = '';
    document.getElementById('searchForm').submit();
}

// 电影名称自动提示功能
function setupAutocomplete() {
    const movieInput = document.getElementById('movieName');
    const suggestionsDiv = document.getElementById('suggestions');
    
    // 示例电影列表 - 实际项目中应从后端获取
    const movieList = [
        '流浪地球',
        '流浪地球2',
        '满江红',
        '复仇者',
        '红海行动',
        '长津湖',
        '长津湖之水门桥',
        '你好，李焕英',
        '哪吒之魔童降世',
        '我和我的祖国',
        '我和我的家乡',
        '悬崖之上',
        '独行月球',
        '万里归途',
        '无名'
    ];
    
    movieInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const filteredMovies = movieList.filter(movie => 
            movie.toLowerCase().includes(searchTerm)
        );
        
        displaySuggestions(filteredMovies);
    });
    
    function displaySuggestions(movies) {
        if (movies.length === 0) {
            suggestionsDiv.style.display = 'none';
            return;
        }
        
        suggestionsDiv.innerHTML = '';
        movies.forEach(movie => {
            const div = document.createElement('div');
            div.className = 'autocomplete-suggestion';
            div.textContent = movie;
            div.addEventListener('click', function() {
                movieInput.value = movie;
                suggestionsDiv.style.display = 'none';
            });
            suggestionsDiv.appendChild(div);
        });
        
        suggestionsDiv.style.display = 'block';
    }
    
    // 点击页面其他地方关闭提示框
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.autocomplete')) {
            suggestionsDiv.style.display = 'none';
        }
    });
}

// 初始化主题分布图表
function initTopicDistributionChart() {
    const ldaData = window.ldaData;
    
    if (!ldaData) {
        return;
    }
    
    var ctx = document.getElementById('topicDistributionChart').getContext('2d');
    
    // 构建主题标签和分布数据
    var topicLabels = [];
    var topicData = [];
    
    for (var i = 0; i < ldaData.num_topics; i++) {
        topicLabels.push('主题 ' + (i + 1));
        topicData.push(ldaData.topic_distribution[i]);
    }
    
    // 调试：检查数据长度
    console.log('主题数量:', ldaData.num_topics);
    console.log('主题列表长度:', ldaData.topics.length);
    console.log('主题分布长度:', ldaData.topic_distribution.length);
    
    var chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topicLabels,
            datasets: [{
                label: '文档数量',
                data: topicData,
                backgroundColor: '#007bff',
                borderColor: '#0056b3',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '文档数量'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '主题'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '文档数量: ' + context.parsed.y;
                        }
                    }
                }
            }
        }
    });
}

// 页面初始化函数
document.addEventListener('DOMContentLoaded', function() {
    // 设置自动完成功能
    setupAutocomplete();
    
    // 显示查询结果提示
    const alertConfig = window.alertConfig;
    if (alertConfig && alertConfig.message) {
        showCustomAlert(alertConfig.message, alertConfig.title || '提示');
    }
    
    // 初始化主题分布图表
    initTopicDistributionChart();
});