document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const resultContainer = document.getElementById('resultContainer');
    const originalImage = document.getElementById('originalImage');
    const processedImage = document.getElementById('processedImage');
    const downloadBtn = document.getElementById('downloadBtn');
    const progressBar = document.getElementById('progressBar');

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
        })
        .catch(error => {
            console.error('Error:', error);
            alert('图片处理失败，请重试');
        })
        .finally(() => {
            progressBar.style.display = 'none';
        });
    }
});