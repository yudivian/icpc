import streamlit as st
import json
import statistics as stats

import plotly.express as px
import plotly.graph_objects as go
import graphviz as gv


with open("data/data-2006-2024.json", "r") as file:
    data = json.load(file)

contests = data["contests"]
regions = data["regions"]
countries = data["countries"]
cstats = data["stats"]

years = [int(x) for x in contests]

minimal = 2010
maximal = max(years)


def get_contests_from_period(first=minimal, last=maximal):
    return {x: y for x, y in contests.items() if first <= int(x) <= last}


def get_university_participations(university, contests):
    cu = {}
    for y, c in contests.items():
        for u in c:
            if u["university"] == university:
                cu[y] = u
    return cu

def get_university_graph(university_contest,name):
    g1 = gv.Digraph(name+"-parent")
    c1 = gv.Digraph(name+"-child")
    c1.attr(rank="same")
    for y in range(2010, 2025):
        if not str(y) in university_contest:
            c1.node(str(y), shape="square")
        else:
            c1.node(str(y), shape="square", style="filled", fillcolor="#40e0d0")
    fr = 2010
    for y in range(2011, 2025):
        c1.edge(str(fr), str(y), style="invis")
        fr = y
    for y1 in range(2010,2024):
        for y2 in range(y1+1,2025):
            if (str(y1) in university_contest) and (str(y2) in university_contest):
                s1 = set(university_contest[str(y1)]["players"])
                s2 = set(university_contest[str(y2)]["players"])
                s =  s1.intersection(s2)
                if len(s)!=0:
                    c1.edge(str(y1),str(y2),label=str(len(s)))
    g1.subgraph(c1)
    return g1


with st.container(border=True):
    st.text("Participaciones por país")

    with st.expander("Parámetros:"):
        minimal_parts = (
            st.session_state["minimal_parts"]
            if "minimal_parts" in st.session_state
            else 10
        )

        first, last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
        )

        participations = [i for i in range(1, last - first + 2)]

        if minimal_parts < last - first + 1:
            ind = participations.index(minimal_parts)
        else:
            ind = participations.index(last - first + 1)

        min_parts = st.selectbox(
            "Seleccione la cantidad de participaciones mínima",
            options=participations,
            index=ind,
        )

        st.session_state["minimal_parts"] = min_parts

        d_regions = {regions[x]["spanish_name"]: x for x in regions}
        n_regions = ["Todas"] + [x for x in d_regions]

        s_regions = st.multiselect(
            "Selecione las regiones", options=n_regions, default=["Todas"]
        )

    with st.expander("Gráfico:"):
        c_countries = {}
        for year in range(first, last + 1):
            year = str(year)
            country_set = set()
            for team in contests[year]:
                c = team["country"]
                if not c in country_set:
                    country_set.add(c)
                    if c in c_countries:
                        c_countries[c] += 1
                    else:
                        c_countries[c] = 1

        if "Todas" not in s_regions:
            c_countries = {
                x: y
                for x, y in c_countries.items()
                if regions[countries[x]["region"]]["spanish_name"] in s_regions
            }

        x_c = []
        y_c = []
        c_items = [i for i in c_countries.items() if i[1] >= min_parts]
        c_items.sort(key=lambda x: x[1])

        for item in c_items:
            x_c.append(item[1])
            y_c.append(item[0])

        fig = go.Figure(go.Bar(x=x_c, y=y_c, orientation="h"))

        fig.update_layout(
            margin={"t": 0, "l": 0},
            height=450 if 450 > 18 * len(x_c) else 18 * len(x_c),
        )

        st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.text("Participaciones por universidades")

    with st.expander("Parámetros:"):
        minimal_u_parts = (
            st.session_state["minimal_u_parts"]
            if "minimal_u_parts" in st.session_state
            else 10
        )

        u_first, u_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="u_part_period",
        )

        u_participations = [i for i in range(1, u_last - u_first + 2)]

        if minimal_u_parts < u_last - u_first + 1:
            u_ind = u_participations.index(minimal_u_parts)
        else:
            u_ind = u_participations.index(u_last - u_first + 1)

        u_min_parts = st.selectbox(
            "Seleccione la cantidad de participaciones mínima",
            options=u_participations,
            index=u_ind,
            key="u_part_min",
        )

        st.session_state["minimal_u_parts"] = u_min_parts

        u_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        u_n_regions = ["Todas"] + [x for x in u_d_regions]

        u_s_regions = st.multiselect(
            "Selecione las regiones",
            options=u_n_regions,
            default=["Todas"],
            key="u_part_regions",
        )

    with st.expander("Gráfico:"):
        universities = {}
        for year in range(u_first, u_last + 1):
            year = str(year)
            for team in contests[year]:
                c = team["university"]
                if c in universities:
                    universities[c]["count"] += 1
                else:
                    universities[c] = {"count": 1, "country": team["country"]}

        if "Todas" not in u_s_regions:
            universities = {
                x: y
                for x, y in universities.items()
                if regions[countries[y["country"]]["region"]]["spanish_name"]
                in u_s_regions
            }

        x_u = []
        y_u = []
        u_items = [i for i in universities.items() if i[1]["count"] >= u_min_parts]
        u_items.sort(key=lambda x: x[1]["count"])
        for item in u_items:
            x_u.append(item[1]["count"])
            y_u.append(item[0])

        fig_u = go.Figure(go.Bar(x=x_u, y=y_u, orientation="h"))

        fig_u.update_layout(
            margin={"t": 0, "l": 0},
            height=700 if 700 > 18 * len(x_u) else 18 * len(x_u),
        )

        st.plotly_chart(fig_u, use_container_width=True)

