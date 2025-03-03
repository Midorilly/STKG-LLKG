# STKG-LLKG

![Linked Linguistic Knowledge Graph](/doc/img/llkg-new-palette.svg "Linked Linguistic Knowledge Graph")  

**Linked Linguistic Knowledge Graph**

Project Organization
------------

    ├── data               
        ├── lkg             <- Input resource.
        ├── etymwn          <- Input resource.
        ├── lexvo           <- Input resource.
        └── llkg            <- Output resource.
    ├── doc                 <- Project documentation.  
    ├── schema              <- LLKG schema.
    ├── src                 <- Code for generating LLKG resource.
    |   └── utils           <- Code for reorganising EtymWordNet data.
    ├── .gitignore
    ├── README.md
    └── requirements.txt


To run
------------
On Windows
1. Install the requirements with `pip install -r requirements.txt`
2. Download [Etymological WordNet](http://etym.org/) and [Lexvo .nt dump](http://lexvo.org/linkeddata/resources.html) resources and store them in the `data` directory
3. Generate the LLKG with `python3 src/generate.py`

Citation
------------
```
Ghizzota, E., Basile, P., d'Amato, C., & Fanizzi, N. (2025). 
Linked Linguistic Knowledge Graph (1.0.0) [Data set]. 
Global WordNet Conference 2025 (GWC2025), Pavia, Italy. Zenodo. 
```
LLKG can be downloaded from [Zenodo](https://doi.org/10.5281/zenodo.14623212).