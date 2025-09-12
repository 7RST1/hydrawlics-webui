<script setup lang="ts">

import {computed, onMounted, ref} from "vue";

const chars = [
    '|',
    '/',
    '-',
    '\\',
]

const i = ref(0);
const currentChar = computed(() => {
  return chars[i.value];
})

onMounted(() => {
  setInterval(()=>{
    i.value = (i.value + 1) % chars.length;
  }, 100)
})

</script>

<template>
<div style="font-family: 'Bitcount Grid Double', sans-serif;">
  {{currentChar}}
</div>
</template>