with st.container(border=True):
    st.text("Problemas resueltos por universidad")

    with st.expander("Parámetros:"):
        p_first, p_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="p_part_period",
        )

        p_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        p_n_regions = ["Todas"] + [x for x in p_d_regions]

        p_s_regions = st.multiselect(
            "Selecione las regiones para estadísticas generales",
            options=p_n_regions,
            default=["Todas"],
            key="p_part_regions",
        )

        p_contests = get_contests_from_period(p_first, p_last)

        m_p_univs = (
            st.session_state["m_p_univs"] if "m_p_univs" in st.session_state else []
        )

        p_univs = set()
        for x, c in p_contests.items():
            for team in c:
                p_univs.add(team["university"])

        p_univs = st.multiselect(
            "Selecciona las universidades:",
            options=list(p_univs),
            # default=m_p_univs
        )
        # st.session_state["m_p_univs"]=p_univs

    with st.expander("Gráfico:"):
        p_max = []
        p_mode = []
        p_mean = []
        p_median = []
        p_min = []
        d_univs = {u: [] for u in p_univs}

        for x, c in p_contests.items():
            l_univs = [i for i in p_univs]
            p_solves = []
            for team in c:
                if team["university"] in l_univs:
                    d_univs[team["university"]].append(team["solved"])
                    l_univs.remove(team["university"])
                if "Todas" not in p_s_regions:
                    c_reg = regions[countries[team["country"]]["region"]][
                        "spanish_name"
                    ]
                    if c_reg in p_s_regions:
                        p_solves.append(int(team["solved"]))
                else:
                    p_solves.append(int(team["solved"]))
            for u in l_univs:
                d_univs[u].append(None)
            if len(p_solves) != 0:
                p_max.append(max(p_solves))
                p_min.append(min(p_solves))
                p_mode.append(stats.mode(p_solves))
                p_mean.append(stats.mean(p_solves))
                p_median.append(round(stats.median(p_solves)))

        years = [y for y in range(p_first, p_last + 1)]
        pfig = go.Figure()
        pfig.add_trace(
            go.Scatter(x=years, y=p_min, name="Mínimo", mode="lines+markers")
        )
        pfig.add_trace(
            go.Scatter(x=years, y=p_max, name="Máximo", mode="lines+markers")
        )
        pfig.add_trace(go.Scatter(x=years, y=p_mode, name="Moda", mode="lines+markers"))
        pfig.add_trace(
            go.Scatter(x=years, y=p_median, name="Mediana", mode="lines+markers")
        )
        pfig.add_trace(
            go.Scatter(x=years, y=p_mean, name="Media", mode="lines+markers")
        )
        for u, s in d_univs.items():
            pfig.add_bar(x=years, y=s, name=u)
        pfig.update_xaxes(showgrid=True, dtick=1)
        pfig.update_layout(
            legend=dict(orientation="h"),
            margin={"t": 0, "l": 0},
            xaxis_title="Ediciones",
            yaxis_title="Problemas resueltos",
        )
        st.plotly_chart(pfig, use_container_width=True)


