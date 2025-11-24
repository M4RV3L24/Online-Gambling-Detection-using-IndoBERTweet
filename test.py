import json

async def run_preprocessing_steps_separate_files(start_idx=0, checkpoint_interval=100):
    stop_words = set(stopwords.words('indonesian'))
    with open('fetched_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    back_translation_results = []
    final_results = []

    if start_idx > 0:
        try:
            with open(f'result_RF2/fetched_data_back_translation_checkpoint_{start_idx}.json', 'r', encoding='utf-8') as f:
                back_translation_results = json.load(f)
            with open(f'result_RF2/fetched_data_final_checkpoint_{start_idx}.json', 'r', encoding='utf-8') as f:
                final_results = json.load(f)
            print(f"Loaded checkpoint at item {start_idx}")
        except FileNotFoundError:
            print(f"Checkpoint files for index {start_idx} not found. Starting from scratch.")
            start_idx = 0

    for idx, item in enumerate(data[start_idx:], start=start_idx):
        text = item['text']
        label = item.get('votes', None)  # Optional, if labels exist
        # 1. Back translation - this part is optional
        text1 = await back_translate(text.lower())
        back_translation_results.append(text1)
        text2 = convert_emojis(text1)
        text3 = normalize_text(text2)
        text4 = replace_slang(text3, slang_dict)
        text5 = remove_extra_chars(text4)
        text6 = text5.lower()
        text8 = replace_links(text6)
        # 9. Remove numbers
        text9 = remove_numbers(text8)
        # 10. Remove punctuation
        text10 = remove_punctuation(text9)
        # 11. Stemming
        text11 = stem_with_exceptions(text10)
        tokens = text11.split()
        text12 = ' '.join([w for w in tokens if w.lower() not in stop_words])

        final_results.append({
            'text': text12,
            'label': label
        })

        # Checkpoint: save every 100 items
        if (idx + 1) % checkpoint_interval == 0:
            checkpoint_num = idx + 1
            with open(f'result_RF2/fetched_data_back_translation_checkpoint_{checkpoint_num}.json', 'w', encoding='utf-8') as f:
                json.dump(back_translation_results, f, ensure_ascii=False, indent=2)
            with open(f'result_RF2/fetched_data_final_checkpoint_{checkpoint_num}.json', 'w', encoding='utf-8') as f:
                json.dump(final_results, f, ensure_ascii=False, indent=2)
            print(f'Checkpoint saved at item {checkpoint_num}')

    # Save back translation results
    with open('result_RF2/fetched_data_back_translation.json', 'w', encoding='utf-8') as f:
        json.dump(back_translation_results, f, ensure_ascii=False, indent=2)
    print('Saved back translation results to result_RF2/fetched_data_back_translation.json')

    # Save final results
    with open('result_RF2/fetched_data_final.json', 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    print('Saved final results to result_RF2/fetched_data_final.json')

await run_preprocessing_steps_separate_files(checkpoint_interval=400, start_idx=8800)