document.addEventListener('DOMContentLoaded', function () {
    // Открытие модального окна для смены аватара
    const changeAvatarBtn = document.getElementById('changeAvatarBtn');
    const avatarModal = new bootstrap.Modal(document.getElementById('avatarModal'));

    changeAvatarBtn.addEventListener('click', function () {
        avatarModal.show();
    });

    // Обработчик отправки формы для обновления аватара
    const avatarForm = document.getElementById('avatarForm');
    avatarForm.addEventListener('submit', function (event) {
        event.preventDefault();  // Предотвратить стандартное поведение формы (перезагрузку страницы)

        const formData = new FormData(avatarForm);

        // Отправка AJAX-запроса на сервер
        fetch('/update_avatar', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Обновить аватар на странице
                const avatarImg = document.getElementById('userAvatar');
                avatarImg.src = data.avatar_url;  // Заменить URL изображения на новый

                // Закрыть модальное окно
                avatarModal.hide();
            } else {
                alert('Ошибка при обновлении аватара: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке запроса:', error);
            alert('Произошла ошибка при обновлении аватара');
        });
    });
});
