// Home page form handlers

// Compress Form
document.addEventListener('DOMContentLoaded', () => {
    const compressForm = document.getElementById('compressForm');
    if (compressForm) {
        compressForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = document.getElementById('compressFile').files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('quality', document.getElementById('compressQuality').value);
            formData.append('max_width', document.getElementById('compressMaxWidth').value);
            formData.append('max_height', document.getElementById('compressMaxHeight').value);
            formData.append('output_format', document.getElementById('compressFormat').value);

            document.getElementById('compressLoading').classList.add('show');

            try {
                const response = await fetch('/api/compress', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (response.ok) {
                    document.getElementById('origSize').textContent = formatBytes(data.original_size);
                    document.getElementById('compSize').textContent = formatBytes(data.compressed_size);
                    document.getElementById('compRatio').textContent = data.compression_ratio + '%';
                    document.getElementById('compressResult').classList.remove('hidden');
                } else {
                    alert('Error: ' + data.detail);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('compressLoading').classList.remove('show');
            }
        });
    }

    // Convert Form
    const convertForm = document.getElementById('convertForm');
    if (convertForm) {
        convertForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = document.getElementById('convertFile').files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('output_format', document.getElementById('convertFormat').value);

            document.getElementById('convertLoading').classList.add('show');

            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (response.ok) {
                    document.getElementById('convertMessage').textContent = data.message;
                    document.getElementById('convertResult').classList.remove('hidden');
                } else {
                    alert('Error: ' + data.detail);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('convertLoading').classList.remove('show');
            }
        });
    }

    // Compress & Convert Form
    const bothForm = document.getElementById('bothForm');
    if (bothForm) {
        bothForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = document.getElementById('bothFile').files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('quality', document.getElementById('bothQuality').value);
            formData.append('output_format', document.getElementById('bothFormat').value);

            document.getElementById('bothLoading').classList.add('show');

            try {
                const response = await fetch('/api/compress-and-convert', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (response.ok) {
                    document.getElementById('bothOrigSize').textContent = formatBytes(data.original_size);
                    document.getElementById('bothCompSize').textContent = formatBytes(data.compressed_size);
                    document.getElementById('bothCompRatio').textContent = data.compression_ratio + '%';
                    document.getElementById('bothFormatResult').textContent = data.format;
                    document.getElementById('bothResult').classList.remove('hidden');
                } else {
                    alert('Error: ' + data.detail);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('bothLoading').classList.remove('show');
            }
        });
    }
});
