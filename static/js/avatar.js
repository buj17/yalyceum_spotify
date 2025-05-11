document.addEventListener('DOMContentLoaded', function() {
    const avatarForm = document.getElementById('avatarForm');

    if (avatarForm) {
        avatarForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('avatarInput');
            const file = fileInput.files[0];

            if (file) {
                const formData = new FormData();
                formData.append('avatar', file);

                fetch('/update_avatar', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Обновляем изображение на странице
                        document.querySelector('.rounded-circle[alt="Аватар"]').src = data.avatar_url + '?' + new Date().getTime();
                        // Закрываем модальное окно
                        bootstrap.Modal.getInstance(document.getElementById('avatarModal')).hide();
                    } else {
                        alert('Ошибка при загрузке аватара: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при загрузке файла');
                });
            }
        });
    }
});
