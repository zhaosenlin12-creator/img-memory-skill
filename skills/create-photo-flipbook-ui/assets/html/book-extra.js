(function () {
  var music = document.getElementById("bgm");
  var sfx = document.getElementById("sfx-flip");
  var btn = document.getElementById("music-toggle");
  var playing = false;
  var lastFlip = 0;

  function setButton() {
    if (!btn) return;
    btn.classList.toggle("on", playing);
    btn.setAttribute("aria-pressed", playing ? "true" : "false");
  }

  function startMusic() {
    if (playing || !music) return;
    var p = music.play();
    if (p && p.then) {
      p.then(function () {
        playing = true;
        setButton();
      }).catch(function () {
        playing = false;
        setButton();
      });
    }
  }

  function toggleMusic() {
    if (!music) return;
    if (playing) {
      music.pause();
      playing = false;
      setButton();
    } else {
      startMusic();
    }
  }

  // flip sound
  var engine = window.__bookFlip;
  if (engine && sfx) {
    engine.on("flip", function () {
      var now = Date.now();
      if (now - lastFlip > 140) {
        try {
          sfx.currentTime = 0;
          var p = sfx.play();
          if (p && p.catch) p.catch(function () {});
        } catch (e) {}
        lastFlip = now;
      }
    });
  }

  if (btn) btn.addEventListener("click", toggleMusic);

  // music starts on first interaction when autoplay is blocked
  startMusic();
  var started = false;
  function onFirstGesture() {
    if (started) return;
    started = true;
    startMusic();
  }
  document.addEventListener("pointerdown", onFirstGesture, { once: true });
  document.addEventListener("keydown", onFirstGesture, { once: true });
  document.addEventListener("touchstart", onFirstGesture, { once: true });

  setButton();
})();
