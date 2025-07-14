<script lang="ts">
    import { Toaster, toast } from "svelte-sonner";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { enhance } from "$app/forms";
    import { flip } from "svelte/animate";

    export let data;
    export let form;

    // Variabel reaktif untuk menyimpan status filter dan sort dari URL
    let currentFilter: string;
    let currentSort: string;

    $: {
        currentFilter = $page.url.searchParams.get("filter") || "all";
        currentSort = $page.url.searchParams.get("sort") || "id_asc";
    }

    // Fungsi untuk mengubah parameter URL tanpa reload halaman penuh
    function applyQuery(key: string, value: string) {
        const searchParams = new URLSearchParams($page.url.searchParams);
        searchParams.set(key, value);
        goto(`?${searchParams.toString()}`, {
            keepFocus: true,
            noScroll: true,
        });
    }

    onMount(() => {
        if (form?.success) {
            toast.success(form.message);
        } else if (form?.message) {
            toast.error(form.message);
        }
        if (
            document.getElementById("selection-table") &&
            typeof simpleDatatables.DataTable !== "undefined"
        ) {
            let multiSelect = true;
            let rowNavigation = false;
            let table = null;

            const resetTable = function () {
                if (table) {
                    table.destroy();
                }

                const options = {
                    rowRender: (row, tr, _index) => {
                        if (!tr.attributes) {
                            tr.attributes = {};
                        }
                        if (!tr.attributes.class) {
                            tr.attributes.class = "";
                        }
                        if (row.selected) {
                            tr.attributes.class += " selected";
                        } else {
                            tr.attributes.class = tr.attributes.class.replace(
                                " selected",
                                ""
                            );
                        }
                        return tr;
                    },
                };
                if (rowNavigation) {
                    options.rowNavigation = true;
                    options.tabIndex = 1;
                }

                table = new simpleDatatables.DataTable(
                    "#selection-table",
                    options
                );

                // Mark all rows as unselected
                table.data.data.forEach((data) => {
                    data.selected = false;
                });

                table.on("datatable.selectrow", (rowIndex, event) => {
                    event.preventDefault();
                    const row = table.data.data[rowIndex];
                    if (row.selected) {
                        row.selected = false;
                    } else {
                        if (!multiSelect) {
                            table.data.data.forEach((data) => {
                                data.selected = false;
                            });
                        }
                        row.selected = true;
                    }
                    table.update();
                });
            };

            // Row navigation makes no sense on mobile, so we deactivate it and hide the checkbox.
            const isMobile = window.matchMedia("(any-pointer:coarse)").matches;
            if (isMobile) {
                rowNavigation = false;
            }

            resetTable();
        }
    });
</script>

