document.addEventListener('DOMContentLoaded', function() {
    const avatarForm = document.getElementById('avatarForm');
    const avatarInput = document.getElementById('avatarInput');
    const avatarError = document.getElementById('avatarError');
    const submitBtn = document.getElementById('submitBtn');

    if (avatarForm) {
        avatarForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Загрузка...';

            const file = avatarInput.files[0];

            try {
                const formData = new FormData();
                formData.append('avatar', file);

                const response = await fetch('/update_avatar', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Обновляем изображение на странице с параметром времени, чтобы избежать кеширования
                    document.getElementById('userAvatar').src = data.avatar_url + '?' + new Date().getTime();

                    // Закрываем модальное окно
                    const modal = bootstrap.Modal.getInstance(document.getElementById('avatarModal'));
                    modal.hide();

                    // Показываем уведомление об успехе
                    showToast('Аватар успешно обновлен', 'success');
                } else {
                    avatarError.textContent = data.message;
                    avatarInput.classList.add('is-invalid');
                }
            } catch (error) {
                console.error('Error:', error);
                avatarError.textContent = 'Произошла ошибка при загрузке файла';
                avatarInput.classList.add('is-invalid');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Сохранить';
            }
        });

        // Сброс ошибок при повторном открытии модального окна
        document.getElementById('avatarModal').addEventListener('show.bs.modal', function() {
            avatarInput.classList.remove('is-invalid');
            avatarError.textContent = '';
            avatarForm.reset();
        });
    }

    // Функция для показа уведомлений
    function showToast(message, type = 'success') {
        const toastContainer = document.createElement('div');
        toastContainer.innerHTML = `
            <div class="toast align-items-center text-white bg-${type} border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        toastContainer.style.position = 'fixed';
        toastContainer.style.top = '20px';
        toastContainer.style.right = '20px';
        toastContainer.style.zIndex = '1100';

        document.body.appendChild(toastContainer);

        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            toastContainer.remove();
        }, 5000);
    }
});