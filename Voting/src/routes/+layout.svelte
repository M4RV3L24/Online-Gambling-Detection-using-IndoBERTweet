<script>
import "../app.css";
let { children } = $props();
</script>

<div class="fixed inset-0 min-h-screen w-full dark:bg-gray-950 -z-10"></div>
<div class="relative z-0 min-h-screen w-full dark:text-gray-100">
  {@render children()}
</div>