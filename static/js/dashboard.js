// 分页控制函数
function changePerPage() {
    const perPage = document.getElementById('perPageSelect').value;
    const form = document.getElementById('pageForm');
    document.getElementById('pageInput').value = 1;
    document.getElementById('perPageInput').value = perPage;
    form.submit();
}

// 页码跳转函数
function jumpToPage() {
    const jumpPage = document.getElementById('jumpPage').value;
    const totalPages = window.totalPages;
    const form = document.getElementById('pageForm');
    
    // 验证页码有效性
    if (jumpPage && !isNaN(jumpPage)) {
        let page = parseInt(jumpPage);
        page = Math.max(1, Math.min(page, totalPages));
        document.getElementById('pageInput').value = page;
        form.submit();
    } else {
        showCustomAlert('请输入有效的页码', '错误');
    }
}

// 重置搜索函数
function resetSearch() {
    // 重置所有搜索字段
    const searchFields = ['movieName', 'commentId', 'keyword'];
    searchFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = '';
        }
    });
    
    document.getElementById('pageInput').value = 1;
    // 在提交表单前添加一个隐藏字段，用于标记需要重置metrics
    let resetField = document.createElement('input');
    resetField.type = 'hidden';
    resetField.name = 'reset_metrics';
    resetField.value = 'true';
    document.getElementById('searchForm').appendChild(resetField);
    
    document.getElementById('searchForm').submit();
}

// 页面初始化函数
document.addEventListener('DOMContentLoaded', function() {
    // 从HTML中获取配置数据
    const alertConfig = window.alertConfig;
    const isSuccess = window.isSuccess;
    
    // 显示成功提示信息
    if (isSuccess) {
        // 检查成功信息的内容，显示相应的提示
        if (typeof isSuccess === 'string' && isSuccess.includes('修改')) {
            showCustomAlert(isSuccess, '修改成功');
        } else {
            showCustomAlert('登录成功');
        }
    }
    
    // 显示查询结果提示
    if (alertConfig && alertConfig.message) {
        showCustomAlert(alertConfig.message, alertConfig.title || '提示');
    }
});