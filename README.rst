#####################
AMG-232 Documentation
#####################

Introduction
************
This utility will read in a Ion Torrent Variant Caller (TVC) file, and generate
a TP53 report suitable for the AMG-232 Studies.  

..note:
    More formal docs coming soon!

Running the Utility
*******************
<text>

Requirements
************
The following packages and tools are required to run this plugin:
    - vcftools
    - vcfExtractor.pl
    - JSON::XS
    - Annovar

Annovar Databases:

    - hg19_clinvar_20170905
    - hg19_cosmic85 (will have to be custom built)
    - hg19_ensGene, hg19_ensGeneMrna, and hg19_knownGene (from standard Annovar build).
    - hg19_popfreq_all_20150413
    - hg19_refGene, hg19_refGeneMrna, and hg19_refGeneVersion (from standard Annovar build).
