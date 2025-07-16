<script lang="ts">
import { Toaster, toast } from "svelte-sonner";
import { onMount, afterUpdate } from "svelte";
import { enhance } from "$app/forms";
import { flip } from "svelte/animate";
import * as simpleDatatables from "simple-datatables";
import "simple-datatables/dist/style.css";

export let data;
export let form;

let tableInstance;
function initDatatable() {
    if (tableInstance) {
        tableInstance.destroy();
    }
    const tableElement = document.getElementById("selection-table");
    if (tableElement) {
        tableInstance = new simpleDatatables.DataTable(tableElement, 
            {
    paging: true, // enable or disable pagination
    perPage: 10, // set the number of rows per page
    perPageSelect: [5, 10, 20, 50], // set the number of rows per page options
    firstLast: true, // enable or disable the first and last buttons
    nextPrev: true, // enable or disable the next and previous buttons

        });
    }
}

afterUpdate(() => {
    initDatatable();
});

onMount(() => {
    if (form?.success) {
        toast.success(form.message);
    } else if (form?.message) {
        toast.error(form.message);
    }
    initDatatable();
});
</script>

<Toaster />



<nav class="bg-white border-gray-200 dark:bg-gray-900">
    <div class="flex flex-wrap justify-between items-center mx-auto max-w-screen-xl p-4">
        <a href="https://flowbite.com" class="flex items-center space-x-3 rtl:space-x-reverse">
            <img src="https://flowbite.com/docs/images/logo.svg" class="h-8" alt="Flowbite Logo" />
            <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">count: {data.already_vote_count}</span>
        </a>
        <div class="flex items-center space-x-6 rtl:space-x-reverse">
            <a href="tel:5541251234" class="text-sm  text-gray-500 dark:text-white hover:underline">{data.session.user.email}</a>
            <form method="POST" action="?/logout">
                <button type="submit" class="text-sm  text-blue-600 dark:text-blue-500 hover:underline">Logout</button>
            </form>
            
        </div>
    </div>
</nav>


<div class="container mx-auto p-1 mt-3 mb-10">
    <table id="selection-table">
        <thead>
            <tr >
                <th>
                    <span class="flex items-center">
                        ID
                        <svg
                            class="w-4 h-4 ms-1"
                            aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke="currentColor"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="m8 15 4 4 4-4m0-6-4-4-4 4"
                            />
                        </svg>
                    </span>
                </th>
                <th>
                    <span class="flex items-center">
                        Comment Text
                        <svg
                            class="w-4 h-4 ms-1"
                            aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke="currentColor"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="m8 15 4 4 4-4m0-6-4-4-4 4"
                            />
                        </svg>
                    </span>
                </th>
                <th>
                    <span class="flex items-center">
                        Action
                        <svg
                            class="w-4 h-4 ms-1"
                            aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke="currentColor"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="m8 15 4 4 4-4m0-6-4-4-4 4"
                            />
                        </svg>
                    </span>
                </th>
            </tr>
        </thead>
        <tbody>
            {#if data.texts.length > 0}
                {#each data.texts as item (item.id)}
                    <tr animate:flip
                        class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                    >
                        <td
                            class=" mx-auto font-medium text-gray-900 whitespace-nowrap dark:text-white"
                            >
                            {item.id}
                        </td>
                        <td class=" text-gray-900 dark:text-white"><p class="">{item.text_content}</p></td>
                        <td class="">
                            <div
                                class="inline-flex rounded-md shadow-xs"
                                role="group"
                            >
                                <form
                                    method="POST"
                                    action="?/vote"
                                    class="inline"
                                    use:enhance
                                >
                                    <input
                                        type="hidden"
                                        name="text_id"
                                        value={item.id}
                                    />
                                    <button
                                        type="submit"
                                        name="vote"
                                        value="yes"
                                        class="btn-yes relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-teal-300 to-lime-300 group-hover:from-teal-300 group-hover:to-lime-300 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-lime-200 dark:focus:ring-lime-800"
                                    >
                                        <span
                                            class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                        >
                                            Yes
                                        </span>
                                    </button>
                                </form>
                                <form
                                    method="POST"
                                    action="?/vote"
                                    class="inline"
                                    use:enhance
                                >
                                    <input
                                        type="hidden"
                                        name="text_id"
                                        value={item.id}
                                    />
                                    <button
                                        type="submit"
                                        name="vote"
                                        value="no"
                                        class="btn-no relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-red-200 via-red-300 to-yellow-200 group-hover:from-red-200 group-hover:via-red-300 group-hover:to-yellow-200 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-red-100 dark:focus:ring-red-400"
                                    >
                                        <span
                                            class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                        >
                                            No
                                        </span>
                                    </button>
                                </form>
                            </div>
                        </td>
                    </tr>
                {/each}
            {:else}{/if}
        </tbody>
    </table>
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
