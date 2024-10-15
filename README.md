# STKG-LLKG

![Linked Linguistic Knowledge Graph](/doc/img/LLKG.svg "Linked Linguistic Knowledge Graph")  

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