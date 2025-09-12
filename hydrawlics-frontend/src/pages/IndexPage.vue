<script setup lang="ts">

import axios from "axios";
import {onMounted, ref} from "vue";
import LoadingDots from "../components/LoadingDots.vue";
import type {FileStatus} from "../models/server-objects.ts";

const input = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const backgroundImage = ref<string>('');
const DEFAULT_selectorWidth = '12rem';
const selectorWidth = ref<string>(DEFAULT_selectorWidth);
const isDarkTheme = ref<boolean>(false);
const isUploading = ref(false);

const SERVER_URL = "http://localhost:5000";

const jobId = ref<string | null>(null);

const sitestage = ref<'not-uploaded' | 'uploading' | 'processing' | 'done'>('not-uploaded');
const fileState = ref<FileStatus | null>(null);

// Title animation
const title = 'Hydrawlics';
const animatedLetters = ref<{ char: string; animated: boolean }[]>(
  title.split('').map(char => ({ char, animated: false }))
);

function showUpload() {
  const event = new MouseEvent('click', {
    'view': window,
    'bubbles': true,
    'cancelable': true
  });
  console.log(event)
  input.value?.dispatchEvent(event)
}

const onFileSelection = () => {
  const files = input.value?.files;
  if (files && files[0]) {
    selectedFile.value = files[0];
    
    const reader = new FileReader();
    reader.onload = (e) => {
      backgroundImage.value = e.target?.result as string;
      
      // Calculate width based on image aspect ratio
      const img = new Image();
      img.onload = () => {
        const aspectRatio = img.width / img.height;
        const height = 192; // 12rem in pixels (assuming 16px = 1rem)
        const calculatedWidth = height * aspectRatio;
        selectorWidth.value = `${calculatedWidth}px`;
      };
      img.src = e.target?.result as string;
    };
    reader.readAsDataURL(files[0]);
  }
}

const cancel = () => {
  selectedFile.value = null;
  selectorWidth.value = DEFAULT_selectorWidth;
  backgroundImage.value = '';
}

const upload = async () => {
  if (!selectedFile.value) return;
  
  isUploading.value = true;
  
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  
  try {
    const response = await axios.post( SERVER_URL + '/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    console.log('Upload successful:', response.data);
    jobId.value = response.data.job_id;
  } catch (error) {
    console.error('Upload failed:', error);
  } finally {
    isUploading.value = false;
    sitestage.value = 'processing';
    startProgressChecks();
  }
}

const startProgressChecks = () => {
  const interval = setInterval(async ()=> {
    const response = await axios.get(SERVER_URL + `/jobs/${jobId.value}/status`, {})
    fileState.value = response.data;
    console.log(fileState.value)
    if (fileState.value?.status === 'completed') {
      clearInterval(interval);
      sitestage.value = 'done';
    }
  }, 250)
}

onMounted(()=> {
  if(input.value){
    input.value.addEventListener('change', () => onFileSelection())
    input.value.style.display = 'none'
  }
  
  // Set initial theme
  isDarkTheme.value = document.documentElement.className === 'dark';
  
  // Listen for theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  mediaQuery.addEventListener('change', (e) => {
    isDarkTheme.value = e.matches;
  });
  
  // Animate title letters
  animatedLetters.value.forEach((letter, index) => {
    setTimeout(() => {
      letter.animated = true;
    }, index * 100); // 100ms delay between each letter
  });
})

</script>