<Toaster />
<p class="text-2xl font-bold bg-gray-900 text-white p-4">TEST</p>
<div class="container mx-auto p-1">
    <table id="selection-table">
        <thead>
            <tr>
                <th
                    class="bg-gray-50 dark:bg-gray-700 text-2xl text-gray-50 dark:text-gray-400 hover:bg-gray-300"
                >
                    <span class="flex items-center">
                        ID
                        <svg
                            class="w-8 h-8 ms-1"
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
                    class="bg-gray-50 dark:bg-gray-700 text-2xl text-gray-50 dark:text-gray-400 hover:bg-gray-300"
                >
                    <span class="flex items-center">
                        Comment Text
                        <svg
                            class="w-8 h-8 ms-1"
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
                    class="bg-gray-50 dark:bg-gray-700 text-2xl text-gray-50 dark:text-gray-400 hover:bg-gray-300"
                >
                    <span class="flex items-center">
                        Action
                        <svg
                            class="w-8 h-8 ms-1"
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
                    <tr
                        class="text-xl text-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 dark:hover:text-gray-50 cursor-pointer"
                    >
                        <td class="font-medium whitespace-nowrap">{item.id}</td>
                        <td><p class="">{item.text_content}</p></td>
                        <td>
                            {#if item.votes.length > 0}
                                <span
                                    class="vote-status"
                                    class:yes={item.votes.vote}
                                    class:no={!item.votes.vote}
                                >
                                    Voted: {item.votes.vote ? "Yes" : "No"}
                                </span>
                                <form method="POST" action="?/undoVote">
                                    <input
                                        type="hidden"
                                        name="text_id"
                                        value={item.id}
                                    />
                                    <button
                                        type="submit"
                                        name="undoVote"
                                        class="btn-undo">Undo</button
                                    >
                                </form>
                            {:else}
                                <div
                                    class="inline-flex rounded-md shadow-xs"
                                    role="group"
                                >
                                    <form
                                        method="POST"
                                        action="?/vote"
                                        class="inline"
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
                                            class="btn-yes relative inline-flex items-center justify-center w-[100px] p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-teal-300 to-lime-300 group-hover:from-teal-300 group-hover:to-lime-300 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-lime-200 dark:focus:ring-lime-800"
                                        >
                                            <span
                                                class="text-xl relative px-8 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                            >
                                                Yes
                                            </span>
                                        </button>
                                    </form>
                                    <form
                                        method="POST"
                                        action="?/vote"
                                        class="inline"
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
                                            class="btn-no relative inline-flex items-center justify-center w-[100px] p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-red-200 via-red-300 to-yellow-200 group-hover:from-red-200 group-hover:via-red-300 group-hover:to-yellow-200 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-red-100 dark:focus:ring-red-400"
                                        >
                                            <span
                                                class="text-xl relative px-8 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent"
                                            >
                                                No
                                            </span>
                                        </button>
                                    </form>
                                </div>
                            {/if}
                        </td>
                    </tr>
                {/each}
            {:else}{/if}
        </tbody>
    </table>
</div>

<div class="controls-container">
    <div class="control-group">
        <span>Filter:</span>
        <button
            class:active={currentFilter === "all"}
            on:click={() => applyQuery("filter", "all")}>All</button
        >
        <button
            class:active={currentFilter === "unvoted"}
            on:click={() => applyQuery("filter", "unvoted")}>Unvoted</button
        >
        <button
            class:active={currentFilter === "voted_yes"}
            on:click={() => applyQuery("filter", "voted_yes")}>Yes</button
        >
        <button
            class:active={currentFilter === "voted_no"}
            on:click={() => applyQuery("filter", "voted_no")}>No</button
        >
    </div>

    <div class="control-group">
        <span>Sort by ID:</span>
        <button
            class:active={currentSort === "id_asc"}
            on:click={() => applyQuery("sort", "id_asc")}>Asc</button
        >
        <button
            class:active={currentSort === "id_desc"}
            on:click={() => applyQuery("sort", "id_desc")}>Desc</button
        >
    </div>
</div>

{#if data.texts.length > 0}
    <div class="card-list">
        {#each data.texts as item (item.id)}
            <div
                class="card"
                class:voted={item.votes.length > 0}
                animate:flip={{ duration: 300 }}
            >
                <p class="text-content">
                    <span class="text-id">ID: {item.id}</span>
                    {item.text_content}
                </p>

                <div class="actions">
                    {#if item.votes.length > 0}
                        <span
                            class="vote-status"
                            class:yes={item.votes.vote}
                            class:no={!item.votes.vote}
                        >
                            Voted: {item.votes.vote ? "Yes" : "No"}
                        </span>
                        <form method="POST" action="?/undoVote">
                            <input
                                type="hidden"
                                name="text_id"
                                value={item.id}
                            />
                            <button
                                type="submit"
                                name="undoVote"
                                class="btn-undo">Undo</button
                            >
                        </form>
                    {:else}
                        <form method="POST" action="?/vote">
                            <input
                                type="hidden"
                                name="text_id"
                                value={item.id}
                            />
                            <button
                                type="submit"
                                name="vote"
                                value="yes"
                                class="btn-yes">Yes</button
                            >
                        </form>
                        <form method="POST" action="?/vote">
                            <input
                                type="hidden"
                                name="text_id"
                                value={item.id}
                            />
                            <button
                                type="submit"
                                name="vote"
                                value="no"
                                class="btn-no">No</button
                            >
                        </form>
                    {/if}
                </div>
            </div>
        {/each}
    </div>
{:else}
    <div class="card empty-state">
        <p>Tidak ada data yang cocok dengan filter Anda.</p>
    </div>
{/if}

<style lang="postcss">
    @reference "tailwindcss";
    :global(html) {
        background-color: theme(--color-gray-100);
    }
</style>
