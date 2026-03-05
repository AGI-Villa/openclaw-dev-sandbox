document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const resultContainer = document.getElementById('resultContainer');
    const originalImage = document.getElementById('originalImage');
    const processedImage = document.getElementById('processedImage');
    const downloadBtn = document.getElementById('downloadBtn');
    const progressBar = document.getElementById('progressBar');

    // 历史记录相关元素
    const historyToggle = document.getElementById('historyToggle');
    const historyContent = document.getElementById('historyContent');
    const toggleIcon = document.getElementById('toggleIcon');
    const historyList = document.getElementById('historyList');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');

    // 点击上传区域触发文件选择
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // 文件选择事件
    fileInput.addEventListener('change', handleFileSelect);

    // 拖拽事件
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#2980b9';
        dropZone.style.backgroundColor = '#ecf0f1';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#3498db';
        dropZone.style.backgroundColor = 'white';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#3498db';
        dropZone.style.backgroundColor = 'white';

        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    function handleFileSelect(e) {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    }

    function handleFile(file) {
        // 验证文件类型
        const validTypes = ['image/png', 'image/jpeg', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            alert('请上传 PNG、JPG 或 WebP 格式的图片');
            return;
        }

        // 验证文件大小 (限制 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('文件大小不能超过 10MB');
            return;
        }

        // 显示原始图片预览
        const reader = new FileReader();
        reader.onload = (e) => {
            originalImage.src = e.target.result;
        };
        reader.readAsDataURL(file);

        // 处理图片
        processImage(file);
    }

    function processImage(file) {
        progressBar.style.display = 'block';
        const formData = new FormData();
        formData.append('file', file);

        fetch('/api/remove-bg', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('处理失败');
            }
            return response.blob();
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            processedImage.src = url;
            resultContainer.style.display = 'block';

            // 设置下载按钮
            downloadBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = url;
                a.download = 'background-removed.png';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            };

            // 处理成功后刷新历史记录
            loadHistory();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('图片处理失败，请重试');
        })
        .finally(() => {
            progressBar.style.display = 'none';
        });
    }

    // ============ 历史记录功能 ============

    // 加载历史记录
    async function loadHistory() {
        try {
            const response = await fetch('/api/history');
            if (!response.ok) throw new Error('Failed to load history');
            const data = await response.json();
            renderHistory(data.history);
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }

    // 渲染历史记录列表
    function renderHistory(history) {
        if (history.length === 0) {
            historyList.innerHTML = '<p class="empty-history">暂无历史记录</p>';
            clearHistoryBtn.style.display = 'none';
            return;
        }

        clearHistoryBtn.style.display = 'block';
        historyList.innerHTML = history.map(record => `
            <div class="history-item" data-id="${record.id}">
                <div class="history-info">
                    <div class="history-filename">${escapeHtml(record.original_filename)}</div>
                    <div class="history-meta">
                        ${new Date(record.timestamp).toLocaleString('zh-CN')} ·
                        ${record.file_size_human}
                    </div>
                </div>
                <div class="history-actions">
                    <button class="history-btn download-btn" onclick="downloadFile('${record.processed_filename}', '${record.id}')">
                        下载
                    </button>
                    <button class="history-btn delete-btn" onclick="deleteRecord('${record.id}')">
                        删除
                    </button>
                </div>
            </div>
        `).join('');
    }

    // 下载历史记录中的文件
    async function downloadFile(filename, recordId) {
        try {
            // 文件名安全验证：只允许字母、数字、连字符和.png扩展名
            if (!/^[a-zA-Z0-9-]+\.png$/.test(filename)) {
                console.error('Invalid filename:', filename);
                alert('下载失败：文件名无效');
                return;
            }

            const response = await fetch(`/api/download/${encodeURIComponent(filename)}`);
            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `background-removed-${filename.slice(0, 8)}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
            alert('下载失败');
        }
    }

    // 删除历史记录
    async function deleteRecord(recordId) {
        if (!confirm('确定要删除这条记录吗？')) return;

        try {
            const response = await fetch(`/api/history/${recordId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Delete failed');

            // 重新加载历史记录
            await loadHistory();
        } catch (error) {
            console.error('Delete failed:', error);
            alert('删除失败');
        }
    }

    // HTML 转义防止 XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 历史记录面板展开/收起
    historyToggle.addEventListener('click', () => {
        const isHidden = historyContent.style.display === 'none' || historyContent.style.display === '';
        historyContent.style.display = isHidden ? 'block' : 'none';
        toggleIcon.classList.toggle('expanded', isHidden);
    });

    // 清空所有历史记录
    clearHistoryBtn.addEventListener('click', async () => {
        if (!confirm('确定要清空所有历史记录吗？此操作不可恢复！')) return;

        try {
            const response = await fetch('/api/history', { method: 'DELETE' });
            if (!response.ok) throw new Error('Clear failed');
            await loadHistory();
        } catch (error) {
            console.error('Clear history failed:', error);
            alert('清空失败');
        }
    });

    // 页面加载时自动加载历史记录
    loadHistory();
});
