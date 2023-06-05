import streamlit as st
import pandas as pd
from io import StringIO
import plotly.express as px

st.write("# Aracnotaio")


renamingdict = {
    "Entrate": "EntrateCassa",
    "Uscite": "UsciteCassa",
    "Saldo": "SaldoCassa",
    "Entrate.1": "EntrateBancaProssima",
    "Uscite.1": "UsciteBancaProssima",
    "Saldo.1": "SaldoBancaProssima",
    "Entrate.2": "EntratePaypal",
    "Uscite.2": "UscitePaypal",
    "Saldo.2": "SaldoPaypal",
    "Data oper.ne": "DataOperazione",
    "Data reg.ne": "DataRegistrazione",
}

negativecolumns = ["UsciteCassa", "UsciteBancaProssima", "UscitePaypal"]

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    
    # ------------------------------ entrate uscite ------------------------------ #
    dataframe = pd.read_excel(
        uploaded_file, skiprows=[0, 1, 2, 3, 4, 5, 6, 8], header=0, index_col=1
    ).rename(columns=renamingdict)
    print(dataframe.head)
    dataframe.loc[:,"DataOperazione"] = dataframe.loc[:,"DataOperazione"].apply(lambda x: x.replace(year = 2021))
    dataframe.loc[:,"DataRegistrazione"] = dataframe.loc[:,"DataRegistrazione"].apply(lambda x: x.replace(year = 2021))
    dataframe.loc[:,negativecolumns] = -dataframe.loc[:,negativecolumns]
    dataframe.drop("Unnamed: 0", axis=1, inplace=True)
    # dataframe = dataframe.loc[:,1:]
    # dataframe = dataframe.dropna(axis=1, how='all')
    st.write(dataframe)

    st.write("### Grafico nel tempo")

    totalscatter = px.line(dataframe, x="DataOperazione", y="Totale")
    st.plotly_chart(totalscatter)

    # -------------------------------- description ------------------------------- #
    st.write("## Analisi operazioni")

    analysecolumns = [
                "EntrateCassa",
                "UsciteCassa",
                "EntrateBancaProssima",
                "UsciteBancaProssima",
                "EntratePaypal",
                "UscitePaypal",
            ]

    df_sum = (
        dataframe.loc[:,analysecolumns+["Descrizione operazioni"]]
        .groupby("Descrizione operazioni")
        .sum()
    )
    
    df_melted = pd.melt(df_sum.reset_index(), id_vars='Descrizione operazioni', value_vars=df_sum.reset_index().columns[1:], var_name='Column', value_name='Sum')

    st.write("### Ammontare per operazione")

    barplotadjacent = px.bar(df_melted, x='Descrizione operazioni', y='Sum', color='Column')
    st.plotly_chart(barplotadjacent)

    st.write("### Entrate e uscite")
    barplotstack = px.bar(df_melted, x='Column', y='Sum', color='Descrizione operazioni', barmode="stack")
    st.plotly_chart(barplotstack)


    st.write("### Ammontare per singole operazioni")
    st.write(df_sum.transpose())
    
    
    # ---------------------------------------------------------------------------- #
    #                                   Entrate                                    #
    # ---------------------------------------------------------------------------- #

    
    st.write("## Entrate per centri di spesa")
    categoriesdf = dataframe.loc[:,"Quote associative":"Altro"]
    categoriesdf["Descrizione operazioni"] = dataframe["Descrizione operazioni"]
    

    
    df_sum_catent = (
        categoriesdf
        .groupby("Descrizione operazioni")
        .sum()
    )
    
    df_melted_catent = pd.melt(df_sum_catent.reset_index(), id_vars='Descrizione operazioni', value_vars=df_sum_catent.reset_index().columns[1:], var_name='Column', value_name='Sum')

    opcolor = st.checkbox("Mostra singole operazioni", key="opcolor")
    if opcolor:
        barplotent = px.bar(df_melted_catent, x='Column', y='Sum', color='Descrizione operazioni')
    else:
        barplotent = px.bar(df_melted_catent, x='Column', y='Sum')
    st.plotly_chart(barplotent)
    
    st.write("### Analisi delle entrate per centri di spesa")
    st.write(categoriesdf.describe())
    
    

    