import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

import driftmlp
import folium
def get_network(_str_append):
    network = driftmlp.network_from_file('transition_'+_str_append+'.GraphML', visual=False)
    return network

class interactive_app:
    def __init__(self):
        self.network = None
        self.network_type = None
        self.__name__ = 'interactive_app'

    def __call__(self, lon_from, lat_from, lon_to, lat_to, network_type):
        ### This is relatively expensive so only do it when needed
        if network_type != self.network_type or self.network is None:
            self.network = get_network(network_type)
            self.network_type = network_type

        from_loc = (lon_from, lat_from)
        to_loc = (lon_to, lat_to)
        path = driftmlp.shortest_path.SingleSP(self.network, from_loc, to_loc)
        if path.sp.travel_time != -1:
            m = path.plot_folium()
        else:
            m = folium.Map(
            location=[lat_from, lon_from],
            zoom_start=5,
            tiles="cartodbpositron",
            )
        folium.Marker([lat_from, lon_from],
                       popup="Starting point",
                         color="blue",
                        icon=folium.DivIcon(html=f"""<div style="font-family: courier new">Start</div>""") 
                         ).add_to(m) 
        folium.Marker([lat_to, lon_to],
                       popup="Ending point",
                       color="red",
                       icon=folium.DivIcon(html=f"""<div style="font-family: courier new">End</div>""") 
                       ).add_to(m)
        return m, path

app = interactive_app()

tab1, tab2 = st.tabs(["🌍 Map", "📖	About"])
with tab1:
    col1, col2 = st.columns([3,1])
    with col2:
        p = st.radio(
            label = "Which Drifters to include?",
            options=['No Drogued Drifters', 'Drogued Drifters', 'Both Drogued and Undrogued'],
        )
        options_map = {"No Drogued Drifters": "nodrg",
                        "Drogued Drifters": "drg",
                        "Both Drogued and Undrogued": "both"}
        lon_from=st.slider(label ="lon_from", value=-38.35, min_value=-180.0, max_value=180.0)
        lat_from = st.slider(label = "lat_from", value=43.41, min_value=-80.0, max_value=80.0)
        lon_to = st.slider(label ="lon_to", value=-19.55, min_value=-180.0, max_value=180.0)
        lat_to = st.slider(label = "lat_to", value=-52.0, min_value=-80.0, max_value=80.0)

    map, path = app(lon_from=lon_from, lat_from=lat_from, lat_to=lat_to, lon_to=lon_to, network_type=options_map[p])
    with col1:
        if path.sp.travel_time!=-1:
            st.write(f"Travel Time Forward (Blue & Start -> End): {round(path.sp.travel_time,1)} days")
        else:
            st.write("No Forward Path Found")

        if path.sp_rev.travel_time!=-1:
            st.write(f"Travel Time Return (Red & End -> Start): {round(path.sp_rev.travel_time,1)} days")
        else:
            st.write("No Return Path Found")

        folium_static(map, width=500)
with tab2:
    """
    **Instructions**

    Select two locations using the four sliders below. Upon releasing the mouse a map will be shown displaying the most likely pathway from the transition matrix. The blue pathway shows the path going from (lon_from, lat_from) to (lon_to, lat_to); the red pathway shows the return. The two points are shown in the top plot; from in blue, to in red.

    Use the dropdown menu to select which drifter data subset to use to estimate the transition matrix.

    - Drogued drifters will give pathways corresponding to top 15m flows. The drifters in this dataset have less of a wind forcing.
    - Undrogued drifters will give pathways corresponding to near surface flows, with a stronger influence from the surface stress winds.
    - Both is simply just a mixture of both datasets.
    Typically undrogued drifters and the both options will have shorter travel times.

    For more information go to https://github.com/MikeOMa/DriftMLP for the source package of this app. 

    Or read the paper at 
    
    O’Malley, M., A. M. Sykulski, R. Laso-Jadart, and M. Madoui, 2021: Estimating the Travel Time and the Most Likely Path from Lagrangian Drifters. J. Atmos. Oceanic Technol., 38, 1059–1073, https://doi.org/10.1175/JTECH-D-20-0134.1.
    """
