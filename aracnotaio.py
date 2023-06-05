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
}

negativecolumns = ["UsciteCassa", "UsciteBancaProssima", "UscitePaypal"]

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    dataframe = pd.read_excel(
        uploaded_file, skiprows=[0, 1, 2, 3, 4, 5, 6, 8], header=0, index_col=1
    ).rename(columns=renamingdict)
    print(dataframe.head)
    dataframe.loc[:,"DataOperazione"] = dataframe.loc[:,"DataOperazione"].apply(lambda x: x.replace(year = 2019))
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

    st.write(df_sum.transpose())
