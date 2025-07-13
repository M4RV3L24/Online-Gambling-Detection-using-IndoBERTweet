<script lang="ts">
	import { Toaster, toast } from 'svelte-sonner';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { enhance } from '$app/forms';
	import { flip } from 'svelte/animate';

	export let data;
	export let form;

	// Variabel reaktif untuk menyimpan status filter dan sort dari URL
	let currentFilter: string;
	let currentSort: string;

	$: {
		currentFilter = $page.url.searchParams.get('filter') || 'all';
		currentSort = $page.url.searchParams.get('sort') || 'id_asc';
	}

	console.log(data.texts);

	// Tampilkan notifikasi toast setelah aksi form berhasil
	onMount(() => {
		if (form?.success) {
			toast.success(form.message);
		} else if (form?.message) {
			toast.error(form.message);
		}
	});

	// Fungsi untuk mengubah parameter URL tanpa reload halaman penuh
	function applyQuery(key: string, value: string) {
		const searchParams = new URLSearchParams($page.url.searchParams);
		searchParams.set(key, value);
		goto(`?${searchParams.toString()}`, { keepFocus: true, noScroll: true });
	}
</script>

<Toaster />

<div class="controls-container">
	<div class="control-group">
		<span>Filter:</span>
		<button class:active={currentFilter === 'all'} on:click={() => applyQuery('filter', 'all')}>All</button>
		<button class:active={currentFilter === 'unvoted'} on:click={() => applyQuery('filter', 'unvoted')}>Unvoted</button>
		<button class:active={currentFilter === 'voted_yes'} on:click={() => applyQuery('filter', 'voted_yes')}>Yes</button>
		<button class:active={currentFilter === 'voted_no'} on:click={() => applyQuery('filter', 'voted_no')}>No</button>
	</div>

	<div class="control-group">
		<span>Sort by ID:</span>
		<button class:active={currentSort === 'id_asc'} on:click={() => applyQuery('sort', 'id_asc')}>Asc</button>
		<button class:active={currentSort === 'id_desc'} on:click={() => applyQuery('sort', 'id_desc')}>Desc</button>
	</div>
</div>

{#if data.texts.length > 0}
	<div class="card-list">
		{#each data.texts as item (item.id)}
			<div class="card" class:voted={item.votes.length > 0} animate:flip={{ duration: 300 }}>
				<p class="text-content">
					<span class="text-id">ID: {item.id}</span>
					{item.text_content}
				</p>

				<div class="actions">
					{#if item.votes.length > 0}
						<span class="vote-status" class:yes={item.votes.vote} class:no={!item.votes.vote}>
							Voted: {item.votes.vote? 'Yes' : 'No'}
						</span>
						<form method="POST" action="?/undoVote">
							<input type="hidden" name="text_id" value={item.id} />
							<button type="submit" name="undoVote" class="btn-undo">Undo</button>
						</form>
					{:else}
						<form method="POST" action="?/vote">
							<input type="hidden" name="text_id" value={item.id} />
							<button type="submit" name="vote" value="yes" class="btn-yes">Yes</button>
						</form>
						<form method="POST" action="?/vote">
							<input type="hidden" name="text_id" value={item.id} />
							<button type="submit" name="vote" value="no" class="btn-no">No</button>
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

<style>
	.controls-container {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 2rem;
		background-color: #f0f0f0;
		border-radius: 8px;
		margin-bottom: 2rem;
		flex-wrap: wrap;
		gap: 1rem;
	}
	.control-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.control-group span {
		font-weight: 500;
		margin-right: 0.5rem;
	}
	.control-group button {
		padding: 0.5rem 1rem;
		border: 1px solid #ccc;
		background-color: white;
		cursor: pointer;
		border-radius: 5px;
		transition: all 0.2s ease;
	}
	.control-group button:hover {
		background-color: #e9e9e9;
	}
	.control-group button.active {
		background-color: #4299e1;
		color: white;
		border-color: #4299e1;
	}

	.card-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.card {
		background-color: white;
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
		transition: all 0.2s ease;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.card.voted {
		background-color: #f9f9f9;
		opacity: 0.7;
	}

	.text-id {
		display: block;
		font-size: 0.8rem;
		color: #999;
		margin-bottom: 0.5rem;
	}

	.text-content {
		font-size: 1.1rem;
		line-height: 1.6;
		flex-grow: 1;
	}

	.actions {
		display: flex;
		gap: 1rem;
		align-items: center;
		justify-content: flex-end;
	}

	.vote-status {
		font-weight: bold;
		padding: 0.5rem 1rem;
		border-radius: 5px;
	}
	.vote-status.yes {
		color: #28a745;
		background-color: #eaf6ec;
	}
	.vote-status.no {
		color: #dc3545;
		background-color: #fbe9eb;
	}

	.actions button {
		padding: 0.6rem 1.2rem;
		border: none;
		border-radius: 5px;
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s ease;
	}

	.btn-yes { background-color: #28a745; color: white; }
	.btn-yes:hover { background-color: #218838; }
	.btn-no { background-color: #dc3545; color: white; }
	.btn-no:hover { background-color: #c82333; }
	.btn-undo { background-color: #6c757d; color: white; }
	.btn-undo:hover { background-color: #5a6268; }

	.empty-state {
		text-align: center;
		padding: 3rem;
		color: #666;
	}
</style>