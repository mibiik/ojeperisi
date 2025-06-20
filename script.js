document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('imageUpload');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultDiv = document.getElementById('result');
    const uploadLabel = document.querySelector('.upload-label');
    const imagePreview = document.getElementById('imagePreview');
    const initialUploadContent = document.getElementById('initial-upload-content');

    let selectedFile = null;

    function resetUploadArea() {
        uploadLabel.innerHTML = '';
        uploadLabel.appendChild(initialUploadContent);
    }

    imageUpload.addEventListener('change', (event) => {
        selectedFile = event.target.files[0];
        if (selectedFile) {
            // Önizlemeyi göster
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Oje Resmi Önizleme">`;
                imagePreview.style.display = 'block';
            }
            reader.readAsDataURL(selectedFile);

            uploadLabel.innerHTML = `
                <div class="post-upload-content">
                    <span class="upload-success-text">✔️ Harika bir seçim!</span>
                    <a href="#" class="change-link">Başka bir görsel seç</a>
                </div>
            `;

            document.querySelector('.change-link').addEventListener('click', (e) => {
                e.preventDefault();
                imageUpload.click();
            });

            analyzeBtn.disabled = false;
        }
    });

    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            alert('Lütfen önce bir resim seçin.');
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analiz Ediliyor...';
        resultDiv.innerHTML = `<p>Ayy, bu oje hangi renk acaba? Çok merak ediyoruumm... 🤔</p>`;

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                // AI tarafından gönderilen özel hata mesajını kullan
                if (data && data.message) {
                    throw new Error(data.message);
                }
                throw new Error('Analiz sırasında bir şeyler ters gitti.');
            }
            
            displayResult(data);

        } catch (error) {
            displayError(error.message);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Rengi Analiz Et';
        }
    });

    function displayError(message) {
        resultDiv.innerHTML = `<p class="ai-error">${message}</p>`;
    }

    function displayResult(data) {
        resultDiv.innerHTML = `
            <div class="color-preview" style="background-color: ${data.hexCode};"></div>
            <div class="color-info">
                <h3>${data.colorName}</h3>
                <p class="hex-code">${data.hexCode}</p>
                <p class="ai-comment">"${data.aiComment}"</p>
            </div>
        `;
    }
}); 