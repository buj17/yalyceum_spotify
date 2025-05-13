document.addEventListener('DOMContentLoaded', function () {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');

    favoriteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const card = this.closest('.soundtrack-card');
            const audioId = card.querySelector('audio').id.split('-')[1];
            const icon = this.querySelector('i');

            fetch(`/toggle_favorite/${audioId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    icon.classList.toggle('bi-heart');
                    icon.classList.toggle('bi-heart-fill');
                    this.classList.toggle('btn-outline-light');
                    this.classList.toggle('btn-danger');
                }
            })
            .catch(error => console.error('Ошибка при добавлении в избранное:', error));
        });
    });
});
