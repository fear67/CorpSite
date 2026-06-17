document.addEventListener('DOMContentLoaded', () => {
    const allButtons = document.querySelectorAll('.read-more-btn');

    allButtons.forEach((button) => {
        
        button.addEventListener('click', () => {
            const currentDesc = button.previousElementSibling;
            if (currentDesc && currentDesc.classList.contains('promo-desc')) {
                
                currentDesc.classList.toggle('expanded');
                if (currentDesc.classList.contains('expanded')) {
                    button.textContent = 'Свернуть';
                } else {
                    button.textContent = 'Ещё';
                }
            }
        });
        
    });
});



document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            // Создаем кастомную кнопку и вставляем
            const wrapper = document.createElement('div');
            wrapper.style.display = 'flex';
            wrapper.style.alignItems = 'center';
            wrapper.style.flexWrap = 'wrap';
            wrapper.style.gap = '10px';
            
            const customBtn = document.createElement('span');
            customBtn.className = 'custom-file-label';
            customBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg> Выберите файл';
            
            const fileNameSpan = document.createElement('span');
            fileNameSpan.className = 'file-name';
            fileNameSpan.textContent = 'Файл не выбран';
            
            fileInput.parentNode.insertBefore(wrapper, fileInput);
            wrapper.appendChild(customBtn);
            wrapper.appendChild(fileNameSpan);
            
            customBtn.addEventListener('click', function() {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', function() {
                if (fileInput.files.length > 0) {
                    fileNameSpan.textContent = fileInput.files[0].name;
                } else {
                    fileNameSpan.textContent = 'Файл не выбран';
                }
            });
        }
    });