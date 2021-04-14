# import Core Pkg
from json import encoder
import streamlit as st
import streamlit.components.v1 as stc
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

# additional pkgs / summarization pkgs
# need: pip install gensim sumy gensim_sum_ext pandas seaborn rouge nltk PyPDF2 wordcloud neattext

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
import json
import PyPDF2
import neattext.functions as nfx

# Text Downloader
import base64
import time

from wordcloud import WordCloud
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')

timestr = time.strftime("%Y%m%d-%H%M%S%m")

# valores iniciais ou fixos
currenteCodeLanguage = 'pt'
language = ['Português', 'English']
codes = {'português': 'pt', 'english': 'en'}
languageNltk = {'português': 'portuguese', 'english': 'english'}
raw_text = ''
currentCodeLanguageStopWords = ''

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


def text_downloader(raw_text, model):
    b64 = base64.b64encode(raw_text.encode()).decode()
    new_filename = "resume_{}_model_{}.txt".format(timestr, model)
    st.markdown('### ' + translate('download') + ' ###')
    href = f'<a href="data:file/txt;base64,{b64}" download="{new_filename}">💾 ' + translate('clique') + '!!</a>'
    st.markdown(href, unsafe_allow_html=True)


def plot_wordcloud(text):
    global currentCodeLanguageStopWords
    
    # remove stopwords
    if currentCodeLanguageStopWords == 'en':
        stop_words = set(stopwords.words('english'))
    else:
        stop_words_initial = stopwords.words('portuguese')
        stop_words_initial.extend(['a','e','i','o','u'])
        stop_words = set(stop_words_initial)
    word_tokens = word_tokenize(text.lower())
    # print(stop_words)
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    filtered_sentence = [] 
    for w in word_tokens: 
        if w not in stop_words: 
            filtered_sentence.append(w)    
    filtered_sentence = ' '.join(filtered_sentence)
    my_wordcloud = WordCloud().generate(filtered_sentence)
    fig = plt.figure()
    plt.imshow(my_wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(fig)

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
            type=['txt']
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

            else:
                st.error(translate('tipoErrado'))

        st.write(translate('ou'))
        raw_text = st.text_area(translate('cole'), height=300, value=conteudo)

        st.write(translate('escolhaTexto'))
        textLanguageChoose = st.radio("", language).lower()
        #print(textLanguageChoose)
        textLanguage = languageNltk[textLanguageChoose]
        #print(textLanguage)

        qtdeFrases = st.slider(translate('qtdeFrases'), 3, 200, 5) 

        st.write("Opções adicionais")
        clean_numbers = st.checkbox(translate("removeNumeros"))
        clean_especial = st.checkbox(translate("removeEspeciais"))
        clean_urls = st.checkbox(translate("removeUrls"))
        clean_emojis = st.checkbox(translate("removeEmojis"))

        #só mostra se tem conteúdo
    
        if st.button(translate('executar')):
            # só executa se tiver texto
            if len(raw_text) > 0:
                with st.beta_expander(translate('textoOriginal') + " (" + str(len(raw_text)) + " " + translate('caracteres')  + ")"):
                    st.write(raw_text)

                # clean text according options
                if clean_numbers:
                    raw_text = nfx.remove_numbers(raw_text)
                if clean_especial:
                    raw_text = nfx.remove_special_characters(raw_text)
                if clean_urls:
                    raw_text = nfx.remove_urls(raw_text)
                if clean_emojis:
                    raw_text = nfx.remove_emojis(raw_text)

                # layout
                c1, c2 = st.beta_columns(2)

                with c1:
                    my_summary = sumy_summarizer(raw_text, textLanguage, qtdeFrases)
                    with st.beta_expander(translate('metodo1') + " (" + str(len(my_summary)) + " " + translate('caracteres')  + ")"):
                        st.write(my_summary)
                        text_downloader(my_summary, 1)
                        plot_wordcloud(raw_text)
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
                        text_downloader(my_summary, 2)
                        plot_wordcloud(raw_text)
                        
            else:
                st.error(translate('vazio'))
    else:
        st.subheader('About')

if __name__ == '__main__':
    main()


# https://www.youtube.com/watch?v=KnaropswzoY&t=228s video with some instructions