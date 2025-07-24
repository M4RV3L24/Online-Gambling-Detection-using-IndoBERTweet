<script>
import "../app.css";
import "simple-datatables/dist/style.css";

let { children } = $props();
</script>

<div class="fixed inset-0 min-h-screen w-full dark:bg-gray-950 -z-10"></div>
<div class="relative z-0 min-h-screen w-full dark:text-gray-100">
  {@render children()}
</div>


<div id="default-modal" tabindex="-1" aria-hidden="true" class="hidden overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full mx-auto">
    <div class="relative p-4 w-full min-w-[90%] sm:min-w-[80%] md:min-w-[60%] lg:min-w-[50%] max-w-2xl max-h-full">
        <!-- Modal content -->
        <div class="relative bg-white rounded-lg shadow-lg dark:bg-gray-700">
            <!-- Modal header -->
            <div class="flex items-center justify-between p-4 md:p-5 border-b rounded-t dark:border-gray-600 border-gray-200">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
                    Rules & Guidelines
                </h3>
                <button type="button" class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white" data-modal-hide="default-modal">
                    <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                    </svg>
                    <span class="sr-only">Close modal</span>
                </button>
            </div>
            <!-- Modal body -->
            <div class="p-4 md:p-5 space-y-4">
                <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
                    <strong>1. Read each text carefully before voting.</strong><br>
                    Take your time to understand the content before making a decision.
                </p>
                <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
                    <strong>2. Vote 'Yes' if the text contains gambling content.</strong><br>
                    This includes references to betting, casinos, lottery, poker, or any form of gambling activities.
                </p>
                <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
                    <strong>3. Vote 'No' if the text does not contain gambling content.</strong><br>
                    Regular posts about sports, entertainment, or other topics without gambling references.
                </p>
                <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
                    <strong>4. Use 'Skip' if you're unsure about the content.</strong><br>
                    When the text is ambiguous or you cannot determine if it's gambling-related.
                </p>
                <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
                    <strong>5. You can cancel your vote anytime before submitting.</strong><br>
                    Use the cancel button to remove your vote if you change your mind.
                </p>
                
                <hr class="border-gray-300 dark:border-gray-600">
                
                <div class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
                    <strong class="text-gray-700 dark:text-gray-200">Kriteria Konten Judi Online:</strong>
                    <ul class=" space-y-1 text-gray-500 list-disc list-inside dark:text-gray-400">
                        <li>Mengandung kalimat yang secara terang-terangan mengajak atau mengundang untuk berpartisipasi dalam aktivitas judi online.</li>
                        <li>Menyebutkan nama platform, menyertakan tautan (link) aktif, atau pola URL yang mengarah ke situs judi online.</li>
                        <li>Menunjukkan atau mengklaim hasil kemenangan, pencapaian (maxwin, jackpot), atau kemudahan penarikan dana (WD) dari aktivitas judi.</li>
                        <li>Memberikan arahan, tutorial, atau panduan tentang cara mendaftar, melakukan deposit, atau bermain di platform judi online.</li>
                    </ul>
                </div>
            </div>
            <!-- Modal footer -->
            <div class="flex items-center p-4 md:p-5 border-t border-gray-200 rounded-b dark:border-gray-600">
                <button data-modal-hide="default-modal" type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Got it!</button>
            </div>
        </div>
    </div>
</div>
