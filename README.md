# STKG-LLKG

![Linked Linguistic Knowledge Graph](/doc/img/LLKG.svg "Linked Linguistic Knowledge Graph")  

**Linked Linguistic Knowledge Graph**

Project Organization
------------

    ├── data               
        ├── lkg             <- Input resource.
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
2. Generate the graph with `python3 src/generate.py`