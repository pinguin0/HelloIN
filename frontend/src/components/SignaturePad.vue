<template>
  <div>
    <canvas ref="canvas" class="signature-pad" @pointerdown="start" @pointermove="draw" @pointerup="end" @pointerleave="end"></canvas>
    <div class="signature-actions">
      <button class="secondary" type="button" @click="clearPad">Cancella</button>
      <button class="secondary" type="button" @click="emitSignature">Salva firma</button>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const emit = defineEmits(["signed"]);
const canvas = ref(null);
let context = null;
let drawing = false;

const resizeCanvas = () => {
  const canvasEl = canvas.value;
  if (!canvasEl) return;
  const ratio = window.devicePixelRatio || 1;
  canvasEl.width = canvasEl.offsetWidth * ratio;
  canvasEl.height = canvasEl.offsetHeight * ratio;
  context = canvasEl.getContext("2d");
  context.scale(ratio, ratio);
  context.lineWidth = 2;
  context.lineCap = "round";
  context.strokeStyle = "#0f172a";
};

const getPoint = (event) => {
  const rect = canvas.value.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
};

const start = (event) => {
  drawing = true;
  const point = getPoint(event);
  context.beginPath();
  context.moveTo(point.x, point.y);
};

const draw = (event) => {
  if (!drawing) return;
  const point = getPoint(event);
  context.lineTo(point.x, point.y);
  context.stroke();
};

const end = () => {
  drawing = false;
};

const clearPad = () => {
  const canvasEl = canvas.value;
  context.clearRect(0, 0, canvasEl.width, canvasEl.height);
  emit("signed", "");
};

const emitSignature = () => {
  const canvasEl = canvas.value;
  const dataUrl = canvasEl.toDataURL("image/png");
  emit("signed", dataUrl);
};

onMounted(() => {
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCanvas);
});
</script>
