<script lang="ts">
    import { onMount, onDestroy, tick } from "svelte";
    import { simpleDatatables } from "../../lib/simpleDatatables";
    export let filteredTexts: any[];
    export let currentFilter: string;
    
    // Callback to update parent state instantly
    export let onVoteUpdate: (textId: number, voteType: 'yes' | 'no' | 'skip' | 'cancel') => void;

    let tableInstance: any;

    onMount(async () => {
        await tick();
        initDatatable();
    });

    $: if (filteredTexts) {
        tick().then(() => {
            initDatatable();
        });
    }

    function initDatatable() {
        if (typeof window === "undefined") return; // Ensure this runs only in the browser
        // Clean up previous instance if it exists
        if (tableInstance) {
            tableInstance.destroy();
            const wrapper = document.querySelector(".datatable-wrapper");
            if (wrapper && wrapper.parentNode) {
                wrapper.parentNode.removeChild(wrapper);
            }
        }
        const tableElement = document.getElementById(
            "selection-table"
        ) as HTMLTableElement | null;
        if (tableElement) {
            tableInstance = new simpleDatatables.DataTable(tableElement, {
                paging: true,
                perPage: 10,
                perPageSelect: [5, 10, 20, 50, 100, 200],
                firstLast: true,
                nextPrev: true,
            });
            
            // Add event delegation for vote buttons after DataTable is initialized
            setupEventDelegation();
        }
    }

    function setupEventDelegation() {
        if (typeof window === "undefined") return; // Ensure this runs only in the browser
        // Remove existing listeners first
        document.removeEventListener('click', handleDelegatedClick);
        // Add new listener
        document.addEventListener('click', handleDelegatedClick);
    }

    function handleDelegatedClick(event: Event) {
        const target = event.target as HTMLElement;
        const button = target.closest('button[data-vote-action]') as HTMLButtonElement;
        
        if (!button) return;
        
        event.preventDefault();
        event.stopPropagation();
        
        const textId = parseInt(button.getAttribute('data-text-id') || '0');
        const voteType = button.getAttribute('data-vote-action') as 'yes' | 'no' | 'skip' | 'cancel';
        
        // console.log('Button clicked via delegation:', { textId, voteType });
        
        if (textId && voteType) {
            handleVote(textId, voteType);
        }
    }

    onDestroy(() => {
        if (typeof window === "undefined") return; // Ensure this runs only in the browser
        // Remove event listener
        document.removeEventListener('click', handleDelegatedClick);
        
        if (tableInstance) {
            tableInstance.destroy();
            // Remove datatable wrapper if it exists
            const wrapper = document.querySelector(".datatable-wrapper");
            if (wrapper && wrapper.parentNode) {
                wrapper.parentNode.removeChild(wrapper);
            }
        }
    });

    // Instant UI update and background fetch
    async function handleVote(textId: number, voteType: 'yes' | 'no' | 'skip' | 'cancel') {
        // console.log('handleVote called:', { textId, voteType });
        
        // Check if onVoteUpdate function exists
        if (!onVoteUpdate) {
            console.error('onVoteUpdate function is not provided!');
            return;
        }
        
        // Update UI immediately
        // console.log('Calling onVoteUpdate...');
        onVoteUpdate(textId, voteType);
        // console.log('onVoteUpdate called successfully');
        
        // Send request to server in background
        const formData = new FormData();
        formData.append('text_id', textId.toString());
        
        let actionPath = '';
        if (voteType === 'cancel') {
            actionPath = '?/cancel-vote';
        } else if (voteType === 'skip') {
            actionPath = '?/skip';
        } else {
            actionPath = '?/vote';
            formData.append('vote', voteType);
        }
        
        // console.log('Sending fetch request to:', window.location.pathname + actionPath);
        
        try {
            const response = await fetch(window.location.pathname + actionPath, {
                method: 'POST',
                body: formData,
                headers: { 'x-sveltekit-action': 'true' }
            });
            // console.log('Server response:', response.status, response.statusText);
        } catch (e) {
            console.error('Vote failed:', e);
        }
    }
</script>

<table id="selection-table">
    <thead>
        <tr>
            <th
                class="bg-white text-gray-800 dark:bg-gray-700 dark:text-gray-200"
            >
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
            <th
                class="bg-white text-gray-800 dark:bg-gray-700 dark:text-gray-200"
            >
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
            <th
                class="bg-white text-gray-800 dark:bg-gray-700 dark:text-gray-200"
            >
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
        {#if filteredTexts.length > 0}
            {#each filteredTexts as item (item.id)}
                <tr class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer odd:dark:bg-gray-950 odd:bg-gray-200">
                    <td class="mx-auto font-medium text-gray-900 whitespace-nowrap dark:text-white">{item.id}</td>
                    <td class="text-gray-900 dark:text-white"><p>{item.text_content}</p></td>
                    <td>
                        <!-- ...existing action buttons... -->
                        <div
                            class="inline-flex rounded-md shadow-xs"
                            role="group"
                        >
                            {#if currentFilter === "all"}
                                <button
                                    type="button"
                                    data-vote-action="yes"
                                    data-text-id={item.id}
                                    class="btn-yes relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-teal-300 to-lime-300 group-hover:from-teal-300 group-hover:to-lime-300 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-lime-200 dark:focus:ring-lime-800"
                                >
                                    <span
                                        class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                    >
                                        Yes
                                    </span>
                                </button>
                                <button
                                    type="button"
                                    data-vote-action="no"
                                    data-text-id={item.id}
                                    class="btn-no relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-red-200 via-red-300 to-yellow-200 group-hover:from-red-200 group-hover:via-red-300 group-hover:to-yellow-200 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-red-100 dark:focus:ring-red-400"
                                >
                                    <span
                                        class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                    >
                                        No
                                    </span>
                                </button>
                                <button
                                    type="button"
                                    data-vote-action="skip"
                                    data-text-id={item.id}
                                    class="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800"
                                >
                                    <span
                                        class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                    >
                                        Skip
                                    </span>
                                </button>
                            {:else}
                                <button
                                    type="button"
                                    data-vote-action="cancel"
                                    data-text-id={item.id}
                                    class="py-2.5 px-1 me-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
                                >
                                    <span
                                        class="text-md relative px-10 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                    >
                                        Cancel
                                    </span>
                                </button>
                            {/if}
                        </div>
                    </td>
                </tr>
            {/each}
        {:else}{/if}
    </tbody>
</table>
