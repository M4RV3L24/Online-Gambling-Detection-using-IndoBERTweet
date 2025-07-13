<script lang="ts">
  import { navigating } from '$app/stores';
  import { onMount } from 'svelte';
  import {toast, Toaster} from 'svelte-sonner';

  // Menerima data dari fungsi `load` di +page.server.ts
  export let data;
  // Menerima hasil dari form action di +page.server.ts
  export let form;
  // Handler for form submit

  // Show toast after form submission based on form result
  onMount(() => {
    if (form?.success) {
      toast.success(form.message);
    } else if (form?.message) {
      toast.error(form.message);
    }
  });

  // function handleSubmit(event: Event) {
  //   // Let the form submit as usual
  //   // Show toast after short delay to ensure navigation
  //   setTimeout(() => {
  //     toast.success('Vote Anda telah direkam!');
  //   }, 100);
  // }

</script>

<Toaster />
{#if data.unvotedText}
    <div class="card">
        <p class="text-content">{data.unvotedText.text_content}</p>
    </div>

    <form method="POST" action="?/vote" class:loading={$navigating}>
        <input type="hidden" name="text_id" value={data.unvotedText.id} />

        <div class="button-container">
            <button type="submit" name="decision" value="yes" class="btn-yes">
                Yes (Mengandung Promosi)
            </button>
            <button type="submit" name="decision" value="no" class="btn-no">
                No (Tidak Mengandung Promosi)
            </button>
        </div>
    </form>
{:else}
    <div class="card">
        <p>Selamat! Semua data telah berhasil dilabeli.</p>
    </div>
{/if}

<style>
    .loading {
        opacity: 0.5;
        pointer-events: none;
    }

    /* (Anda bisa menambahkan style lain di sini untuk mempercantik tampilan) */
    .card {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .text-content {
        font-size: 1.2rem;
        line-height: 1.6;
    }

    .button-container {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }

    button {
        padding: 0.8rem 1.5rem;
        border: none;
        border-radius: 5px;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }

    .btn-yes {
        background-color: #28a745;
        color: white;
    }

    .btn-yes:hover {
        background-color: #218838;
    }

    .btn-no {
        background-color: #dc3545;
        color: white;
    }

    .btn-no:hover {
        background-color: #c82333;
    }
</style>
