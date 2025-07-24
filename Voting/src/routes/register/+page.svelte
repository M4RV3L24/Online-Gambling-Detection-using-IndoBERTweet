<script lang="ts">
    import { enhance } from "$app/forms";
    import type { ActionData } from "./$types";

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
            Welcome
        </a>
        <div
            class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700"
        >
            <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
                <h1
                    class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white"
                >
                    Create an account
                </h1>
                <form class="space-y-4 md:space-y-6" method="POST" use:enhance={() => {
                    isSubmitting = true;
                    return async ({ update }) => {
                        isSubmitting = false;
                        await update();
                    };
                }}>
                    <!-- General error/success message -->
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

                    <!-- Email Field -->
                    <div>
                        <label
                            for="email"
                            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                            >Email</label
                        >
                        <input
                            type="email"
                            name="email"
                            id="email"
                            class="bg-gray-50 border {form?.errors?.email ? 'border-red-300' : 'border-gray-300'} text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            placeholder="name@company.com"
                            required
                            disabled={isSubmitting}
                        />
                        {#if form?.errors?.email}
                            <p class="mt-1 text-sm text-red-600">{form.errors.email}</p>
                        {/if}
                    </div>

                    <!-- Password Field -->
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
                            class="bg-gray-50 border {form?.errors?.password ? 'border-red-300' : 'border-gray-300'} text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            required
                            disabled={isSubmitting}
                        />
                        {#if form?.errors?.password}
                            <p class="mt-1 text-sm text-red-600">{form.errors.password}</p>
                        {/if}
                    </div>

                    <!-- Confirm Password Field -->
                    <div>
                        <label
                            for="confirm-password"
                            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                            >Confirm Password</label
                        >
                        <input
                            type="password"
                            name="confirm_password"
                            id="confirm-password"
                            placeholder="••••••••"
                            class="bg-gray-50 border {form?.errors?.confirmPassword ? 'border-red-300' : 'border-gray-300'} text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            required
                            disabled={isSubmitting}
                        />
                        {#if form?.errors?.confirmPassword}
                            <p class="mt-1 text-sm text-red-600">{form.errors.confirmPassword}</p>
                        {/if}
                    </div>

                    <!-- Terms and Conditions -->
                    <div class="flex items-start">
                        <div class="flex items-center h-5">
                            <input
                                id="terms"
                                aria-describedby="terms"
                                type="checkbox"
                                class="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-primary-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-primary-600 dark:ring-offset-gray-800"
                                required
                                disabled={isSubmitting}
                            />
                        </div>
                        <div class="ml-3 text-sm">
                            <label
                                for="terms"
                                class="font-light text-gray-500 dark:text-gray-300"
                                >Saya menyetujui <a
                                    class="font-medium text-primary-600 hover:underline dark:text-primary-500"
                                    href="#">Syarat dan Ketentuan</a
                                ></label
                            >
                        </div>
                    </div>

                    <!-- Submit Button -->
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        class="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                    >
                        {#if isSubmitting}
                            <div class="flex items-center justify-center">
                                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Mendaftarkan...
                            </div>
                        {:else}
                            Sign Up
                        {/if}
                    </button>

                    <!-- Login Link -->
                    <p
                        class="text-sm font-light text-gray-500 dark:text-gray-400"
                    >
                        Already have an account? <a
                            href="/login"
                            class="font-medium text-blue-600 hover:underline dark:text-blue-500"
                            >Login here</a
                        >
                    </p>
                </form>
            </div>
        </div>
    </div>
</section>

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

    .success-message {
        color: #22543d;
        background-color: #c6f6d5;
        border: 1px solid #48bb78;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
</style>
