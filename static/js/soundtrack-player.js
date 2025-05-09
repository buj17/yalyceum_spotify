document.addEventListener('DOMContentLoaded', function () {
    const playButtons = document.querySelectorAll('.play-btn');

    playButtons.forEach(button => {
        button.addEventListener('click', function () {
            const audioId = this.getAttribute('data-audio-id');
            const audio = document.getElementById(audioId);
            const icon = this.querySelector('i');

            // Остановить все остальные треки
            document.querySelectorAll('audio').forEach(a => {
                if (a !== audio) {
                    a.pause();
                    a.currentTime = 0;
                }
            });

            // Сбросить иконки на всех кнопках
            document.querySelectorAll('.play-btn i').forEach(i => {
                i.classList.remove('bi-pause-fill');
                i.classList.add('bi-play-fill');
            });

            // Воспроизведение или пауза
            if (audio.paused) {
                audio.play();
                icon.classList.remove('bi-play-fill');
                icon.classList.add('bi-pause-fill');
            } else {
                audio.pause();
                icon.classList.remove('bi-pause-fill');
                icon.classList.add('bi-play-fill');
            }

            // Когда трек закончится — вернуть иконку "play"
            audio.addEventListener('ended', function () {
                icon.classList.remove('bi-pause-fill');
                icon.classList.add('bi-play-fill');
            });
        });
    });
});