with st.container(border=True):
    st.text("Lugar general por universidades")

    with st.expander("Parámetros:"):
        po_first, po_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="po_period",
        )

        po_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        po_n_regions = ["Todas"] + [x for x in po_d_regions]

        po_s_region = st.multiselect(
            "Selecione la región a analizar",
            options=p_n_regions,
            default=["Todas"],
            key="po_part_regions",
        )

        po_contests = get_contests_from_period(po_first, po_last)

        po_univs = set()
        for x, c in po_contests.items():
            for team in c:
                if (
                    "Todas" in po_s_region
                    or regions[countries[team["country"]]["region"]]["spanish_name"]
                    in po_s_region
                ):
                    po_univs.add(team["university"])

        po_univs = st.multiselect(
            "Selecciona las universidades:",
            options=list(po_univs),
            key="po_multiselect",
            # default=m_p_univs
        )

    with st.expander("Gráficos:"):
        pu_univs = {u: {"place": [], "solved": []} for u in po_univs}
        quartiles4 = []
        quantities = {int(x): [] for x in po_contests}
        for x, c in po_contests.items():
            lo_univs = [i for i in pu_univs]
            ind = 0
            for t in c:
                if (
                    "Todas" in po_s_region
                    or regions[countries[t["country"]]["region"]]["spanish_name"]
                    in po_s_region
                ):
                    ind += 1
                    quantities[int(x)].append(int(t["solved"]))
                    if t["university"] in lo_univs:
                        pu_univs[t["university"]]["place"].append(ind)
                        pu_univs[t["university"]]["solved"].append(int(t["solved"]))
                        lo_univs.remove(t["university"])
            quartiles4.append(ind)
            for u in lo_univs:
                pu_univs[u]["place"].append(None)
                pu_univs[u]["solved"].append(None)

        years = [y for y in range(po_first, po_last + 1)]
        quartiles1 = []
        quartiles2 = []
        quartiles3 = []
        for n in quartiles4:
            quartiles1.append(int(n / 4))
            quartiles2.append(int(n / 4 * 2))
            quartiles3.append(int(n / 4 * 3))
        po_fig = go.Figure()
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles1,
                name="Cuartil 1",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(130, 200, 254, 0.5)",
                line=dict(color="rgba(130, 200, 254, 1)"),
            )
        )
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles2,
                name="Cuartil 2",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(0, 101, 195, 0.5)",
                line=dict(color="rgba(0, 101, 195, 1)"),
            )
        )
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles3,
                name="Cuartil 3",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(255, 171, 171, 0.5)",
                line=dict(color="rgba(255, 171, 171, 1)"),
            )
        )
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles4,
                name="Cuartil 4",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(250, 42, 42, 0.5)",
                line=dict(color="rgba(250, 42, 42, 1)"),
            )
        )
        for u, v in pu_univs.items():
            po_fig.add_trace(go.Scatter(x=years, y=v["place"], name=u, mode="markers"))
        po_fig.update_xaxes(showgrid=True, dtick=1)
        po_fig.update_yaxes(autorange="reversed")
        po_fig.update_layout(
            legend=dict(orientation="h"),
            margin={"t": 0, "l": 0},
            xaxis_title="Ediciones",
            yaxis_title="Lugar",
        )
        st.text("Distribución por ubicación")
        st.plotly_chart(po_fig, use_container_width=True)

        if len(po_s_region) != 0:
            quantities1 = []
            quantities2 = []
            quantities3 = []
            quantities4 = []

            i = 0
            for y in years:
                p = quantities[y]
                p.sort(reverse=True)
                quantities1.append(p[0])
                quantities2.append(p[quartiles1[i] + 1])
                quantities3.append(p[quartiles2[i] + 1])
                quantities4.append(p[quartiles3[i] + 1])
                i += 1

            ps_fig = go.Figure()
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities4,
                    name="Cuartil 4",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(250, 42, 42, 0.5)",
                    line=dict(color="rgba(250, 42, 42, 1)"),
                )
            )
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities3,
                    name="Cuartil 3",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(255, 171, 171, 0.5)",
                    line=dict(color="rgba(255, 171, 171, 1)"),
                )
            )
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities2,
                    name="Cuartil 2",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(0, 101, 195, 0.5)",
                    line=dict(color="rgba(0, 101, 195, 1)"),
                )
            )
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities1,
                    name="Cuartil 1",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(130, 200, 254, 0.5)",
                    line=dict(color="rgba(130, 200, 254, 1)"),
                )
            )
            for u, v in pu_univs.items():
                ps_fig.add_trace(
                    go.Scatter(x=years, y=v["solved"], name=u, mode="markers")
                )
            ps_fig.update_xaxes(showgrid=True, dtick=1)
            ps_fig.update_layout(
                legend=dict(orientation="h"),
                margin={"t": 0, "l": 0},
                xaxis_title="Ediciones",
                yaxis_title="Problemas resueltos",
            )
            st.text("Distribución por problemas resueltos")
            st.plotly_chart(ps_fig, use_container_width=True)

