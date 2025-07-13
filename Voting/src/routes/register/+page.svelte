<script lang="ts">
    import { enhance } from "$app/forms";
    import type { ActionData } from "./$types";

    export let form: ActionData;
</script>

<div class="register-container">
    <div class="card">
        <h1 class="header">Buat Akun Baru</h1>
        <p class="description">Daftar untuk mulai memberi label</p>

        <form method="POST" use:enhance>
            <div class="form-group">
                <label for="email">Email</label>
                <input id="email" name="email" type="email" required />
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input id="password" name="password" type="password" required />
            </div>

            {#if form?.message}
                <p class="error-message">{form.message}</p>
            {/if}

            <button type="submit" class="submit-button">Daftar</button>
        </form>
    </div>
</div>

<style>
    /* Anda bisa menyalin gaya dari halaman login atau membuat yang baru */
    .register-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        background-color: #f7fafc;
    }

    .card {
        background: white;
        padding: 2.5rem;
        border-radius: 0.5rem;
        box-shadow:
            0 4px 6px -1px rgb(0 0 0 / 0.1),
            0 2px 4px -2px rgb(0 0 0 / 0.1);
        width: 100%;
        max-width: 400px;
    }

    .header {
        font-size: 1.875rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .description {
        text-align: center;
        color: #718096;
        margin-bottom: 2rem;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #4a5568;
    }

    input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #e2e8f0;
        border-radius: 0.375rem;
        box-sizing: border-box;
    }

    .submit-button {
        width: 100%;
        padding: 0.75rem;
        border: none;
        border-radius: 0.375rem;
        background-color: #4299e1;
        color: white;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .submit-button:hover {
        background-color: #3182ce;
    }

    .error-message {
        color: #e53e3e;
        background-color: #fed7d7;
        border: 1px solid #f56565;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
</style>
