<script lang="ts">
    import { Toaster, toast } from "svelte-sonner";

    // Function to load more unvoted data
    async function loadMoreData() {
        if (isLoadingMore || !hasMoreData) return;
        
        isLoadingMore = true;
        // console.log('Loading more data...');
        
        try {
            // Get IDs of texts we already have
            const existingIds = allTexts.map(t => t.id);
            
            const response = await fetch('/api/load-more-texts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    excludeIds: existingIds,
                    limit: 500 // Load 500 more records
                })
            });
            
            if (response.ok) {
                const newData = await response.json();
                if (newData.texts && newData.texts.length > 0) {
                    // console.log(`Loaded ${newData.texts.length} new texts`);
                    // Add new texts to our existing array
                    allTexts = [...allTexts, ...newData.texts.map(t => ({ ...t, votes: [...t.votes] }))];
                    tableVersion++; // Force re-render
                } else {
                    hasMoreData = false;
                    // console.log('No more data available');
                }
            }
        } catch (error) {
            console.error('Failed to load more data:', error);
        } finally {
            isLoadingMore = false;
        }
    }

    // Check if we need to load more data
    function checkAndLoadMoreData() {
        const unvotedCount = allTexts.filter((t) => {
            return (
                (!t.votes.some((v) => v.user_id === data.session.user.id) &&
                    !t.votes.some((v) => v.user_id === data.session.user.id && v.skip === 1)) ||
                t.votes.some((v) => v.user_id === data.session.user.id && (v.skip === 0 || v.skip === null) && v.vote === null)
            );
        }).length;
        
        // console.log(`Unvoted count: ${unvotedCount}`);
        
        // Load more data if unvoted count is low
        if (unvotedCount < 200 && hasMoreData && !isLoadingMore) {
            loadMoreData();
        }
    };
    import { onMount } from "svelte";
    import { enhance } from "$app/forms";
    import { flip } from "svelte/animate";
    import SelectionTable from "./SelectionTable.svelte";
    import { writable } from "svelte/store";
    export let data;
    export let form;

    const filter = writable("all");

    // Make texts reactive for instant UI updates
    let allTexts = data?.texts ? data.texts.map(t => ({ ...t, votes: [...t.votes] })) : [];
    let tableVersion = 0; // Force table re-render
    let isLoadingMore = false; // Prevent multiple simultaneous loads
    let hasMoreData = true; // Track if more data is available
    
    // Calculate real-time vote count
    $: currentVoteCount = allTexts.filter((t) => {
        return t.votes.some((v) => 
            v.user_id === data.session.user.id && 
            (v.vote === true || v.vote === false || v.skip === 1)
        );
    }).length;
    
    // Debug: Log initial data
    // console.log('Initial data structure:', { 
    //     dataExists: !!data, 
    //     textsCount: data?.texts?.length || 0, 
    //     allTextsCount: allTexts.length,
    //     firstText: allTexts[0],
    //     userID: data?.session?.user?.id
    // });

    $: filteredTexts = allTexts
        ? allTexts
              .filter((t) => {
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
                          (v) =>
                              v.user_id === data.session.user.id && v.skip === 1
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
              })
              .slice(0, 200)
        : [];

    function onVoteUpdate(textId: number, voteType: 'yes' | 'no' | 'skip' | 'cancel') {
        // console.log('onVoteUpdate called in parent:', { textId, voteType });
        
        // Find the text item
        const tIdx = allTexts.findIndex(t => t.id === textId);
        // console.log('Text index found:', tIdx, 'in array of length:', allTexts.length);
        
        if (tIdx === -1) {
            console.error('Text not found with id:', textId);
            return;
        }
        
        const userId = data.session.user.id;
        // console.log('User ID:', userId);
        
        // Find or create the vote object for this user
        let vIdx = allTexts[tIdx].votes.findIndex(v => v.user_id === userId);
        // console.log('Vote index found:', vIdx);
        
        if (voteType === 'cancel') {
            if (vIdx !== -1) {
                allTexts[tIdx].votes.splice(vIdx, 1);
                // console.log('Vote removed');
            }
        } else if (voteType === 'skip') {
            if (vIdx === -1) {
                allTexts[tIdx].votes.push({ user_id: userId, vote: null, skip: 1 });
                // console.log('Skip vote added');
            } else {
                allTexts[tIdx].votes[vIdx].vote = null;
                allTexts[tIdx].votes[vIdx].skip = 1;
                // console.log('Vote updated to skip');
            }
        } else {
            if (vIdx === -1) {
                allTexts[tIdx].votes.push({ user_id: userId, vote: voteType === 'yes', skip: 0 });
                // console.log('New vote added:', voteType);
            } else {
                allTexts[tIdx].votes[vIdx].vote = voteType === 'yes';
                allTexts[tIdx].votes[vIdx].skip = 0;
                // console.log('Vote updated to:', voteType);
            }
        }
        
        // console.log('Before reassignment - allTexts length:', allTexts.length);
        // Force reactivity
        allTexts = [...allTexts];
        tableVersion++; // Force table re-render
        // console.log('After reassignment - allTexts length:', allTexts.length);
        // console.log('Table version updated to:', tableVersion);
        // console.log('Updated vote count:', currentVoteCount);
        // console.log('Reactivity update complete');
        
        // Check if we need to load more data
        setTimeout(() => checkAndLoadMoreData(), 100);
    }

    onMount(() => {
        if (form?.success) {
            toast.success(form.message);
        } else if (form?.message) {
            toast.error(form.message);
        }
    });

    function applyQuery(value: string) {
        // Clean up datatable and wrapper BEFORE changing filter
        const wrapper = document.querySelector(".datatable-wrapper");
        if (wrapper && wrapper.parentNode) {
            wrapper.parentNode.removeChild(wrapper);
        }
        filter.set(value);
        // Force table re-render even if same filter is applied
        tableVersion++;
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
                >count: {currentVoteCount}</span
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
        {#if isLoadingMore}
            <div class="mb-4 p-4 bg-blue-100 dark:bg-blue-900 rounded-lg text-center">
                <p class="text-blue-800 dark:text-blue-200">
                    Loading more data... 🔄
                </p>
            </div>
        {/if}
        
        {#key `${$filter}-${tableVersion}`}
            <SelectionTable {filteredTexts} currentFilter={$filter} onVoteUpdate={onVoteUpdate} />
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