with st.container(border=True):
    st.text("Acumulado de problemas resueltos")

    with st.expander("Parámetros:"):
        a_first, a_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="a_period",
        )

        a_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        a_n_regions = ["Todas"] + [x for x in a_d_regions]

        a_s_region = st.multiselect(
            "Selecione la región a analizar",
            options=a_n_regions,
            default=["Todas"],
            key="a_part_regions",
        )

        a_contests = get_contests_from_period(a_first, a_last)
        a_univs = {}
        for x, c in a_contests.items():
            for t in c:
                if (
                    "Todas" in a_s_region
                    or regions[countries[t["country"]]["region"]]["spanish_name"]
                    in a_s_region
                ):
                    if t["university"] in a_univs:
                        a_univs[t["university"]]["solved"] += int(t["solved"])
                        a_univs[t["university"]]["total"] += len(cstats[x]["problems"])
                    else:
                        a_univs[t["university"]] = {
                            "solved": int(t["solved"]),
                            "total": len(cstats[x]["problems"]),
                        }
        amount = 0
        if a_univs:
            amount = st.slider(
                "Cantidad de lugares a mostrar",
                min_value=1,
                max_value=len(a_univs),
                value=len(a_univs) if len(a_univs) < 50 else 50,
            )

    with st.expander("Gráficos:"):

        prob_solv = [(x, y["solved"]) for x, y in a_univs.items()]
        perc_solv = [(x, y["solved"] * 100 / y["total"]) for x, y in a_univs.items()]
        prob_solv.sort(key=lambda x: x[1], reverse=True)
        perc_solv.sort(key=lambda x: x[1], reverse=True)

        if len(prob_solv) < amount:
            y_a = [c[0] for c in prob_solv]
            x_a = [c[1] for c in prob_solv]
            y_pe = [c[0] for c in perc_solv]
            x_pe = [c[1] for c in perc_solv]
        else:
            y_a = [c[0] for c in prob_solv[:amount]]
            x_a = [c[1] for c in prob_solv[:amount]]
            y_pe = [c[0] for c in perc_solv[:amount]]
            x_pe = [c[1] for c in perc_solv[:amount]]

        a_fig = go.Figure(go.Bar(x=x_a, y=y_a, orientation="h"))
        a_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=600 if 600 > 18 * len(x_a) else 18 * len(x_a),
        )
        a_fig.update_yaxes(autorange="reversed")

        st.text("Por total de problemas resueltos")
        st.plotly_chart(a_fig, use_container_width=True)

        ape_fig = go.Figure(go.Bar(x=x_pe, y=y_pe, orientation="h"))
        ape_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=600 if 600 > 18 * len(x_pe) else 18 * len(x_pe),
        )
        ape_fig.update_yaxes(autorange="reversed")

        st.text("Por porciento de problemas resueltos")
        st.plotly_chart(ape_fig, use_container_width=True)

