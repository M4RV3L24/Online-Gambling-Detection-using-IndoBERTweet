<script lang="ts">
    import { Toaster, toast } from "svelte-sonner";
    import { onMount } from "svelte";
    import { enhance } from "$app/forms";
    import { flip } from "svelte/animate";
    import SelectionTable from "./SelectionTable.svelte";
    import { writable } from "svelte/store";
    export let data;
    export let form;


    const filter = writable("all");

    $: filteredTexts = data?.texts
        ? data.texts.filter((t) => {
              if ($filter === "voted_yes") {
                  return t.votes.some(
                      (v) =>
                          v.user_id === data.session.user.id &&
                          v.vote === true &&
                          (!v.skip || v.skip === 0)
                  );
              } else if ($filter === "voted_no") {
                  return t.votes.some(
                      (v) =>
                          v.user_id === data.session.user.id &&
                          v.vote === false &&
                          (!v.skip || v.skip === 0)
                  );
              } else if ($filter === "skipped") {
                  return t.votes.some(
                      (v) => v.user_id === data.session.user.id && v.skip === 1
                  );
              } else {
                  return (
                      (!t.votes.some(
                          (v) => v.user_id === data.session.user.id
                      ) &&
                          !t.votes.some(
                              (v) =>
                                  v.user_id === data.session.user.id &&
                                  v.skip === 1
                          )) ||
                      t.votes.some(
                          (v) =>
                              v.user_id === data.session.user.id &&
                              (v.skip === 0 || v.skip === null) &&
                              v.vote === null
                      )
                  );
              }
          }).slice(0, 200)
        : [];


onMount(() => {
    if (form?.success) {
        toast.success(form.message);
    } else if (form?.message) {
        toast.error(form.message);
    }
});

function applyQuery(value: string) {
    // Clean up datatable and wrapper BEFORE changing filter
    const wrapper = document.querySelector('.datatable-wrapper');
    if (wrapper && wrapper.parentNode) {
        wrapper.parentNode.removeChild(wrapper);
    }
    filter.set(value);
}
</script>

<Toaster />

<nav class="bg-white border-gray-200 dark:bg-gray-900">
    <div
        class="flex flex-wrap justify-between items-center mx-auto max-w-screen-xl p-4"
    >
        <a href="/" class="flex items-center space-x-3 rtl:space-x-reverse">
            <img
                src="https://flowbite.com/docs/images/logo.svg"
                class="h-8"
                alt="Flowbite Logo"
            />
            <span
                class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white"
                >count: {data.already_vote_count}</span
            >
        </a>
        <div class="flex items-center space-x-6 rtl:space-x-reverse">
            <a
                href="tel:5541251234"
                class="text-sm text-gray-500 dark:text-white hover:underline"
                >{data.session.user.email}</a
            >
            <form method="POST" action="?/logout">
                <button
                    type="submit"
                    class="text-sm text-blue-600 dark:text-blue-500 hover:underline"
                    >Logout</button
                >
            </form>
        </div>
    </div>
</nav>
<nav class="bg-gray-200 dark:bg-gray-700">
    <div class="max-w-screen-xl px-4 py-3 mx-auto">
        <div class="flex items-center">
            <ul
                class="flex flex-row font-medium mt-0 space-x-8 rtl:space-x-reverse text-sm"
            >
                <li>
                    <a
                        href="/"
                        on:click|preventDefault={() => applyQuery("all")}
                        class="text-gray-900 dark:text-white hover:underline {$filter ===
                        'all'
                            ? 'font-bold underline'
                            : ''}"
                        aria-current="page">All</a
                    >
                </li>
                <li>
                    <a
                        href="/"
                        on:click|preventDefault={() => applyQuery("voted_yes")}
                        class="text-gray-900 dark:text-white hover:underline {$filter ===
                        'voted_yes'
                            ? 'font-bold underline'
                            : ''}">Yes Choice</a
                    >
                </li>
                <li>
                    <a
                        href="/"
                        on:click|preventDefault={() => applyQuery("voted_no")}
                        class="text-gray-900 dark:text-white hover:underline {$filter ===
                        'voted_no'
                            ? 'font-bold underline'
                            : ''}">No Choice</a
                    >
                </li>
                <li>
                    <a
                        href="/"
                        on:click|preventDefault={() => applyQuery("skipped")}
                        class="text-gray-900 dark:text-white hover:underline {$filter ===
                        'skipped'
                            ? 'font-bold underline'
                            : ''}">Skipped</a
                    >
                </li>
                <li>
                    <a
                        href="/"
                        class="text-gray-900 dark:text-white hover:underline"
                        >Rules</a
                    >
                </li>
            </ul>
        </div>
    </div>
</nav>

<div class="dark:bg-gray-900 dark:text-white bg-gray-300">
    <div class="container mx-auto p-1 mt-3 mb-10">
       {#key $filter}
           <SelectionTable filteredTexts={filteredTexts} />
       {/key}
    </div>
</div>

<style lang="postcss">
    @reference "tailwindcss";
    :global(html) {
        background-color: theme(--color-gray-100);
    }

    /* Force border between datatable rows, override simple-datatables */
    :global(#selection-table tbody tr) {
        border-bottom: 1px solid #e5e7eb !important; /* Tailwind gray-200 */
    }
    :global(.dark #selection-table tbody tr) {
        border-bottom: 1px solid #374151 !important; /* Tailwind gray-700 */
    }
</style>
