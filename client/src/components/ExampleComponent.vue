<script setup lang="ts">
import { useExampleStore } from '../stores/exampleStore';
import { storeToRefs } from 'pinia';

// acquire pinia store
const exampleStore = useExampleStore();
// button configurations
const { exampleData } = storeToRefs(exampleStore);

const getExampleData = () => {
  exampleStore.get_example_data();
  exampleData.value = exampleStore.exampleData;
};

const modifyExampleData = () => {
  exampleStore.modify_example_data();
  exampleData.value = exampleStore.exampleData;
};
</script>

<template>
   <div class="flex justify-center">
    <button btn @click="getExampleData">Get</button>
    <button btn @click="modifyExampleData">Post</button>
    {{ exampleData }}
  </div>
</template>


