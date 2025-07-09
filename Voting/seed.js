// seed.js
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import 'dotenv/config'; // Pastikan Anda telah menginstal dotenv: npm install dotenv

// Konfigurasi Klien Supabase
// Gunakan SERVICE_ROLE_KEY untuk operasi backend
const supabaseUrl = process.env.PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.PRIVATE_SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function seedData() {
  try {
    // 1. Baca file JSON lokal
    const data = fs.readFileSync('dataset.json', 'utf-8');
    const jsonData = JSON.parse(data);

    // 2. Format data agar sesuai dengan skema tabel
    // Format input:
    // Format output: [{ text_content: "some text" }]
    const formattedData = jsonData.map(item => ({
      text_content: item.Text
    }));

    if (formattedData.length === 0) {
      console.log('Tidak ada data untuk di-seed.');
      return;
    }

    console.log(`Mempersiapkan untuk memasukkan ${formattedData.length} baris...`);

    // 3. Masukkan data ke tabel 'texts_to_label'
    const { error } = await supabase
     .from('texts_to_label')
     .insert(formattedData);

    if (error) {
      console.error('Gagal memasukkan data:', error);
      throw error;
    }

    console.log('Data berhasil di-seed ke tabel texts_to_label!');

  } catch (err) {
    console.error('Terjadi kesalahan selama proses seeding:', err.message);
  }
}

seedData();