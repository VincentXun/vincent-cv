'use strict';
const videos = [...document.querySelectorAll('video')];
const pair = [document.querySelector('#tactile-video'), document.querySelector('#vision-video')];
const playButton = document.querySelector('#compare-play');
const restartButton = document.querySelector('#compare-restart');
const status = document.querySelector('#compare-status');
const note = '两段为独立演示，非逐帧配对实验；展示具体案例，不代表统计成功率。';
let pairMode = false;
let command = 0;
document.querySelector('.comparison-controls').hidden = false;
function updateButton() {
  playButton.textContent = pair.some(video => !video.paused && !video.ended) ? '暂停对照' : '同时播放';
}
function showError(video) {
  if (video.closest('figure').querySelector('.media-error')) return;
  const message = document.createElement('p');
  message.className = 'media-error';
  message.append('视频暂时无法播放。请刷新重试，或');
  const link = document.createElement('a');
  link.href = video.getAttribute('src');
  link.textContent = '打开视频文件';
  message.append(link, '。');
  video.closest('figure').append(message);
}
videos.forEach(video => {
  video.muted = true;
  video.addEventListener('play', () => {
    videos.forEach(other => {
      if (other !== video && !(pairMode && pair.includes(video) && pair.includes(other))) other.pause();
    });
    if (!pair.includes(video)) {pairMode = false; command++;}
    updateButton();
  });
  ['pause', 'ended'].forEach(event => video.addEventListener(event, updateButton));
  video.addEventListener('error', () => showError(video));
});
async function startComparison(reset) {
  const token = ++command;
  pairMode = true;
  videos.filter(video => !pair.includes(video)).forEach(video => video.pause());
  if (reset || pair.some(video => video.ended)) pair.forEach(video => {video.currentTime = 0;});
  // Both play requests occur inside the same user gesture, including on mobile.
  const results = await Promise.allSettled(pair.map(video => video.play()));
  if (token !== command) return;
  if (results.some(result => result.status === 'rejected')) {
    pair.forEach(video => video.pause());
    pairMode = false;
    status.textContent = '同时播放未能启动，请使用各视频的播放按钮。' + note;
  } else {
    status.textContent = note;
  }
  updateButton();
}
playButton.addEventListener('click', () => {
  if (pair.some(video => !video.paused && !video.ended)) {
    command++;
    pair.forEach(video => video.pause());
  } else startComparison(false);
});
restartButton.addEventListener('click', () => startComparison(true));
