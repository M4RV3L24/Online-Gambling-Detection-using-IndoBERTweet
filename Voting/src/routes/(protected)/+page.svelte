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

    // Make texts reactive for instant UI updates
    let allTexts = data?.texts ? data.texts.map(t => ({ ...t, votes: [...t.votes] })) : [];
    let tableVersion = 0; // Force table re-render
    
    // Pagination settings for large datasets
    let currentPage = 1;
    let itemsPerPage = 300; // Default items per page
    let itemsPerPageOptions = [100, 200, 300, 500, 1000]; // Available options
    
    // Calculate pagination
    $: totalPages = Math.ceil((filteredTextsAll?.length || 0) / itemsPerPage);
    $: startIndex = (currentPage - 1) * itemsPerPage;
    $: endIndex = startIndex + itemsPerPage;
    
    // Calculate real-time vote counts
    $: yesVoteCount = allTexts.filter((t) => {
        return t.votes.some((v) => 
            v.user_id === data.session.user.id && 
            v.vote === true &&
            (!v.skip || v.skip === 0)
        );
    }).length;
    
    $: noVoteCount = allTexts.filter((t) => {
        return t.votes.some((v) => 
            v.user_id === data.session.user.id && 
            v.vote === false &&
            (!v.skip || v.skip === 0)
        );
    }).length;
    
    $: skippedCount = allTexts.filter((t) => {
        return t.votes.some((v) => 
            v.user_id === data.session.user.id && 
            v.skip === 1
        );
    }).length;
    
    $: totalVoteCount = yesVoteCount + noVoteCount + skippedCount;
    
    // Debug: Log data structure and filtering
    $: {
        // console.log('=== DEBUGGING DATA ===');
        // console.log('Total allTexts:', allTexts.length);
        // console.log('Current filter:', $filter);
        // console.log('User ID:', data?.session?.user?.id);
        
        // Sample first few texts for debugging
        if (allTexts.length > 0) {
            // console.log('Sample text structure:', {
            //     id: allTexts[0].id,
            //     hasVotes: allTexts[0].votes?.length || 0,
            //     firstVote: allTexts[0].votes?.[0]
            // });
        }
        
        // Count unvoted texts manually
        const unvotedCount = allTexts.filter((t) => {
            const hasUserVote = t.votes.some((v) => v.user_id === data.session.user.id);
            const hasUserSkip = t.votes.some((v) => v.user_id === data.session.user.id && v.skip === 1);
            const hasNullVote = t.votes.some((v) => v.user_id === data.session.user.id && (v.skip === 0 || v.skip === null) && v.vote === null);
            
            return (!hasUserVote && !hasUserSkip) || hasNullVote;
        }).length;
        
        // console.log('Manual unvoted count:', unvotedCount);
        // console.log('Filtered texts (all):', filteredTextsAll.length);
        // console.log('Filtered texts (paginated):', filteredTexts.length);
        // console.log('Current page:', currentPage, 'of', totalPages);
        // console.log('Showing items:', startIndex + 1, 'to', Math.min(endIndex, filteredTextsAll.length));
        // console.log('=== END DEBUG ===');
    }

    $: filteredTextsAll = allTexts
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
                      // For "all" filter: show texts that have NO user votes at all
                      // OR texts where user has a null vote (incomplete vote)
                      const userVotes = t.votes.filter(v => v.user_id === data.session.user.id);
                      
                      if (userVotes.length === 0) {
                          // No votes from this user at all
                          return true;
                      }
                      
                      // Check if user has any incomplete/null votes
                      return userVotes.some(v => 
                          v.vote === null && (v.skip === 0 || v.skip === null)
                      );
                  }
              })
        : [];

    // Paginated filtered texts for display
    $: filteredTexts = filteredTextsAll.slice(startIndex, endIndex);
    
    // Reset to page 1 when filter changes
    $: if ($filter) {
        currentPage = 1;
    }

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
    }

    onMount(() => {
        if (form?.success) {
            toast.success(form.message);
        } else if (form?.message) {
            toast.error(form.message);
        }
        
        // Initialize Flowbite modals
        if (typeof window !== 'undefined') {
            // Import and initialize Flowbite
            import('flowbite').then((flowbite) => {
                flowbite.initModals();
            }).catch(() => {
                // Fallback: Manual modal handling if Flowbite is not available
                console.log('Flowbite not found, using manual modal handling');
                setupManualModal();
            });
        }
    });

    function setupManualModal() {
        const modal = document.getElementById('default-modal');
        const openButton = document.querySelector('[data-modal-target="default-modal"]');
        const closeButtons = document.querySelectorAll('[data-modal-hide="default-modal"]');
        
        if (openButton && modal) {
            openButton.addEventListener('click', () => {
                modal.classList.remove('hidden');
                modal.classList.add('flex');
            });
        }
        
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            });
        });
        
        // Close on backdrop click
        modal?.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        });
    }


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

    // Pagination functions
    function goToPage(page: number) {
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
            tableVersion++; // Force table re-render
        }
    }

    function nextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            tableVersion++;
        }
    }

    function prevPage() {
        if (currentPage > 1) {
            currentPage--;
            tableVersion++;
        }
    }

    function changeItemsPerPage(newItemsPerPage: number) {
        // Calculate what item we're currently viewing
        const currentItemIndex = (currentPage - 1) * itemsPerPage + 1;
        
        // Update items per page
        itemsPerPage = newItemsPerPage;
        
        // Calculate which page the current item should be on with new page size
        const newPage = Math.ceil(currentItemIndex / itemsPerPage);
        currentPage = Math.min(newPage, Math.ceil(filteredTextsAll.length / itemsPerPage));
        
        // Force table re-render
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
                class="self-center text-xl font-semibold whitespace-nowrap dark:text-white"
                >Total: {totalVoteCount} | Yes: {yesVoteCount} | No: {noVoteCount} | Skip: {skippedCount}</span
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
                    <button
                        data-modal-target="default-modal" 
                        data-modal-toggle="default-modal"
                        class="text-gray-900 dark:text-white hover:underline"
                        type="button"
                        >Rules</button
                    >
                </li>
            </ul>
        </div>
    </div>
</nav>

<div class="dark:bg-gray-900 dark:text-white bg-gray-300">
    <div class="container mx-auto p-1 mt-3 mb-10">
        <!-- Pagination Controls -->
        {#if filteredTextsAll.length > Math.min(...itemsPerPageOptions)}
            <div class="mb-4 flex flex-col sm:flex-row justify-between items-center bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                <div class="mb-2 sm:mb-0">
                    <span class="text-sm text-gray-700 dark:text-gray-300">
                        Showing <span class="font-semibold">{startIndex + 1}</span> to 
                        <span class="font-semibold">{Math.min(endIndex, filteredTextsAll.length)}</span> of 
                        <span class="font-semibold">{filteredTextsAll.length}</span> results
                    </span>
                </div>
                
                <div class="flex items-center space-x-4">
                    <!-- Items per page selector -->
                    <div class="flex items-center space-x-2">
                        <label for="itemsPerPage" class="text-sm text-gray-700 dark:text-gray-300">Show:</label>
                        <select 
                            id="itemsPerPage"
                            bind:value={itemsPerPage}
                            on:change={() => changeItemsPerPage(itemsPerPage)}
                            class="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                        >
                            {#each itemsPerPageOptions as option}
                                <option value={option}>{option}</option>
                            {/each}
                        </select>
                        <span class="text-sm text-gray-700 dark:text-gray-300">per page</span>
                    </div>
                    
                    <!-- Navigation buttons -->
                    <div class="flex items-center space-x-2">
                        <button 
                            on:click={prevPage}
                            disabled={currentPage === 1}
                            class="px-3 py-1 text-sm bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600"
                        >
                            Previous
                        </button>
                        
                        <span class="text-sm text-gray-700 dark:text-gray-300">
                            Page {currentPage} of {totalPages}
                        </span>
                        
                        <button 
                            on:click={nextPage}
                            disabled={currentPage === totalPages}
                            class="px-3 py-1 text-sm bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600"
                        >
                            Next
                        </button>
                    </div>
                </div>
            </div>
        {/if}
        
        {#key `${$filter}-${tableVersion}`}
            <SelectionTable {filteredTexts} currentFilter={$filter} onVoteUpdate={onVoteUpdate} />
        {/key}
    </div>
</div>




<!-- Flowbite Modal for Rules -->



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
