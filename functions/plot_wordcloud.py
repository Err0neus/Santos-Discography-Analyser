#!/usr/bin/env python
# coding: utf-8

# In[2]:


# IMPORT MODULES FOR WORDCLOUD
import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt

# In[4]:


def createGroupDf(df, v_groupby, v_lyric_version):    
    df_lyric_raw_grouped = df.groupby(v_groupby)[v_lyric_version].apply(','.join).reset_index()
    #df_lyric_raw_grouped['lyrics_cleaned'] = df_lyric_raw_grouped['lyrics_cleaned'].str.replace("\r","").str.replace("\n", " ").str.split(" ")
    df_lyric_raw_grouped = df_lyric_raw_grouped.set_index(v_groupby)
    df_lyric_raw_pivot = df_lyric_raw_grouped.T #transpose to switch year to be columns
    return df_lyric_raw_pivot


# In[5]:


def grid(n):
    max_cols = 3
    if n == 2:
        return (1,2)
    elif n == 4:
        return (2,2)
    elif n == 9:
        return (3,3)
    else:
        return (max(1,int(np.ceil((n/max_cols)))),min(n,max_cols))


# In[9]:
ls_stopwords_extended = ls_stopwords_extended = ['a', 'all', 'an', 'any', 'both', 'each', 'no', 'some', 'that', 'the', 'these', 'this', 'those', 'another', 'every', 'about', 'after', 'as', 'at', 'before', 'below', 'between', 'by', 'during', 'for', 'from', 'if', 'in', 'into', 'ma', 'o', 'of', 'on', 'than', 'through', 'under', 'until', 'up', "wasn't", 'while', 'with', 'across', 'although', 'among', 'around', 'behind', 'besides', 'except', 'like', 'near', 'non', 'onto', 'per', 'since', 'thereupon', 'thou', 'though', 'throughout', 'toward', 'unless', 'unlike', 'via', 'whereas', 'whereupon', 'wherever', 'whether', 'within', 'despite', 'thorough', 'above', 'against', 'becausebehind', 'beyond', 'over', 'upon', 'ab', 'al', 'ax', 'de', 'en', 'oc', 'again', "aren't", 'because', 'here', 'just', "mightn't", 'not', 'now', 'once', 'only', 'so', 'then', 'too', 'very', 'accordingly', 'actually', 'ah', 'almost', 'already', 'also', 'always', 'anymore', 'apparently', 'approximately', 'aside', 'away', 'certainly', 'e', 'else', 'elsewhere', 'especially', 'even', 'formerly', 'hardly', 'however', 'immediately', 'indeed', 'instead', 'largely', 'later', 'latterly', 'ltd', 'mainly', 'maybe', 'meantime', 'meanwhile', 'merely', 'moreover', 'mostly', 'namely', 'nearly', 'necessarily', 'never', 'nevertheless', 'nonetheless', 'noone', 'normally', 'often', 'otherwise', 'particularly', 'perhaps', 'possibly', 'potentially', 'predominantly', 'previously', 'primarily', 'probably', 'promptly', 'quite', 'rather', 'readily', 'really', 'recently', 'regardless', 'relatively', 'respectively', 'significantly', 'similarly', 'slightly', 'sometime', 'sometimes', 'somewhat', 'specifically', 'still', 'strongly', 'substantially', 'sufficiently', 'thereafter', 'thereby', 'therefore', 'thus', 'truly', 'twice', 'usefully', 'usually', 'whither', 'widely', 'yes', 'yet', 'apart', 'consequently', 'currently', 'definitely', 'entirely', 'exactly', 'presumably', 'reasonably', 'secondly', 'thoroughly', 'well', 'anyway', 'anywhere', 'back', 'eleven', 'enough', 'ever', 'first', 'much', 'nowhere', 'somewhere', 'there', 'ain', 'be', 'couldn', 'didn', 'do', 'doesn', "doesn't", "don't", 'have', 'll', "should've", "you've", "he'd", "she'd", 'cannot', 'end', 'give', 'go', 'keep', 'kept', 'look', 'n', 'name', 'obtain', 'shed', 'consider', 'wonder', 'couldnt', 'find', 'get', 'hence', 'mill', 'please', 'put', 'show', 'take', 'thence', 'dp', 'dr', 'vq', 'am', 'are', 'mightn', 'needn', "won't", "you'd", 'co', 'come', 'contain', 'et', 'hi', 'immediate', 'know', 'particular', 'pp', 'say', 'see', 'seem', 'suggest', "that've", 'thereto', 'think', 'til', 'use', "'ve", 'vs', 'want', 'whence', 'whos', 'www', 'appear', 'inner', 'move', 'thickv', 'twelve', 'wherein', 'ea', 'i2', 'nah', 'and', 'but', 'nor', 'or', 'either', 'neither', 'plus', 'aren', "couldn't", 'don', 'few', 'further', 'i', 'isn', 'mustn', "needn't", 'other', 'own', 'same', 'such', 've', 'wasn', 'weren', 'wouldn', "you'll", "he'll", "she'll", 'able', 'adj', 'along', 'amongst', 'arent', 'ask', 'available', 'b', 'brief', 'certain', 'different', 'due', 'ed', 'edu', 'ex', 'ff', 'former', 'gotten', 'hereupon', 'id', 'inc', 'kg', 'latter', 'lest', 'likely', 'make', 'many', 'mg', 'nay', 'necessary', 'new', 'next', 'nos', 'obtained', 'oh', 'ok', 'overall', 'past', 'que', 'qv', 'rd', 'recent', 'right', 'several', 'significant', 'similar', 'sub', 'sup', 'sure', 'th', 'therein', 'therere', 'thoughh', 'thru', 'tip', 'ts', 'u', 'un', 'unlikely', 'unto', 'used', 'useful', 'usefulness', 'v', 'various', 'wasnt', 'werent', 'whoever', 'willing', 'x', 'youd', "c'mon", 'inasmuch', 'insofar', "it'd", 'novel', 'second', "t's", 'third', 'bottom', 'cant', 'empty', 'fifteen', 'full', 'ie', 'last', 're', 'top', 'whole', 'f', 'le', 'u201d', 'well-b', 'ac', 'ao', 'ay', 'bj', 'cc', 'ds', 'ec', 'gr', 'io', 'n2', 'nc', 'ng', 'ni', 'nn', 'nr', 'ny', 'og', 'oi', 'oo', 'os', 'ot', 'p3', 'tt', 'ue', 'ui', 'uj', 'uk', 'um', 'uo', 'ur', 'ut', 'been', 'hadn', 'hasn', 'haven', 'done', 'given', 'gone', 'hed', 'placed', 'related', 'seemed', 'seen', 'shown', 'specified', 'taken', 'thered', 'tried', 'associated', 'described', 'hasnt', 'bi', 'can', 'should', 'will', 'could', 'ought', 'would', 'ca', "'ll", 'may', 'might', 'must', 'shall', 'wo', 'd', "didn't", "hadn't", "isn't", 'm', "mustn't", 'off', 's', 'shan', "shan't", 'shouldn', "shouldn't", "wouldn't", 'y', "you're", "he's", "here's", "how's", "i'd", "i'll", "i'm", "i've", "let's", "that's", "there's", "they'd", "they'll", "they're", "they've", "we'd", "we'll", "we're", "we've", "what's", "when's", "where's", "who's", "why's", 'abst', 'accordance', 'act', 'announce', 'anybody', 'anyhow', 'anyone', 'anything', 'arise', 'auth', 'beforehand', 'begin', 'beside', 'biol', 'briefly', "can't", 'cause', 'date', 'effect', 'eg', 'eighty', 'everybody', 'everyone', 'everything', 'fix', 'forth', 'furthermore', 'h', 'hereafter', 'hereby', 'herein', 'hid', 'hither', 'home', 'howbeit', 'im', 'index', 'information', 'invention', 'inward', 'itd', "it'll", 'j', 'k', 'let', 'line', 'ml', 'mrs', 'mug', 'nd', 'need', 'ninety', 'nobody', 'none', 'nothing', 'okay', 'ord', 'p', 'page', 'part', 'r', 'research', 'run', 'sec', 'section', 'somebody', 'somehow', 'someone', 'something', 'specify', 'tell', "there'll", 'thereof', "there've", 'theyd', 'theyre', 'throug', 'value', 'viz', 'vol', 'w', 'way', 'whatever', "what'll", 'whereafter', 'whereby', 'whim', "who'll", 'whomever', 'wont', 'world', 'wouldnt', 'youre', 'z', "a's", "ain't", 'appropriate', "c's", 'course', 'example', 'help', 'indicate', 'amoungst', 'amount', 'become', 'bill', 'call', 'con', 'detail', 'etc', 'fify', 'fill', 'fire', 'forty', 'front', 'interest', 'ours', 'side', 'sixty', 'system', 'c', 'g', 'l', 'q', 't', 'op', 'cit', 'ibid', 'au', 'pas', 'los', 'http', 'volumtype', 'par', 'a1', 'a2', 'a3', 'a4', 'ad', 'ae', 'af', 'ag', 'aj', 'ap', 'ar', 'av', 'aw', 'az', 'b1', 'b2', 'b3', 'ba', 'bc', 'bd', 'bk', 'bl', 'bn', 'bp', 'br', 'bs', 'bt', 'bu', 'bx', 'c1', 'c2', 'c3', 'cd', 'ce', 'cf', 'cg', 'ch', 'ci', 'cj', 'cl', 'cm', 'cn', 'cp', 'cq', 'cr', 'cs', 'ct', 'cu', 'cv', 'cx', 'cy', 'cz', 'd2', 'da', 'dc', 'dd', 'dk', 'dl', 'dt', 'du', 'dx', 'dy', 'e2', 'e3', 'ee', 'ef', 'ei', 'ej', 'el', 'em', 'f2', 'fa', 'fc', 'fi', 'fj', 'fl', 'fn', 'fo', 'fr', 'fs', 'ft', 'fu', 'fy', 'ga', 'ge', 'gi', 'gj', 'gl', 'gs', 'gy', 'h2', 'h3', 'hh', 'hj', 'ho', 'hr', 'hs', 'hu', 'hy', 'i3', 'i4', 'i6', 'i7', 'i8', 'ia', 'ib', 'ic', 'ig', 'ih', 'ii', 'ij', 'il', 'ip', 'iq', 'ir', 'iv', 'ix', 'iy', 'iz', 'jj', 'jr', 'js', 'jt', 'ju', 'ke', 'kj', 'km', 'ko', 'l2', 'la', 'lc', 'lf', 'lj', 'ln', 'lo', 'lr', 'ls', 'lt', 'm2', 'mn', 'mo', 'ms', 'mt', 'mu', 'ne', 'nj', 'nl', 'ns', 'nt', 'oa', 'ob', 'od', 'oj', 'ol', 'om', 'oq', 'ou', 'ow', 'ox', 'oz', 'p1', 'p2', 'pc', 'pd', 'pe', 'pf', 'ph', 'pi', 'pj', 'pk', 'pl', 'pm', 'pn', 'po', 'pq', 'pr', 'ps', 'pt', 'pu', 'py', 'qj', 'qu', 'r2', 'ra', 'rc', 'rf', 'rh', 'ri', 'rj', 'rl', 'rm', 'rn', 'ro', 'rq', 'rr', 'rs', 'rt', 'ru', 'rv', 'ry', 's2', 'sa', 'sc', 'sd', 'se', 'sf', 'si', 'sj', 'sl', 'sm', 'sn', 'sp', 'sq', 'sr', 'ss', 'st', 'sy', 'sz', 't1', 't2', 't3', 'tb', 'tc', 'td', 'te', 'tf', 'ti', 'tj', 'tl', 'tm', 'tn', 'tp', 'tq', 'tr', 'tv', 'tx', 'va', 'wa', 'vd', 'wi', 'vj', 'vo', 'vt', 'vu', 'yeah', 'hey', 'huh', 'uh', 'tu', 'did', 'had', "she's", 'was', 'were', 'added', 'became', 'came', 'got', 'noted', 'omitted', 'said', 'sent', 'showed', 'somethan', 'wed', 'went', 'whod', 'indicated', 'found', 'hundred', 'made', 'does', 'has', 'is', "it's", "that'll", 'anyways', 'causes', 'comes', 'gets', 'gives', 'goes', 'happens', 'heres', 'makes', 'mr', 'provides', 'ref', 'says', 'seems', 'selves', 'shows', 'tendswheres', 'les', 'out', "hasn't", "haven't", 'hers', 'theirs', "weren't", 'won', 'yours', 'yourselves', 'affects', 'afterwards', 'becomes', 'com', 'contains', 'fifth', 'hes', 'keeps', 'knows', 'lets', 'looks', 'means', 'ones', 'others', 'pages', 'refs', 'regards', 'results', 'saw', 'shes', 'showns', 'thats', 'theres', 'towards', 'tries', 'ups', 'uses', 'vols', 'whats', 'words', 'indicates', 'he', 'him', 'it', 'me', 'she', 'them', 'they', 'we', 'you', 'self', 'us', 'I', 'her', 'his', 'its', 'my', 'our', 'their', 'your', 'how', 'where', 'whenever', 'when', 'why', 'more', 'less', 'ten', 'most', 'least', 'est', 'to', 'na', 'what', 'who', 'whom', 'which', 'eight', 'five', 'four', 'million', 'nine', 'one', 'seven', 'six', 'thousand', 'two', 'zero', 'three', 'twenty', '0o', '0s', '3a', '3b', '3d', '6b', '6o', 'describe', 'df', 'di', 'dj', 'eo', 'ep', 'eq', 'er', 'es', 'eu', 'ev', 'ey', 'lb', 'whose', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'x1', 'x2', 'x3', 'xf', 'xi', 'xj', 'xk', 'xl', 'xn', 'xo', 'xs', 'xt', 'xv', 'xx', 'y2', 'yj', 'yl', 'yr', 'ys', 'yt', 'zi', 'zz',"ya","yeah","hey","nah","ooo","oooo","cha","ooh","woah","woah","wooah","woooah",'gonna','gotta','wanna','goin']
def createWordCloud(df, col):
    data = createGroupDf(df, col, 'LYRICS_CLEAN')
    fig = plt.figure(figsize = (20, 15))
    col_list = data.columns
    y= grid(len(col_list))[0]
    x= grid(len(col_list))[1]
    for i in range(0, len(col_list)):
        ax = fig.add_subplot(y, x, i+1)
        plt.axis('off')
        wordcloud2 = WordCloud(max_font_size=50, max_words=75, background_color="white", stopwords=ls_stopwords_extended,collocations=False).generate((' '.join(data[col_list[i]])))
        plt.title(col_list[i])
        plt.imshow(wordcloud2, interpolation='bilinear')

    plt.show()


