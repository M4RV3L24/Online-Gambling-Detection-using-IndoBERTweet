// get_data.js
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import 'dotenv/config'; // Pastikan Anda telah menginstal dotenv: npm install dotenv

// Konfigurasi Klien Supabase
// Gunakan SERVICE_ROLE_KEY untuk operasi backend
const supabaseUrl = process.env.PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.PRIVATE_SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function fetchData() {
    try {
        // 1. Ambil data dari tabel 'texts_to_label' beserta hasil voting dari tabel 'votes'
        const { data, error } = await supabase
            .from('texts_to_label')
            .select(`*, votes:votes(text_id, user_id, vote, skip)`); // Join votes
        if (error) {
            console.error('Gagal mengambil data:', error);
            throw error;
        }
        if (!data || data.length === 0) {
            console.log('Tidak ada data yang ditemukan di tabel texts_to_label.');
            return;
        }

        // Filter: hanya text yang semua votes sama dan tidak ada skip
        const filtered = data.filter(text => {
            const votes = text.votes || [];
            if (votes.length === 0) return false; // Harus ada vote

            // Tidak boleh ada skip
            if (votes.some(v => v.skip === 1)) return false;

            // Semua vote harus sama (true/false)
            const firstVote = votes[0].vote;
            return votes.every(v => v.vote === firstVote);
        })
        .map(text => {
            // Ambil hanya satu vote (vote pertama)
            return {
                text: text.text_content,
                votes: text.votes && text.votes.length > 0 ? text.votes[0].vote : null
            };
        });

        console.log(`Mengambil ${filtered.length} baris yang lolos filter dari tabel texts_to_label...`);
        // 2. Simpan data ke file JSON lokal
        fs.writeFileSync('fetched_data.json', JSON.stringify(filtered, null, 2));
        console.log('Data berhasil disimpan ke fetched_data.json!');
    } catch (err) {
        console.error('Terjadi kesalahan selama proses pengambilan data:', err.message);
    }
}

fetchData();
