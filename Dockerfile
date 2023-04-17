FROM mambaorg/micromamba:1.4.2


ARG MAMBA_DOCKERFILE_ACTIVATE=1
WORKDIR /app

COPY *.GraphML /app/
COPY requirements.txt /app/requirements.txt
COPY streamlit_app.py /app/streamlit_app.py

RUN micromamba install --yes --name base --channel conda-forge \
      cartopy==0.20.0  \
      python=3.9.1 \
      numpy=1.20.0 \
      numba \
      geopandas=0.12.2 \
      streamlit \
      streamlit-folium \
      pandas=1.4.4 && \
    micromamba clean --all --yes
RUN python -m pip install -r /app/requirements.txt


EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "python", "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]

