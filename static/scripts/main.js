tsParticles.loadJSON('Backdrop', '/static/jsons/amongus.json');

anime({
  targets: '.flash-animation .anime-object',
  scale: [
    { value: 0.9, duration: 500 },
    { value: 1.1, duration: 500 },
    { value: 1, duration: 500 }
  ],
  easing: 'spring(1, 80, 10, 0)'
});
var nothing = anime({
  targets: '.nothing-animation .anime-object',
  scale: [
    { value: 0.9, duration: 500 },
    { value: 1.1, duration: 500 },
    { value: 1, duration: 500 }
  ],
  rotate: {
    value: 360,
    duration: 500,
    easing: 'easeInOutSine'
  },
  direction: 'alternate',
  autoplay: false,
  easing: 'spring(1, 80, 10, 0)'
});