<script lang="ts">
    import { enhance } from "$app/forms";
    import type { ActionData } from "./$types";
    // import { goto } from '$app/navigation';

    // Example: redirect to /dashboard
    // goto('/register');

    // 'form' akan berisi data yang dikembalikan dari action,
    // seperti pesan error jika login gagal.
    export let form: ActionData;
    
    let isSubmitting = false;
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
                <form class="space-y-4 md:space-y-6" method="POST" use:enhance={() => {
                    isSubmitting = true;
                    return async ({ update }) => {
                        isSubmitting = false;
                        await update();
                    };
                }}>
                    <!-- Error/Success Messages -->
                    {#if form?.message}
                        <div class="rounded-md p-4 {form.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}">
                            <div class="flex">
                                <div class="ml-3">
                                    <h3 class="text-sm font-medium {form.success ? 'text-green-800' : 'text-red-800'}">
                                        {form.message}
                                    </h3>
                                </div>
                            </div>
                        </div>
                    {/if}

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
                            class="bg-gray-50 border {form?.errors?.email ? 'border-red-300' : 'border-gray-300'} text-gray-900 rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            placeholder="name@company.com"
                            required=""
                            disabled={isSubmitting}
                        />
                        {#if form?.errors?.email}
                            <p class="mt-1 text-sm text-red-600">{form.errors.email}</p>
                        {/if}
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
                            class="bg-gray-50 border {form?.errors?.password ? 'border-red-300' : 'border-gray-300'} text-gray-900 rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            required=""
                            disabled={isSubmitting}
                        />
                        {#if form?.errors?.password}
                            <p class="mt-1 text-sm text-red-600">{form.errors.password}</p>
                        {/if}
                    </div>
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        class="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {#if isSubmitting}
                            <div class="flex items-center justify-center">
                                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Signing in...
                            </div>
                        {:else}
                            Sign in
                        {/if}
                    </button>
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


