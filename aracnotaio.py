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

tabview, tabadd = st.tabs(["Analisi", "Aggiungi spesa"])

with tabview:
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # ------------------------------ entrate uscite ------------------------------ #
        dataframe = pd.read_excel(
            uploaded_file, skiprows=[0, 1, 2, 3, 4, 5, 6, 8], header=0, index_col=1
        ).rename(columns=renamingdict)
        print(dataframe.head)
        dataframe.loc[:, "DataOperazione"] = dataframe.loc[:, "DataOperazione"].apply(
            lambda x: x.replace(year=2021)
        )
        dataframe.loc[:, "DataRegistrazione"] = dataframe.loc[
            :, "DataRegistrazione"
        ].apply(lambda x: x.replace(year=2021))
        dataframe.loc[:, negativecolumns] = -dataframe.loc[:, negativecolumns]
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
            dataframe.loc[:, analysecolumns + ["Descrizione operazioni"]]
            .groupby("Descrizione operazioni")
            .sum()
        )

        df_melted = pd.melt(
            df_sum.reset_index(),
            id_vars="Descrizione operazioni",
            value_vars=df_sum.reset_index().columns[1:],
            var_name="Column",
            value_name="Sum",
        )

        st.write("### Ammontare per operazione")

        barplotadjacent = px.bar(
            df_melted, x="Descrizione operazioni", y="Sum", color="Column"
        )
        st.plotly_chart(barplotadjacent)

        st.write("### Entrate e uscite")
        barplotstack = px.bar(
            df_melted,
            x="Column",
            y="Sum",
            color="Descrizione operazioni",
            barmode="stack",
        )
        st.plotly_chart(barplotstack)

        st.write("### Ammontare per singole operazioni")
        st.write(df_sum.transpose())

        # ---------------------------------------------------------------------------- #
        #                                   Entrate                                    #
        # ---------------------------------------------------------------------------- #

        st.write("## Entrate per centri di spesa")
        categoriesdf = dataframe.loc[:, "Quote associative":"Altro"]
        categoriesdf["Descrizione operazioni"] = dataframe["Descrizione operazioni"]

        df_sum_catent = categoriesdf.groupby("Descrizione operazioni").sum()

        df_melted_catent = pd.melt(
            df_sum_catent.reset_index(),
            id_vars="Descrizione operazioni",
            value_vars=df_sum_catent.reset_index().columns[1:],
            var_name="Column",
            value_name="Sum",
        )

        opcolor = st.checkbox("Mostra singole operazioni", key="opcolor")
        if opcolor:
            barplotent = px.bar(
                df_melted_catent, x="Column", y="Sum", color="Descrizione operazioni"
            )
        else:
            barplotent = px.bar(df_melted_catent, x="Column", y="Sum")
        st.plotly_chart(barplotent)

        st.write("### Analisi delle entrate per centri di spesa")
        st.write(categoriesdf.describe())

        # ---------------------------------------------------------------------------- #
        #                                   Uscite                                    #
        # ---------------------------------------------------------------------------- #

        st.write("## Uscite per centri di spesa")
        categoriesdf = dataframe.loc[:, "Cancelleria":"Altro.1"]
        categoriesdf["Descrizione operazioni"] = dataframe["Descrizione operazioni"]

        df_sum_catent = categoriesdf.groupby("Descrizione operazioni").sum()

        df_melted_catent = pd.melt(
            df_sum_catent.reset_index(),
            id_vars="Descrizione operazioni",
            value_vars=df_sum_catent.reset_index().columns[1:],
            var_name="Column",
            value_name="Sum",
        )

        opcolor = st.checkbox("Mostra singole operazioni", key="opcoloruscite")
        if opcolor:
            barplotent = px.bar(
                df_melted_catent, x="Column", y="Sum", color="Descrizione operazioni"
            )
        else:
            barplotent = px.bar(df_melted_catent, x="Column", y="Sum")
        st.plotly_chart(barplotent)

        st.write("### Analisi delle uscite per centri di spesa")
        st.write(categoriesdf.describe())

with tabadd:
    # ----------------------------------- intro ---------------------------------- #
    st.write("## Bozza form per inserimento spesa")
    # st.write("valori positivi inseriscono entrate, valori negativi inseriscono uscite")
    # --------------------------------- dataframe -------------------------------- #
    try:
        dfadd = pd.read_feather("dfadd.feather")
    except Exception as e:
        dfadd = pd.DataFrame(
            columns=[
                "Descrizione operazione",
                "Data operazione",
                "Conto",
                "Categoria",
                "Spesa",
            ]
        )
    dfaddanalysis = pd.DataFrame()
    # --------------------------------- funzioni --------------------------------- #
    containervalue = st.container()
    opzionientrata = [
        "Quote associative",
        "Erogazioni liberari",
        "Webinar e corsi",
        "Contributi pubblici",
        "Interessi attivi",
        "Attività economica",
        "Cessione a terzi beni di modesto valore/oggettistica",
        "Partecipazione Workshop/bioblitz",
    ]
    opzioniuscita = [
        "Cancelleria",
        "Attrezzatura e spese tipografiche",
        "Postali e bollati",
        "Imposte e tasse",
        "Spese bancarie",
        "Costi informatici",
        "Costi Trasferte Missioni (viaggi+pasti)",
        "Compensi professionali",
        "Altro",
    ]

    # ----------------------------------- form ----------------------------------- #
    descrizione = st.text_input("Descrizione operazione")
    data = st.date_input("Data operazione")
    conto = st.selectbox("Conto", options=["Cassa", "Banca Prossima", "Paypal"])
    with containervalue:
        valore = st.number_input("Valore", key="valore")
        categoria = st.selectbox(
            "Categoria",
            options=opzionientrata + opzioniuscita,
            key="categoria",
        )
    submit = st.button("Submit")

    # ---------------------------------- valori ---------------------------------- #
    if submit:
        row = pd.DataFrame(
            data={
                "Descrizione operazione": descrizione,
                "Data operazione": data,
                "Conto": conto,
                "Categoria": categoria,
                "Spesa": valore,
            },
            index=[0],
        )
        dfadd = pd.concat(
            [dfadd, row],
            ignore_index=True,
        )
        dfadd.to_feather("dfadd.feather")
    st.data_editor(dfadd)

    dfanalysis = (
        dfadd
        .groupby("Conto")["Spesa"]
        .cumsum(axis=0)
    ).transform(pd.DataFrame).rename({"Spesa": "Saldo Conto"}, axis=1)
    dfanalysis["Totale"] = dfadd["Spesa"].cumsum()
    st.write("### Tabella con Saldo cumulativo e Totale")
    st.write(pd.concat([dfadd, dfanalysis], axis=1))
    # dfanalysis["Conto"] = dfadd["Conto"]
    st.write("### Valore corrente per Conto")
    st.write(pd.concat([dfadd, dfanalysis], axis=1).groupby("Conto")["Spesa"].agg("sum").rename({"Spesa": "Saldo"}, axis=0))
    st.write("### Valore corrente per Categoria")
    st.write(pd.concat([dfadd, dfanalysis], axis=1).groupby("Categoria")["Spesa"].agg("sum").rename({"Spesa": "Saldo"}, axis=0))

    st.bar_chart(dfadd, x="Categoria", y="Spesa")
