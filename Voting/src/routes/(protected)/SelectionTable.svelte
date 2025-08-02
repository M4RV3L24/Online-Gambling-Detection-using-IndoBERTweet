<script lang="ts">
    import { onMount, onDestroy, tick } from "svelte";
    import { simpleDatatables } from "../../lib/simpleDatatables";
    export let filteredTexts: any[];
    export let currentFilter: string;
    
    // Callback to update parent state instantly
    export let onVoteUpdate: (textId: number, voteType: 'yes' | 'no' | 'skip' | 'cancel') => void;

    let tableInstance: any;
    let initTimeout: any;
    let isTableInitialized = false;
    let lastFilteredTexts: any[] = [];
    let isProcessing = false; // Add flag to prevent overlapping operations
    
    // Performance cache for button templates
    let buttonTemplateCache = new Map();
    
    // Pre-compile button templates for better performance
    function getButtonTemplate(itemId: number, isAllFilter: boolean) {
        const cacheKey = `${isAllFilter ? 'all' : 'voted'}-template`;
        
        if (!buttonTemplateCache.has(cacheKey)) {
            const template = isAllFilter ? 
                `<button type="button" data-vote-action="yes" data-text-id="ID_PLACEHOLDER" class="btn-yes relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-teal-300 to-lime-300 group-hover:from-teal-300 group-hover:to-lime-300 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-lime-200 dark:focus:ring-lime-800">
                    <span class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">Yes</span>
                </button>
                <button type="button" data-vote-action="no" data-text-id="ID_PLACEHOLDER" class="btn-no relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-red-200 via-red-300 to-yellow-200 group-hover:from-red-200 group-hover:via-red-300 group-hover:to-yellow-200 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-red-100 dark:focus:ring-red-400">
                    <span class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">No</span>
                </button>
                <button type="button" data-vote-action="skip" data-text-id="ID_PLACEHOLDER" class="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800">
                    <span class="text-md relative px-6 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">Skip</span>
                </button>` :
                `<button type="button" data-vote-action="cancel" data-text-id="ID_PLACEHOLDER" class="py-2.5 px-1 me-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700">
                    <span class="text-md relative px-10 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">Cancel</span>
                </button>`;
            
            buttonTemplateCache.set(cacheKey, template);
        }
        
        return buttonTemplateCache.get(cacheKey).replace(/ID_PLACEHOLDER/g, itemId);
    }

    onMount(async () => {
        if (typeof window === "undefined") return; // Ensure this runs only in the browser
        
        await tick();
        await populateTableBody(); // Wait for table body to be fully populated
        initDatatable();
    });

    // Reactive statement to handle data changes
    $: if (filteredTexts && typeof window !== "undefined" && !isProcessing) {
        const hasChanged = JSON.stringify(filteredTexts) !== JSON.stringify(lastFilteredTexts);
        if (hasChanged) {
            lastFilteredTexts = [...filteredTexts];
            if (!isTableInitialized) {
                // Initial table creation
                if (initTimeout) clearTimeout(initTimeout);
                initTimeout = setTimeout(() => {
                    tick().then(async () => {
                        isProcessing = true;
                        await populateTableBody(); // Wait for completion
                        initDatatable();
                        isProcessing = false;
                    });
                }, 20);
            } else {
                // Update existing table
                rebuildTable();
            }
        }
    }

    function populateTableBody() {
        if (typeof window === "undefined" || isProcessing) return; // Prevent overlapping calls
        
        const tbody = document.querySelector('#selection-table tbody');
        if (!tbody) return;
        
        // Performance optimization: Use DocumentFragment for batch DOM operations
        const fragment = document.createDocumentFragment();
        const isAllFilter = currentFilter === "all";
        
        // Clear existing content
        tbody.innerHTML = '';
        
        // Optimized batch size: Use larger batches for better performance with large datasets
        const batchSize = Math.min(500, filteredTexts.length); // Adaptive batch size
        let currentIndex = 0;
        
        return new Promise<void>((resolve) => {
            const processBatch = () => {
                const endIndex = Math.min(currentIndex + batchSize, filteredTexts.length);
                
                for (let i = currentIndex; i < endIndex; i++) {
                    const item = filteredTexts[i];
                    const row = document.createElement('tr');
                    row.className = 'hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer odd:dark:bg-gray-950 odd:bg-gray-200';
                    
                    // Use optimized template with caching
                    const buttonHTML = getButtonTemplate(item.id, isAllFilter);
                    
                    row.innerHTML = `
                        <td class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white text-center">${item.id}</td>
                        <td class="w-[75%] min-w-52 max-w-[75%] px-4 py-2 text-gray-900 dark:text-white"><p class="break-words">${item.text_content}</p></td>
                        <td class="px-4 py-2">
                            <div class="inline-flex rounded-md shadow-xs" role="group">
                                ${buttonHTML}
                            </div>
                        </td>
                    `;
                    
                    fragment.appendChild(row);
                }
                
                currentIndex = endIndex;
                
                // Continue processing if there are more rows
                if (currentIndex < filteredTexts.length) {
                    // Use requestAnimationFrame to avoid blocking the UI
                    requestAnimationFrame(processBatch);
                } else {
                    // All done, append to DOM in one operation
                    tbody.appendChild(fragment);
                    resolve(); // Signal completion
                }
            };
            
            // Start batch processing
            if (filteredTexts.length > 0) {
                processBatch();
            } else {
                resolve(); // No data to process
            }
        });
    }

    function initDatatable() {
        if (typeof window === "undefined") return; // Ensure this runs only in the browser
        
        // More aggressive cleanup to prevent duplicate headers
        const cleanupAllDataTables = () => {
            // Destroy any existing instances
            if (tableInstance) {
                try {
                    tableInstance.destroy();
                } catch (e) {
                    // Ignore destroy errors
                }
                tableInstance = null;
            }
            
            // Remove all DataTable wrappers and containers
            const selectors = [
                ".datatable-wrapper", 
                ".datatable-container", 
                ".dataTable-wrapper",
                ".dataTable-container"
            ];
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    if (element && element.parentNode) {
                        // Move any child tables back to parent before removing wrapper
                        const tables = element.querySelectorAll('table');
                        tables.forEach(table => {
                            if (element.parentNode) {
                                element.parentNode.insertBefore(table, element);
                            }
                        });
                        element.parentNode.removeChild(element);
                    }
                });
            });
        };
        
        // Clean up previous instance if it exists
        setTimeout(() => {
            cleanupAllDataTables();
            
            const tableElement = document.getElementById("selection-table") as HTMLTableElement | null;
            if (tableElement) {
                // Ensure table is not already wrapped
                const existingWrapper = tableElement.closest('.datatable-wrapper, .dataTable-wrapper');
                if (existingWrapper) {
                    const parent = existingWrapper.parentNode;
                    if (parent) {
                        parent.appendChild(tableElement); // Move table out of wrapper
                        parent.removeChild(existingWrapper); // Remove wrapper
                    }
                }

                // Wait a bit more to ensure DOM is clean
                setTimeout(() => {
                    tableInstance = new simpleDatatables.DataTable(tableElement, {
                        paging: true,
                        perPage: 10,
                        perPageSelect: [5, 10, 20, 50, 100, 200],
                        firstLast: true,
                        nextPrev: true,
                    });
                    
                    // Add event delegation for vote buttons after DataTable is initialized
                    setupEventDelegation();
                    isTableInitialized = true;
                    lastFilteredTexts = [...filteredTexts];
                }, 50);
            }
        }, 10);
    }

    function rebuildTable() {
        if (isProcessing) return; // Prevent overlapping rebuilds
        
        // Preserve current pagination state
        const currentPage = tableInstance?.currentPage || 1;
        const perPage = tableInstance?.options?.perPage || 10;
        
        // Update tracking first to prevent infinite loops
        lastFilteredTexts = [...filteredTexts];
        
        // Full table rebuild for filter changes or major data updates
        if (initTimeout) clearTimeout(initTimeout);
        initTimeout = setTimeout(() => {
            tick().then(async () => {
                isProcessing = true;
                
                if (tableInstance) {
                    tableInstance.destroy();
                    
                    // Clean up wrappers
                    const allWrappers = document.querySelectorAll(".datatable-wrapper");
                    allWrappers.forEach(wrapper => {
                        if (wrapper && wrapper.parentNode) {
                            wrapper.parentNode.removeChild(wrapper);
                        }
                    });
                }
                
                // Repopulate table body with new data and wait for completion
                await populateTableBody();
                
                const tableElement = document.getElementById("selection-table") as HTMLTableElement | null;
                if (tableElement) {
                    tableInstance = new simpleDatatables.DataTable(tableElement, {
                        paging: true,
                        perPage: perPage,
                        perPageSelect: [5, 10, 20, 50, 100, 200],
                        firstLast: true,
                        nextPrev: true,
                    });
                    
                    // Restore pagination if possible
                    if (currentPage > 1) {
                        setTimeout(() => {
                            try {
                                const totalPages = Math.ceil(filteredTexts.length / perPage);
                                const targetPage = Math.min(currentPage, totalPages);
                                if (targetPage > 1) {
                                    tableInstance.page(targetPage);
                                }
                            } catch (e) {
                                // Ignore page restoration errors
                            }
                        }, 100);
                    }
                    
                    setupEventDelegation();
                }
                
                isProcessing = false;
            });
        }, 20);
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
        // Make sure this button belongs to our specific table
        const ourTable = document.getElementById('selection-table');
        if (!ourTable || !ourTable.contains(button)) return;
        
        // Also check if the button is within a DataTable wrapper to avoid conflicts
        const datatableWrapper = button.closest('.datatable-wrapper');
        if (!datatableWrapper) return;
        
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
        // Clear any pending initialization
        if (initTimeout) clearTimeout(initTimeout);
        isTableInitialized = false;
        
        // Remove event listener
        document.removeEventListener('click', handleDelegatedClick);
        
        if (tableInstance) {
            try {
                tableInstance.destroy();
            } catch (e) {
                // Ignore destroy errors
            }
            tableInstance = null;
        }
        
        // Clean up all DataTable elements
        const allWrappers = document.querySelectorAll(".datatable-wrapper");
        allWrappers.forEach(wrapper => {
            if (wrapper && wrapper.parentNode) {
                wrapper.parentNode.removeChild(wrapper);
            }
        });
        
        const allContainers = document.querySelectorAll(".datatable-container");
        allContainers.forEach(container => {
            if (container && container.parentNode) {
                container.parentNode.removeChild(container);
            }
        });
        
        // Clear template cache to free memory
        buttonTemplateCache.clear();
    });

    // Instant UI update and background fetch
    async function handleVote(textId: number, voteType: 'yes' | 'no' | 'skip' | 'cancel') {
        // Check if onVoteUpdate function exists
        if (!onVoteUpdate) {
            console.error('onVoteUpdate function is not provided!');
            return;
        }
        
        // Apply visual feedback immediately
        animateRowRemoval(textId);
        
        // Update parent state instantly
        onVoteUpdate(textId, voteType);
        
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
        
        try {
            const response = await fetch(window.location.pathname + actionPath, {
                method: 'POST',
                body: formData,
                headers: { 'x-sveltekit-action': 'true' }
            });
        } catch (e) {
            console.error('Vote failed:', e);
        }
    }
    
    function animateRowRemoval(textId: number) {
        try {
            // Find the row with the specific text ID
            const tableBody = document.querySelector('#selection-table tbody');
            if (!tableBody) return;
            
            const rows = tableBody.querySelectorAll('tr');
            const targetRow = Array.from(rows).find(row => {
                const button = row.querySelector(`[data-text-id="${textId}"]`);
                return button !== null;
            });
            
            if (targetRow) {
                // Add smooth fade-out animation
                (targetRow as HTMLElement).style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                (targetRow as HTMLElement).style.opacity = '0';
                (targetRow as HTMLElement).style.transform = 'scale(0.95)';
                (targetRow as HTMLElement).style.pointerEvents = 'none';
                
                // Remove the row after animation
                setTimeout(() => {
                    try {
                        targetRow.remove();
                    } catch (e) {
                        // Ignore removal errors
                    }
                }, 300);
            }
        } catch (error) {
            console.error('Error animating row removal:', error);
        }
    }
</script>

<table id="selection-table" class="w-full">
    <thead>
        <tr>
            <th
                class="px-4 py-2 bg-white text-gray-800 dark:bg-gray-700 dark:text-gray-200"
            >
                <span class="flex items-center justify-center">
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
                class="w-[75%] min-w-52 max-w-[75%] px-4 py-2 bg-white text-gray-800 dark:bg-gray-700 dark:text-gray-200"
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
                class="px-4 py-2 bg-white text-gray-800 dark:bg-gray-700 dark:text-gray-200"
            >
                <span class="flex items-center justify-center">
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
        <!-- Table body is populated manually via JavaScript to avoid Svelte reactivity issues -->
    </tbody>
</table>

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