<template>
  <div class="p-3 flex row items-center container justify-between">
    <h1 style="color: var(--md-sys-color-primary)">
      <span 
        v-for="(letter, index) in animatedLetters" 
        :key="index"
        class="letter"
        :class="{ 'animated': letter.animated }"
      >
        {{ letter.char }}
      </span>
    </h1>
  </div>

  <div class="main-visualizer flex-1 flex flex-column items-center ">
    <!-- Processing -->
    <div v-if="sitestage == 'processing'" class="flex flex-row items-center" style="color: var(--md-sys-color-on-background)">
      <div style="font-family: monospace; font-size: 1.4rem">processing {{fileState?.progress ?? 0}}%</div>
      <loading-dots style="font-size: 2rem" class="ml-2"/>
    </div>

    <!-- Show image -->
    <div v-else-if="sitestage == 'done'" class="flex flex-row items-center">
      <img v-if="fileState?.download_url" :src="SERVER_URL + fileState.download_url" class="result-img"/>
    </div>


    <!-- idle image -->
    <img v-else :src="isDarkTheme ? '/scribble-hydrawlics-dark.svg' : '/scribble-hydrawlics-light.svg'" alt="Hydrawlics logo" class="scribble-svg">
  </div>

  <div class="main-container container mb-6">
    <div class="flex flex-row mt-4 p-5 rounded-4xl" style="background-color: var(--md-sys-color-surface-container)">

      <div class="flex flex-col flex-1">
        <h2 class="text-xl flex-1" style="color: var(--md-sys-color-on-surface)">Last opp et bilde</h2>

        <div v-if="selectedFile" class="flex flex-row">
          <button @click="upload" class="w-min text-nowrap mr-3">Last opp</button>
          <button @click="cancel" class="w-min secondary" style="color: var(--md-sys-color-on-surface)">Avbryt</button>
        </div>
      </div>

      <div 
        @click="showUpload" 
        class="rounded-2xl min-h-[12rem] flex items-center justify-center bg-cover bg-center file-selector"
        :class="{ 'has-image': backgroundImage }"
        :style="{ 
          backgroundImage: backgroundImage ? `url(${backgroundImage})` : '',
          width: selectorWidth
        }"
      >
<!--        <div v-if="!backgroundImage" class="text-gray-300">Velg et bilde</div>-->
        <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h240l80 80h320q33 0 56.5 23.5T880-640H447l-80-80H160v480l96-320h684L837-217q-8 26-29.5 41.5T760-160H160Zm84-80h516l72-240H316l-72 240Zm0 0 72-240-72 240Zm-84-400v-80 80Z"/></svg>
      </div>
    </div>
    <input ref="input" name="image_uploads" id="image_uploads" type="file" style="display: none"/>
  </div>
</template>

<style scoped>

h1 {
  font-family: 'Bitcount Grid Double', sans-serif;
}

.letter {
  font-weight: 50;
  transition: font-weight 0.8s ease-out;
}

.letter.animated {
  font-weight: 300;
}


button {
  border-radius: 2em;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  background-color: var(--md-sys-color-primary);
  cursor: pointer;
  transition: background-color 0.10s;

  &.secondary {
    background-color: var(--md-sys-color-surface-container);
    border: 1px solid var(--md-sys-color-outline);

    &:hover {
      background-color: color-mix(in srgb, var(--md-sys-color-surface-container) 90%, white 10%);
    }
  }

  &:hover {
    background-color: color-mix(in srgb, var(--md-sys-color-primary) 90%, white 10%);
  }
  &:focus,
  &:focus-visible {
    outline: 4px auto -webkit-focus-ring-color;
  }
}

.result-img {
  animation: img-appear 1s forwards;
  max-height: 70vh;
}

.file-selector {
  position: relative;
  overflow: hidden;
  transition: all 0.6s ease-in-out;
  clip-path: circle(3rem at center);
  background-color: var(--md-sys-color-surface-container-high);
}

.file-selector.has-image {
  clip-path: circle(100% at center);
}

.file-selector svg {
  transition: opacity 0.3s ease-in-out;
}

.file-selector.has-image svg {
  opacity: 0;
}

.scribble-svg {
  color: var(--md-sys-color-primary);
  opacity: 0.6;
  height: 12rem;
}

@keyframes img-appear {
  0% {
    opacity: 0;
    clip-path: circle(3rem at center);
    transform: scale(0.7);
  }
  100% {
    opacity: 1;
    clip-path: circle(100% at center);
    transform: scale(1);
  }
}
</style>