(() => {
  const strip = document.querySelector('.project-scroll');
  if (!strip) return;
  const carousel = strip.closest('.project-carousel');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let touching = false;
  let resumeAfter = 0;
  let direction = 1;
  let previousTime = null;
  let pendingDistance = 0;

  // Use the same scroll position for animation and gestures. Reverse gently
  // at either end instead of duplicating links or jumping back to the start.
  const animate = (time) => {
    const elapsed = previousTime === null ? 0 : Math.min(time - previousTime, 50);
    previousTime = time;
    const paused = reducedMotion.matches || document.hidden || touching || drag ||
      time < resumeAfter || carousel.matches(':hover') ||
      carousel.querySelector(':focus-visible');
    const max = strip.scrollWidth - strip.clientWidth;
    if (!paused && max > 0) {
      if (strip.scrollLeft >= max - 1) direction = -1;
      else if (strip.scrollLeft <= 0) direction = 1;
      // Some browsers round scrollLeft assignments to pixels. Accumulate
      // subpixel motion so small steps cannot disappear on fast displays.
      pendingDistance += elapsed * 0.028;
      const pixels = Math.floor(pendingDistance);
      pendingDistance -= pixels;
      strip.scrollLeft += direction * pixels;
    } else {
      pendingDistance = 0;
    }
    window.requestAnimationFrame(animate);
  };

  // Horizontal trackpad gestures and touch swipes use native scrolling.
  // Convert a vertical mouse wheel only while there is room in that direction.
  strip.addEventListener('wheel', (event) => {
    resumeAfter = performance.now() + 3000;
    if (event.ctrlKey || event.shiftKey || event.deltaX !== 0) return;
    const scale = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? strip.clientWidth : 1;
    const delta = event.deltaY * scale;
    const max = strip.scrollWidth - strip.clientWidth;
    if ((delta > 0 && strip.scrollLeft < max - 1) || (delta < 0 && strip.scrollLeft > 0)) {
      event.preventDefault();
      strip.scrollLeft += delta;
    }
  }, { passive: false });

  let drag = null;
  let suppressClick = false;
  strip.addEventListener('pointerdown', (event) => {
    suppressClick = false;
    if (event.pointerType !== 'mouse') touching = true;
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    drag = { id: event.pointerId, x: event.clientX, left: strip.scrollLeft, moved: false };
  });
  window.addEventListener('pointermove', (event) => {
    if (!drag || event.pointerId !== drag.id) return;
    const distance = event.clientX - drag.x;
    if (!drag.moved && Math.abs(distance) < 5) return;
    if (!drag.moved) {
      drag.moved = true;
      strip.setPointerCapture(event.pointerId);
      strip.classList.add('is-dragging');
    }
    event.preventDefault();
    strip.scrollLeft = drag.left - distance;
  });
  const finishDrag = (event) => {
    if (event.pointerType !== 'mouse') {
      touching = false;
      resumeAfter = performance.now() + 3000;
    }
    if (!drag || event.pointerId !== drag.id) return;
    suppressClick = drag.moved;
    drag = null;
    strip.classList.remove('is-dragging');
    if (strip.hasPointerCapture(event.pointerId)) strip.releasePointerCapture(event.pointerId);
  };
  window.addEventListener('pointerup', finishDrag);
  window.addEventListener('pointercancel', finishDrag);
  strip.addEventListener('lostpointercapture', finishDrag);
  strip.addEventListener('dragstart', (event) => event.preventDefault());
  strip.addEventListener('click', (event) => {
    if (!suppressClick || event.detail === 0) return;
    event.preventDefault();
    event.stopPropagation();
    suppressClick = false;
  }, true);
  window.requestAnimationFrame(animate);
})();
