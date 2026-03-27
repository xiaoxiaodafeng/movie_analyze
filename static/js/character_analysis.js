// 全局变量
var modal;

// 所有DOM元素加载完成后执行
(document.addEventListener('DOMContentLoaded', function() {
    // 弹出框元素
    modal = document.getElementById("characterModal");

    // 关闭按钮
    var span = document.getElementsByClassName("close")[0];
    var closeBtn = document.getElementsByClassName("close-btn")[0];

    // 关闭弹出框
    function closeModal() {
        modal.style.display = "none";
    }

    // 点击关闭按钮或关闭图标时关闭弹出框
    span.onclick = closeModal;
    closeBtn.onclick = closeModal;

    // 点击弹出框外部时关闭弹出框
    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        }
    }
}));

// 显示演员/导演详细信息
function showCharacterDetails(characterId) {
    // 发送AJAX请求获取演员详情
    fetch('/character_details/' + characterId)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('获取演员详情失败: ' + data.error);
                return;
            }
            
            // 显示基本信息
            var detailsHtml = '<div class="character-basic-info">';
            detailsHtml += '<p><strong>人物ID:</strong> ' + data.character_id + '</p>';
            detailsHtml += '<p><strong>人物姓名:</strong> ' + data.character_name + '</p>';
            detailsHtml += '<p><strong>参与身份:</strong> ' + data.participation_role + '</p>';
            detailsHtml += '<p><strong>演员作品数:</strong> ' + data.actor_work_count + '</p>';
            detailsHtml += '<p><strong>导演作品数:</strong> ' + data.director_work_count + '</p>';
            detailsHtml += '<p><strong>总作品数:</strong> ' + data.total_work_count + '</p>';
            detailsHtml += '<p><strong>电影类型数:</strong> ' + data.movie_type_count + '</p>';
            detailsHtml += '<p><strong>主要电影类型:</strong> ' + data.main_movie_type + '</p>';
            detailsHtml += '<p><strong>前三大类型:</strong> ' + data.top_three_types + '</p>';
            detailsHtml += '</div>';
            
            document.getElementById('characterDetails').innerHTML = detailsHtml;
            
            // 绘制拍摄类型比例饼图
            try {
                console.log('开始绘制类型比例饼图');
                console.log('all_types_stat数据:', data.all_types_stat);
                
                if (data.all_types_stat) {
                    drawTypeChart(data.all_types_stat);
                    console.log('类型比例饼图绘制完成');
                } else {
                    console.log('暂无类型统计数据');
                    document.querySelector('#typeChart').parentElement.innerHTML += '<p>暂无类型统计数据</p>';
                }
            } catch (error) {
                console.error('绘制类型比例饼图出错:', error);
                console.error('错误堆栈:', error.stack);
                document.querySelector('#typeChart').parentElement.innerHTML += '<p>类型统计数据格式错误</p>';
            }
            
            // 绘制类型详情条形图
            try {
                console.log('开始绘制类型详情条形图');
                console.log('type_details数据:', data.type_details);
                
                if (data.type_details) {
                    drawTypeDetailsChart(data.type_details);
                    console.log('类型详情条形图绘制完成');
                } else {
                    console.log('暂无类型详情数据');
                    document.querySelector('#typeDetailsChart').parentElement.innerHTML += '<p>暂无类型详情数据</p>';
                }
            } catch (error) {
                console.error('绘制类型详情条形图出错:', error);
                console.error('错误堆栈:', error.stack);
                // 更详细的错误信息
                var errorMsg = '<p>类型详情数据格式错误: ' + (error.message || '未知错误') + '</p>';
                document.querySelector('#typeDetailsChart').parentElement.innerHTML += errorMsg;
            }
            
            // 显示弹出框
            modal.style.display = "block";
        })
        .catch(error => {
            console.error('获取演员详情出错:', error);
            alert('获取演员详情失败');
        });
}