with st.container(border=True):
    st.text("Miembros de los equipos")

    with st.expander("Parámetros:"):
        t_first, t_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="t_period",
        )

        t_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        t_n_regions = ["Todas"] + [x for x in t_d_regions]

        t_s_region = st.multiselect(
            "Selecione la región a analizar",
            options=a_n_regions,
            default=["Todas"],
            key="t_part_regions",
        )

        teams = {}
        t_contests = get_contests_from_period(t_first, t_last)
        for x, c in t_contests.items():
            for t in c:
                if (
                    "Todas" in t_s_region
                    or regions[countries[t["country"]]["region"]]["spanish_name"]
                    in t_s_region
                ):
                    if t["university"] in teams:
                        teams[t["university"]]["teams"] += 1
                        repeated = False
                        for s in t["players"]:
                            if s in teams[t["university"]]["players"]:
                                teams[t["university"]]["repeated_players"] += 1
                                if not repeated:
                                    teams[t["university"]]["repeated"] += 1
                                    repeated = True
                            else:
                                teams[t["university"]]["players"].add(s)
                    else:
                        teams[t["university"]] = {
                            "players": set(),
                            "teams": 1,
                            "repeated": 0,
                            "repeated_players": 0,
                        }
                        for s in t["players"]:
                            teams[t["university"]]["players"].add(s)

        t_amount = 0
        if teams:
            t_amount = st.slider(
                "Cantidad de lugares a mostrar",
                min_value=1,
                max_value=len(teams),
                value=len(teams) if len(teams) < 50 else 50,
                key="t_slider",
            )

    with st.expander("Gráficos:"):
        t_repeated_teams = [
            (x, y["repeated"]) for x, y in teams.items() if y["repeated"] != 0
        ]
        t_percent_repeated_teams = [
            (x, y["repeated"] * 100 / y["teams"])
            for x, y in teams.items()
            if y["repeated"] != 0
        ]
        t_repeated_players = [
            (x, y["repeated_players"]) for x, y in teams.items() if y["repeated"] != 0
        ]
        t_percent_repeated_players = [
            (x, y["repeated_players"] * 100 / len(y["players"]))
            for x, y in teams.items()
            if y["repeated"] != 0
        ]

        t_repeated_teams.sort(key=lambda x: x[1], reverse=True)
        t_percent_repeated_teams.sort(key=lambda x: x[1], reverse=True)
        t_repeated_players.sort(key=lambda x: x[1], reverse=True)
        t_percent_repeated_players.sort(key=lambda x: x[1], reverse=True)

        if len(t_repeated_teams) < t_amount:
            y_rt = [c[0] for c in t_repeated_teams]
            x_rt = [c[1] for c in t_repeated_teams]
            y_prt = [c[0] for c in t_percent_repeated_teams]
            x_prt = [c[1] for c in t_percent_repeated_teams]
            y_rp = [c[0] for c in t_repeated_players]
            x_rp = [c[1] for c in t_repeated_players]
            y_prp = [c[0] for c in t_percent_repeated_players]
            x_prp = [c[1] for c in t_percent_repeated_players]
        else:
            y_rt = [c[0] for c in t_repeated_teams[:t_amount]]
            x_rt = [c[1] for c in t_repeated_teams[:t_amount]]
            y_prt = [c[0] for c in t_percent_repeated_teams[:t_amount]]
            x_prt = [c[1] for c in t_percent_repeated_teams[:t_amount]]
            y_rp = [c[0] for c in t_repeated_players[:t_amount]]
            x_rp = [c[1] for c in t_repeated_players[:t_amount]]
            y_prp = [c[0] for c in t_percent_repeated_players[:t_amount]]
            x_prp = [c[1] for c in t_percent_repeated_players[:t_amount]]

        rt_fig = go.Figure(go.Bar(x=x_rt, y=y_rt, orientation="h"))
        rt_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        rt_fig.update_yaxes(autorange="reversed")

        st.text("Total de equipos con miembros participantes en otra edición")
        st.plotly_chart(rt_fig, use_container_width=True)

        prt_fig = go.Figure(go.Bar(x=x_prt, y=y_prt, orientation="h"))
        prt_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        prt_fig.update_yaxes(autorange="reversed")

        st.text("Porciento de equipos con miembros participantes en otra edición")
        st.plotly_chart(prt_fig, use_container_width=True)

        rp_fig = go.Figure(go.Bar(x=x_rp, y=y_rp, orientation="h"))
        rp_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        rp_fig.update_yaxes(autorange="reversed")

        st.text("Total de estudiantes participantes en otra edición")
        st.plotly_chart(rp_fig, use_container_width=True)

        prp_fig = go.Figure(go.Bar(x=x_prp, y=y_prp, orientation="h"))
        prp_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        prp_fig.update_yaxes(autorange="reversed")

        st.text("Porciento de estudiantes participantes en otra edición")
        st.plotly_chart(prp_fig, use_container_width=True)

with st.container(border=True):
    st.text("Secuencia de participaciones por universidad")

    with st.expander("Gráficos:"):

        s_univs = set()
        for x, c in po_contests.items():
            for team in c:
                s_univs.add(team["university"])

        s_univs = list(s_univs)
        hi = s_univs.index("Universidad de La Habana")
        oi = s_univs.index("Universidad de Oriente - Sede Antonio Maceo")

        s1_univs = st.selectbox(
            "Selecciona una universidad:", options=s_univs, index=hi, key="s1_univs"
        )
        
        u1 = get_university_participations(s1_univs, contests)

        try:
            st.graphviz_chart(get_university_graph(u1,"s1"))
        except:
            pass

        s2_univs = st.selectbox(
            "Selecciona otra universidad:", options=s_univs, index=oi, key="s2_univs"
        )
        
        u2 = get_university_participations(s2_univs, contests)
        
        try:
            st.graphviz_chart(st.graphviz_chart(get_university_graph(u2,"s2")))
        except:
            pass

#Angélica
with st.container(border=True):
    st.text("Cantidad de universidades finalistas por país")

    with st.expander("Parámetros:"):
        st.text("Expander para parámetros")

    with st.expander("Gráficos:"):
        st.text("Expander para parámetros")

#Alberto
with st.container(border=True):
    st.text("Posiciones y medallas por universidades")

    with st.expander("Parámetros:"):
        st.text("Expander para parámetros")

    with st.expander("Gráficos:"):
        st.text("Expander para parámetros")

    