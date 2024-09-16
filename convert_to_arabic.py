import re
from PyPDF2 import PdfReader

ones = ['صفر', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة']
tens = ['', 'عشرة', 'عشرون', 'ثلاثون', 'أربعون', 'خمسون', 'ستون', 'سبعون', 'ثمانون', 'تسعون']
teens = ['عشرة', 'أحد عشر', 'اثنا عشر', 'ثلاثة عشر', 'أربعة عشر', 'خمسة عشر', 'ستة عشر', 'سبعة عشر', 'ثمانية عشر', 'تسعة عشر']
hundreds = ['', 'مائة', 'مائتان', 'ثلاثمائة', 'أربعمائة', 'خمسمائة', 'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة']
thousands = ['', 'ألف', 'ألفان', 'آلاف']
millions = ['', 'مليون', 'مليونان', 'ملايين']

def convert_three_digits(number):
    num = int(number)
    if num < 10:
        return ones[num]
    elif num < 20:
        return teens[num - 10]
    elif num < 100:
        return (ones[num % 10] + ' و' + tens[num // 10]) if num % 10 != 0 else tens[num // 10]
    else:
        remainder = num % 100
        hundreds_part = hundreds[num // 100]
        if remainder == 0:
            return hundreds_part
        else:
            return hundreds_part + ' و' + convert_three_digits(remainder)

def convert_large_number(number):
    num = int(number)
    if num < 1000:
        return convert_three_digits(num)

    num_str = str(num)[::-1]
    groups = [num_str[i:i+3][::-1] for i in range(0, len(num_str), 3)]
    groups = groups[::-1]

    arabic_parts = []
    for idx, group in enumerate(groups):
        group_num = int(group)
        if group_num == 0:
            continue
        if idx == 1:
            arabic_parts.append(thousands[group_num] if group_num <= 2 else convert_three_digits(group_num) + ' آلاف')
        elif idx == 2:
            arabic_parts.append(millions[group_num] if group_num <= 2 else convert_three_digits(group_num) + ' ملايين')
        else:
            arabic_parts.append(convert_three_digits(group_num))

    return ' و'.join(arabic_parts)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_and_convert_numbers(pdf_file):
    text = extract_text_from_pdf(pdf_file)
    western_numbers = re.findall(r'\d+', text)
    arabic_numbers_in_words = [convert_large_number(num) for num in western_numbers]
    return arabic_numbers_in_words

pdf_file = "aa.pdf"
arabic_numbers = extract_and_convert_numbers(pdf_file)

for num, arabic_word in zip(re.findall(r'\d+', extract_text_from_pdf(pdf_file)), arabic_numbers):
    num=arabic_numbers
