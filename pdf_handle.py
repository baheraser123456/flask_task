import PyPDF2 as p


  

def get_ranges(file_path):
    with open(file_path, 'rb') as file:
        reader = p.PdfReader(file)
        len_page=len(reader.pages)
        list_ranges=[]
        j=0
        for i in range(len_page):
            if(i==0):
                continue
            if(reader.pages[i].extract_text().upper().__contains__( 'SECTION 1:') or reader.pages[i].extract_text().upper().__contains__( 'SECTION 1.')):
                list_ranges.append((j,i))
                j=i
        pdf = p.PdfReader(file_path)
    

    for i, (start_page, end_page) in enumerate(list_ranges):
        pdf_writer = p.PdfWriter()
        

        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf.pages[page_num])
        

        output_filename = f'split_{i + 1}.pdf'
        with open(output_filename, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        print(f'Created: {output_filename}')

ranges= get_ranges('aa.pdf')


    
             

               



            
            