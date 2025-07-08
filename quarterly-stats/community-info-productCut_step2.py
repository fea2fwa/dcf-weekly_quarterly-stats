import os

def extract_community_qa(file_path):
    # Read text from file
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split text into blocks
    blocks = text.split('---')

    # Initialize empty list to store extracted data
    qa_data = []

    # Process each block
    for block in blocks:
        if f'製品カテゴリ: {product_name}' in block:
            title_start = block.find('タイトル:')
            if title_start != -1:
                title_end = block.find('本文: [質問]', title_start)
                title_text = block[title_start + len('タイトル:'):title_end]

            # Extract question text
            question_start = block.find('本文: [質問]')
            if question_start != -1:
                # question_end = block.find('[提案された回答]', question_start)
                question_end = block.find('[提案された回答]')
                question_text = block[question_start + len('本文: [質問]'):question_end]

            # Extract answer text
            answer_start = block.find('[提案された回答]', question_end)
            if answer_start != -1:
                # answer_end = block.find('製品カテゴリ:', answer_start)
                answer_end = block.find('製品カテゴリ:')
                answer_text = block[answer_start + len('[提案された回答]'):answer_end]

            # Append extracted data to the list
            if question_text and answer_text:
                qa_data.append({'title': title_text, 'question': question_text, 'answer': answer_text})

    # Return formatted results
    return qa_data

def delete_meaningless_text(text):
    text = text.replace("[受け入れられた良い回答]", "")
    text = text.replace("(受け入れられた良い回答は無し)", "")
    return text

# Example usage (assuming the file is named 'data.txt' in the same directory)
# file_path = os.path.join(os.getcwd(), 'dcf-content_20240219_1239.txt')
file_path = os.path.join(os.getcwd(), './text-data/dcf-content_20250507_1234.txt')
product_name = 'PPDM'
qa_data = extract_community_qa(file_path)

with open(f'./text-data/community_contents_{product_name}.txt', 'w', encoding='utf-8') as wf:
    for thread in qa_data:
        wf.write('タイトル：')
        wf.write(thread['title'])
        wf.write('質問：')
        wf.write(thread['question'])
        wf.write('回答：')
        wf.write(delete_meaningless_text(thread['answer']))