// 绘制拍摄类型比例饼图
function drawTypeChart(allTypesStat) {
    // 解析类型统计数据 - "喜剧:123; 剧情:84; 动作:71;..."格式
    var typeStats = {};
    var typePairs = allTypesStat.split('; ');
    
    for (var i = 0; i < typePairs.length; i++) {
        var pair = typePairs[i].trim();
        if (pair) {
            var [type, count] = pair.split(':');
            typeStats[type.trim()] = parseInt(count.trim());
        }
    }
    
    var labels = [];
    var data = [];
    var colors = [];
    
    // 生成颜色
    for (var type in typeStats) {
        labels.push(type);
        data.push(typeStats[type]);
        colors.push('#' + Math.floor(Math.random()*16777215).toString(16));
    }
    
    // 获取canvas元素
    var ctx = document.getElementById('typeChart').getContext('2d');
    
    // 清除之前的图表
    if (window.typeChart && typeof window.typeChart.destroy === 'function') {
        window.typeChart.destroy();
        // 重置为null，避免下次使用时出现问题
        window.typeChart = null;
    } else {
        console.warn('window.typeChart不是有效的Chart.js对象，无法销毁');
        window.typeChart = null;
    }
    
    // 创建新图表
    window.typeChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(color => color + '80'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                title: {
                    display: true,
                    text: '拍摄类型比例'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            var label = context.label || '';
                            var value = context.parsed || 0;
                            var total = context.dataset.data.reduce((a, b) => a + b, 0);
                            var percentage = Math.round((value / total) * 100);
                            return label + ': ' + value + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// 绘制类型详情条形图
function drawTypeDetailsChart(typeDetails) {
    try {
        console.log('原始类型详情数据:', typeDetails);
        
        // 确保数据是字符串
        if (typeof typeDetails !== 'string') {
            console.error('typeDetails不是字符串类型:', typeof typeDetails);
            throw new Error('数据类型错误：typeDetails必须是字符串');
        }
        
        // 解析类型详情数据 - 提取每种类型的演员和导演数量
        var typeNames = [];
        var actorCounts = [];
        var directorCounts = [];
        
        // 首先处理可能的换行符、制表符和多余空格
        var cleanedData = typeDetails.replace(/[\r\n\t]+/g, ' ').trim();
        console.log('清理后的数据:', cleanedData);
        
        // 使用|分隔符分割类型条目
        var typeEntries = cleanedData.split(/\s*\|\s*/);
        console.log('使用|分割后的类型条目:', typeEntries);
        
        // 处理每个类型条目
        var parsedCount = 0;
        for (var i = 0; i < typeEntries.length; i++) {
            var entry = typeEntries[i].trim();
            console.log('处理条目', i + 1, ':', entry);
            
            if (entry && !entry.includes('character_id')) { // 排除可能的表头
                // 提取类型名称
                var typeMatch = entry.match(/^\s*(.*?)\s*\(\d+\)/);
                if (typeMatch && typeMatch[1]) {
                    var typeName = typeMatch[1].trim();
                    
                    // 提取演员数量
                    var actorMatch = entry.match(/演:\s*(\d+)/);
                    var actorCount = actorMatch ? parseInt(actorMatch[1]) : 0;
                    
                    // 提取导演数量
                    var directorMatch = entry.match(/导:\s*(\d+)/);
                    var directorCount = directorMatch ? parseInt(directorMatch[1]) : 0;
                    
                    console.log('提取结果:', typeName, '演员:', actorCount, '导演:', directorCount);
                    
                    // 只添加有数据的类型
                    if (actorCount > 0 || directorCount > 0) {
                        typeNames.push(typeName);
                        actorCounts.push(actorCount);
                        directorCounts.push(directorCount);
                        parsedCount++;
                    }
                } else {
                    console.warn('无法匹配类型名称:', entry);
                }
            }
        }
        
        console.log('解析后的详情数据:', {typeNames, actorCounts, directorCounts});
        console.log('成功解析', parsedCount, '个类型条目');
        
        // 检查是否解析到数据
        if (typeNames.length === 0) {
            console.error('未解析到任何类型详情数据');
            // 显示原始数据作为后备
            var rawDataElement = document.createElement('div');
            rawDataElement.innerHTML = '<p>数据格式无法解析，原始数据：</p><pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;">' + typeDetails + '</pre>';
            document.querySelector('#typeDetailsChart').parentElement.appendChild(rawDataElement);
            return;
        }
        
        // 获取canvas元素
        var ctx = document.getElementById('typeDetailsChart').getContext('2d');
        if (!ctx) {
            console.error('无法获取canvas上下文');
            throw new Error('无法获取图表绘制上下文');
        }
        
        // 清除之前的图表
        if (window.typeDetailsChart && typeof window.typeDetailsChart.destroy === 'function') {
            window.typeDetailsChart.destroy();
            // 重置为null，避免下次使用时出现问题
            window.typeDetailsChart = null;
        } else {
            console.warn('window.typeDetailsChart不是有效的Chart.js对象，无法销毁');
            window.typeDetailsChart = null;
        }
        
        // 创建新图表 - 分组条形图展示演员和导演数量
        window.typeDetailsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: typeNames,
                datasets: [
                    {
                        label: '演员作品数',
                        data: actorCounts,
                        backgroundColor: '#667eea',
                        borderColor: '#5568d3',
                        borderWidth: 1
                    },
                    {
                        label: '导演作品数',
                        data: directorCounts,
                        backgroundColor: '#f093fb',
                        borderColor: '#c77dff',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '作品数量'
                        },
                        stacked: false // 使用分组条形图
                    },
                    x: {
                        title: {
                            display: true,
                            text: '类型'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: '各类型演员/导演作品数量分析'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                var label = context.dataset.label || '';
                                var value = context.parsed.y || 0;
                                return label + ': ' + value + '部作品';
                            }
                        }
                    },
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
        
        console.log('类型详情条形图绘制完成');
    } catch (error) {
        console.error('绘制类型详情条形图出错:', error);
        console.error('错误堆栈:', error.stack);
        // 显示详细错误信息
        var errorDetails = '<p>错误详情：' + (error.message || '未知错误') + '</p>';
        errorDetails += '<p>请检查浏览器控制台以获取更多调试信息。</p>';
        document.querySelector('#typeDetailsChart').parentElement.innerHTML += errorDetails;
        throw error;
    }
}