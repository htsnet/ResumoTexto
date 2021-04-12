# import Core Pkg
import streamlit as st

# additional pkgs / summarization pkgs
# need: pip install gensim sumy gensim_sum_ext pandas altair seaborn rouge nltk

# TextRank Algorithm
from gensim.summarization import summarize

# LexRank Algorithm
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk

nltk.download('punkt')

# evaluate summay
from rouge import Rouge

# EDA pkgs
import pandas as pd

import altair as alt

import json

# valores iniciais ou fixos
currenteCodeLanguage = 'pt'
language = ['Português', 'English']
codes = {'português': 'pt', 'english': 'en'}

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

# Configuração inicial da página
st.set_page_config(page_title=translate('titulo'), page_icon='favicon.png', layout='centered', )

def main():
    global currenteCodeLanguage
    
    currentLanguage = st.radio(translate('escolha'), language).lower()
    currenteCodeLanguage = codes[currentLanguage]

    st.title(translate('titulo'))
    menu = ['Home', 'About']
    choice = st.sidebar.selectbox('Menu', menu)
    
    if choice == 'Home':
        st.subheader(translate('resumo'))

        raw_text = st.text_area(translate('cole'), height=50)
        textLanguage = st.radio(translate('escolhaTexto'), language).lower()
        qtdeFrases = st.slider(translate('qtdeFrases'), 3, 200, 5) 

        #só mostra se tem conteúdo
    
        if st.button(translate('executar')):
            # só executa se tiver texto
            if len(raw_text) > 0:
            
                with st.beta_expander('Original Text'):
                    st.write(raw_text)

                # layout
                c1, c2 = st.beta_columns(2)

                with c1:
                    with st.beta_expander('LexRank Summary'):
                        my_summary = sumy_summarizer(raw_text, textLanguage, qtdeFrases)
                        document_len = {
                            "Original": len(raw_text), 
                            'Summary': len(my_summary)
                            }
                        st.write(document_len)
                        st.write(my_summary)

                        st.info("Rouge Score")
                        eval_df = evaluate_summary(my_summary, raw_text)
                        st.dataframe(eval_df.T)
                        eval_df['metrics'] = eval_df.index
                        c = alt.Chart(eval_df).mark_bar().encode(
                            x = 'metrics',
                            y = 'rouge-1'
                        )
                        st.altair_chart(c)

                        

                with c2:
                    with st.beta_expander('TextRank Summary'):
                        # para o caso de texto muito pequeno
                        try:
                            my_summary = summarize(raw_text)
                            document_len = {
                                "Original": len(raw_text), 
                                'Summary': len(my_summary)
                                }
                            st.write(document_len)
                            st.write(my_summary)

                            st.info("Rouge Score")
                            eval_df = evaluate_summary(my_summary, raw_text)
                            st.dataframe(eval_df)
                            eval_df['metrics'] = eval_df.index
                            c = alt.Chart(eval_df).mark_bar().encode(
                                x = 'metrics',
                                y = 'rouge-1'
                            )
                            st.altair_chart(c)
                        except:
                            st.write(raw_text)
                            st.info("Texto original mantido")
            else:
                st.error(translate('vazio'))
    else:
        st.subheader('About')

if __name__ == '__main__':
    main()