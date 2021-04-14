# import Core Pkg
from json import encoder
import streamlit as st
import streamlit.components.v1 as stc

# additional pkgs / summarization pkgs
# need: pip install gensim sumy gensim_sum_ext pandas altair seaborn rouge nltk PyPDF2 wordcloud

# TextRank Algorithm
from gensim.summarization import summarize

# LexRank Algorithm
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk

nltk.download('punkt', 'stopwords')

# evaluate summay
from rouge import Rouge

# EDA pkgs
import pandas as pd
import altair as alt
import json
import PyPDF2
from tika import parser
import fitz # PyMuPDF

# valores iniciais ou fixos
currenteCodeLanguage = 'pt'
language = ['Português', 'English']
codes = {'português': 'pt', 'english': 'en'}
languageNltk = {'português': 'portuguese', 'english': 'english'}
raw_text = ''

with open('translation.json', 'r', encoding='UTF-8') as j:
    json_dictionary = json.load(j)
    # print(json_dictionary)
    # print(json_dictionary['pt']['nome'])

def translate(key):
    global currenteCodeLanguage
    # print(currenteCodeLanguage)
    try:
        return json_dictionary[currenteCodeLanguage][key]
    except:
        return key


#para esconder o menu do próprio streamlit 
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
# Configuração inicial da página
st.set_page_config(page_title=translate('titulo'), page_icon='favicon.png', layout='centered', )

# passa javascript e estilos
#stc.html('<script src="https://code.iconify.design/1/1.0.7/iconify.min.js"></script>')
#stc.html(hide_streamlit_style)
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Fxn for LexRank Summarization
# Function for Sumy Summarization
def sumy_summarizer(docx,language,num=2):
    parser = PlaintextParser.from_string(docx,Tokenizer(language))
    lex_summarizer = LexRankSummarizer()
    summary = lex_summarizer(parser.document,num)
    summary_list = [str(sentence) for sentence in summary]
    result = ' '.join(summary_list)
    return result


# Evaluate
def evaluate_summary(summary,reference):
    r = Rouge()
    eval_score = r.get_scores(summary, reference)
    eval_score_df = pd.DataFrame(eval_score[0])
    return eval_score_df



def main():
    global currenteCodeLanguage
    
    currentLanguage = st.radio(translate('escolha'), language).lower()
    currenteCodeLanguage = codes[currentLanguage]

    st.title(translate('titulo'))
    menu = ['Home', 'About']
    choice = st.sidebar.selectbox('Menu', menu)
    
    if choice == 'Home':
        conteudo = ''
        st.subheader(translate('textoOriginal'))

        arquivo = st.file_uploader(translate('arraste'),
            #type=['pdf', 'doc', 'txt', 'docx']
            type=['pdf', 'txt']
        )
        if arquivo is not None:
            # read the content
            #st.write(type(arquivo))
            #st.write(dir(arquivo))
            #st.write(arquivo.__format__)
            nomeArquivo = arquivo.name.upper().split('.')
            if nomeArquivo[-1] == 'PDF':
                # arquivoPDF = PyPDF2.PdfFileReader(arquivo, strict=False)
                # for i  in range(0, arquivoPDF.getNumPages()):
                #     pagina = arquivoPDF.getPage(i)
                #     conteudo += pagina.extractText()
                # raw_text = conteudo
                # safe_text = conteudo.encode('utf-8', errors='ignore')
                # safe_text = str(safe_text).replace("\n", "").replace("\\", "")
                # # print(safe_text)
                # raw_text = safe_text
                #print(conteudo)

                # raw = parser.from_file(arquivo)
                # print("TIKA")
                # print(str(raw))
                # print(raw['content'])
                # print("TIKA")

                # doc = fitz.open(arquivo)
                # print(doc)

                with open(arquivo, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">' 
                

            elif nomeArquivo[-1] == 'TXT':
                conteudo = arquivo.read().decode('utf-8')
                raw_text = conteudo
                


                
            else:
                st.error(translate('tipoErrado'))

        st.write(translate('ou'))
        raw_text = st.text_area(translate('cole'), height=300, value=conteudo)
        textLanguageChoose = st.radio(translate('escolhaTexto'), language).lower()
        #print(textLanguageChoose)
        textLanguage = languageNltk[textLanguageChoose]
        #print(textLanguage)
        qtdeFrases = st.slider(translate('qtdeFrases'), 3, 200, 5) 

        #só mostra se tem conteúdo
    
        if st.button(translate('executar')):
            # só executa se tiver texto
            if len(raw_text) > 0:
            
                with st.beta_expander(translate('textoOriginal') + " (" + str(len(raw_text)) + " " + translate('caracteres')  + ")"):
                    st.write(raw_text)

                # layout
                c1, c2 = st.beta_columns(2)

                with c1:
                    my_summary = sumy_summarizer(raw_text, textLanguage, qtdeFrases)
                    with st.beta_expander(translate('metodo1') + " (" + str(len(my_summary)) + " " + translate('caracteres')  + ")"):
                        st.write(my_summary)
                        # st.info("Rouge Score")
                        # eval_df = evaluate_summary(my_summary, raw_text)
                        # st.dataframe(eval_df.T)
                        # eval_df['metrics'] = eval_df.index
                        # c = alt.Chart(eval_df).mark_bar().encode(
                        #     x = 'metrics',
                        #     y = 'rouge-1'
                        # )
                        # st.altair_chart(c)
                with c2:
                    # para o caso de texto muito pequeno, avalia o resultado antes de mostrar
                    try:
                        my_summary = summarize(raw_text)
                        textoAdicional = ""
                        # st.info("Rouge Score")
                        # eval_df = evaluate_summary(my_summary, raw_text)
                        # st.dataframe(eval_df)
                        # eval_df['metrics'] = eval_df.index
                        # c = alt.Chart(eval_df).mark_bar().encode(
                        #     x = 'metrics',
                        #     y = 'rouge-1'
                        # )
                        # st.altair_chart(c)
                    except:
                        my_summary = raw_text
                        textoAdicional = "Texto original mantido"

                    with st.beta_expander(translate('metodo2') + " (" + str(len(my_summary)) + " " + translate('caracteres')  + ")"):
                        if len(textoAdicional) > 0:
                            st.info(textoAdicional)
                        st.write(my_summary)
                        
            else:
                st.error(translate('vazio'))
    else:
        st.subheader('About')

if __name__ == '__main__':
    main()