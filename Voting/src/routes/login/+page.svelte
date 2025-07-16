<script lang="ts">
    import { enhance } from "$app/forms";
    import type { ActionData } from "./$types";
    // import { goto } from '$app/navigation';

    // Example: redirect to /dashboard
    // goto('/register');

    // 'form' akan berisi data yang dikembalikan dari action,
    // seperti pesan error jika login gagal.
    export let form: ActionData;
</script>

<section class="bg-gray-50 dark:bg-gray-900">
    <div
        class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0"
    >
        <a
            href="#"
            class="flex items-center mb-6 text-2xl font-semibold text-gray-900 dark:text-white"
        >
            <img
                class="w-8 h-8 mr-2"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg"
                alt="logo"
            />
            Welcome, Please Login to Continue
        </a>
        <div
            class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700"
        >
            <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
                <h1
                    class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white"
                >
                    Sign in to your account
                </h1>
                <form class="space-y-4 md:space-y-6" method="POST" use:enhance>
                    <div>
                        <label
                            for="email"
                            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                            >Your email</label
                        >
                        <input
                            type="email"
                            name="email"
                            id="email"
                            class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            placeholder="name@company.com"
                            required=""
                        />
                    </div>
                    <div>
                        <label
                            for="password"
                            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                            >Password</label
                        >
                        <input
                            type="password"
                            name="password"
                            id="password"
                            placeholder="••••••••"
                            class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            required=""
                        />
                    </div>
                    <button
                        type="submit"
                        class="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                        >Sign in</button
                    >
                    <p
                        class="text-sm font-light text-gray-500 dark:text-gray-400"
                    >
                        Don’t have an account yet? <a
                            href="/register"
                            class="font-medium text-blue-600 hover:underline dark:text-blue-500"
                            >Sign up</a
                        >
                    </p>
                </form>
            </div>
        </div>
    </div>
</section>

<!-- <div class="container">
    <div class="card">
        <h1 class="header">Selamat Datang</h1>
        <p class="description">Silakan masuk untuk melanjutkan</p>

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

            <button type="submit" class="submit-button">Login</button>
        </form>
    </div>
</div> -->

<style>
    .login-container {
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
        box-sizing: border-box; /* Pastikan padding tidak menambah lebar */
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
