/*
  Animated Agent Pointer
  - Smoothly follows mouse or touch input
  - Running figure with arm and leg swing animations
  - Cycles task icons representing agent tasks
  - Click animation feedback on desktop
  - Minimal, elegant, suitable for developer UIs
*/

(() => {
  const cursor = document.getElementById('custom-cursor');
  const taskBubble = document.getElementById('task-icons');
  const taskIcons = Array.from(taskBubble.querySelectorAll('svg'));

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let posX = mouseX;
  let posY = mouseY;
  const speed = 0.15; 

  let taskIndex = 0;
  const cycleInterval = 4000;

  function cycleTasks() {
    taskIcons.forEach((icon, i) => {
      icon.classList.toggle('active', i === taskIndex);
    });
    taskIndex = (taskIndex + 1) % taskIcons.length;
  }
  cycleTasks();
  setInterval(cycleTasks, cycleInterval);

  function animate() {
    posX += (mouseX - posX) * speed;
    posY += (mouseY - posY) * speed;
    const offsetX = 14;
    const offsetY = -22;
    if (!cursor.classList.contains('click-animate')) {
      cursor.style.transform = `translate3d(${posX + offsetX}px, ${posY + offsetY}px, 0)`;
    }
    requestAnimationFrame(animate);
  }
  animate();

  window.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  window.addEventListener('mousedown', () => {
    cursor.classList.add('click-animate');
    cursor.style.transform = `translate3d(${mouseX + 14}px, ${mouseY - 22}px, 0) scale(1.15)`;
  });
  window.addEventListener('mouseup', () => {
    cursor.classList.remove('click-animate');
  });

  window.addEventListener('resize', () => {
    mouseX = Math.min(mouseX, window.innerWidth);
    mouseY = Math.min(mouseY, window.innerHeight);
  });
})();


