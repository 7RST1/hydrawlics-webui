<script setup lang="ts">
import {SERVER_URL} from "../constants.ts";
import {onMounted, ref} from "vue";
import axios, {AxiosError} from "axios";

export type ConnectionLevel = 'local' | 'server' | 'robot'

const connectionStatus = ref<undefined | ConnectionLevel>(undefined);

const tryConnectServer = async () => {
  const response = await axios.get(SERVER_URL + `/ping`, {})
  const res = response.data;
  console.log(res)
  console.log("connected")
  connectionStatus.value = 'server';
}

const connectIter = async () => {
  try {
    await tryConnectServer();
    setTimeout(connectIter, 3000);
  } catch (error) {
    connectionStatus.value = 'local';
    setTimeout(connectIter, 1000);
  }
}

onMounted(async () => {
  connectIter();
})

defineExpose({
  connectionStatus
})

</script>

<template>
<div class="flex flex-row items-center">

  <div class="status-icon">
    <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M160-80q-33 0-56.5-23.5T80-160v-360q0-33 23.5-56.5T160-600h80v-200q0-33 23.5-56.5T320-880h480q33 0 56.5 23.5T880-800v360q0 33-23.5 56.5T800-360h-80v200q0 33-23.5 56.5T640-80H160Zm0-80h480v-280H160v280Zm560-280h80v-280H320v120h320q33 0 56.5 23.5T720-520v80Z"/></svg>
  </div>

  <div class="flex flex-row dots" :class="{'error-dots': connectionStatus == 'local'}">
    <span v-for="i in 3" :style="{animationDelay: i/5+1+'s'}">
      <span v-if="i == 2 && connectionStatus == 'local'" class="error-x">+</span>
      <template v-else>·</template>
    </span>
  </div>

  <div class="status-icon">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M323-160q-11 0-20.5-5.5T288-181l-78-139h58l40 80h92v-40h-68l-40-80H188l-57-100q-2-5-3.5-10t-1.5-10q0-4 5-20l57-100h104l40-80h68v-40h-92l-40 80h-58l78-139q5-10 14.5-15.5T323-800h97q17 0 28.5 11.5T460-760v160h-60l-40 40h100v120h-88l-40-80h-92l-40 40h108l40 80h112v200q0 17-11.5 28.5T420-160h-97Zm217 0q-17 0-28.5-11.5T500-200v-200h112l40-80h108l-40-40h-92l-40 80h-88v-120h100l-40-40h-60v-160q0-17 11.5-28.5T540-800h97q11 0 20.5 5.5T672-779l78 139h-58l-40-80h-92v40h68l40 80h104l57 100q2 5 3.5 10t1.5 10q0 4-5 20l-57 100H668l-40 80h-68v40h92l40-80h58l-78 139q-5 10-14.5 15.5T637-160h-97Z"/></svg>
  </div>


  <div class="flex flex-row dots" :class="{'error-dots': true, 'hide': connectionStatus == 'local', 'second-connect': connectionStatus == 'server' || connectionStatus == undefined}">
    <span v-for="i in 3" :style="{animationDelay: i/5+1+'s'}">
      <span v-if="i == 2 && true" class="error-x">+</span>
      <template v-else>·</template>
    </span>
  </div>

  <div class="status-icon">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M159-120v-120h124L181-574q-27-15-44.5-44T119-680q0-50 35-85t85-35q39 0 69.5 22.5T351-720h128v-40q0-17 11.5-28.5T519-800q9 0 17.5 4t14.5 12l68-64q9-9 21.5-11.5T665-856l156 72q12 6 16.5 17.5T837-744q-6 12-17.5 15.5T797-730l-144-66-94 88v56l94 86 144-66q11-5 23-1t17 15q6 12 1 23t-17 17l-156 74q-12 6-24.5 3.5T619-512l-68-64q-6 6-14.5 11t-17.5 5q-17 0-28.5-11.5T479-600v-40H351q-3 8-6.5 15t-9.5 15l200 370h144v120H159Zm80-520q17 0 28.5-11.5T279-680q0-17-11.5-28.5T239-720q-17 0-28.5 11.5T199-680q0 17 11.5 28.5T239-640Zm126 400h78L271-560h-4l98 320Zm78 0Z"/></svg>
  </div>
</div>
</template>

<style scoped lang="scss">
$dot-size: 2em;

.status-icon {
  background-color: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  padding: 0.4em;
  border-radius: 50%;
  margin-right: $dot-size * 0.18;

  svg {
    height: 1.8em;
    width: 1.8em;
  }
}

.dots {
  font-family: 'Bitcount Grid Double', sans-serif;
  font-size: $dot-size;
  margin: 0;

  &.hide {
    opacity: 0 !important;
  }

  &:not(.error-dots) {
    span {
      opacity: 0;
      animation: dot-appear 0.1s forwards ease-in-out, dot-blink 1s infinite ease-in-out;
    }
  }

  &.error-dots {
    font-family: 'Bitcount Grid Double', sans-serif;
    font-size: $dot-size;
    color: color-mix(in srgb, var(--md-sys-color-on-background) 50%, transparent 100%);
    .error-x {
      opacity: 1;
      display: inline-block;
      transform: rotate(45deg);
      margin-right: $dot-size * 0.045;
      margin-left: $dot-size * -0.045;
      animation: error-blink 1s infinite step-end;
      color: red;
    }

    &.second-connect {
      opacity: 0;
      animation: dot-appear 0.1s forwards 2s ease-in-out;
    }
  }
}

@keyframes dot-appear {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@keyframes dot-blink {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0.8;
  }
}

@keyframes error-blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}
</style>