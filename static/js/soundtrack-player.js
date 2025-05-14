document.addEventListener('DOMContentLoaded', function() {
  const playButtons = document.querySelectorAll('.play-btn');
  let currentVolume = localStorage.getItem('audioVolume') || 0.5;

  // Инициализация громкости для всех аудио элементов
  document.querySelectorAll('audio').forEach(audio => {
    audio.volume = currentVolume;
  });

  // Обновление иконки громкости
  function updateVolumeIcon(volume) {
    const icons = document.querySelectorAll('.volume-icon');
    icons.forEach(icon => {
      if (volume == 0) {
        icon.className = 'bi bi-volume-mute volume-icon';
      } else if (volume < 0.5) {
        icon.className = 'bi bi-volume-down volume-icon';
      } else {
        icon.className = 'bi bi-volume-up volume-icon';
      }
    });
  }

  // Обработчики для регуляторов громкости
  document.querySelectorAll('.volume-slider').forEach(slider => {
    slider.value = currentVolume;
    slider.addEventListener('input', function() {
      const volume = parseFloat(this.value);
      document.querySelectorAll('audio').forEach(audio => {
        audio.volume = volume;
      });
      localStorage.setItem('audioVolume', volume);
      updateVolumeIcon(volume);
    });
  });

  // Ваш существующий код для кнопок воспроизведения
  playButtons.forEach(button => {
    button.addEventListener('click', function() {
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
      audio.addEventListener('ended', function() {
        icon.classList.remove('bi-pause-fill');
        icon.classList.add('bi-play-fill');
      });
    });
  });

  // Инициализация иконок громкости
  updateVolumeIcon(currentVolume);
});