# MAESTRO

![GitHub](https://img.shields.io/github/license/liulab-dfci/MAESTRO)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/liulab-dfci/MAESTRO)
[![Conda](https://img.shields.io/conda/dn/liulab-dfci/maestro?label=Conda%20downloads)](https://anaconda.org/liulab-dfci/maestro)
[![Docker Pulls](https://img.shields.io/docker/pulls/winterdongqing/maestro)](https://hub.docker.com/repository/docker/winterdongqing/maestro)

**MAESTRO**(**M**odel-based **A**nalys**E**s of **S**ingle-cell **T**ranscriptome and **R**egul**O**me) is a comprehensive single-cell RNA-seq and ATAC-seq analysis suit built using [snakemake](https://bitbucket.org/snakemake/snakemake/wiki/Home). MAESTRO combines several dozen tools and packages to create an integrative pipeline, which enables scRNA-seq and scATAC-seq analysis from raw sequencing data (fastq files) all the way through alignment, quality control, cell filtering, normalization, unsupervised clustering, differential expression and peak calling, celltype annotation and transcription regulation analysis. Currently, MAESTRO support [Smart-seq2](https://www.ncbi.nlm.nih.gov/pubmed/24385147), [10x-genomics](https://www.10xgenomics.com/solutions/single-cell/), [Drop-seq](https://www.cell.com/abstract/S0092-8674(15)00549-8), [SPLiT-seq](https://science.sciencemag.org/content/360/6385/176) for scRNA-seq protocols; [microfudics-based](https://www.ncbi.nlm.nih.gov/pubmed/26083756), [10x-genomics](https://www.10xgenomics.com/solutions/single-cell-atac/) and [sci-ATAC-seq](https://science.sciencemag.org/content/348/6237/910) for scATAC-seq protocols.       
        
## ChangLog

### v1.0.0
* Release MAESTRO.
### v1.0.1
* Provide [docker image](https://hub.docker.com/repository/docker/winterdongqing/maestro) for easy installation. Note, the docker do not include cellranger/cellrangerATAC, as well as the corresponding genome index. Please install cellranger/cellranger ATAC follow the installation instructions.

## System requirements
* Linux/Unix
* Python (>= 3.0) for MAESTRO snakemake workflow
* R (>= 3.5.1) for MAESTRO R package

## Installation

**Installing the MAESTRO by conda**     

MAESTRO uses the [Miniconda3](http://conda.pydata.org/miniconda.html) package management system to harmonize all of the software packages. 

Use the following commands to the install Minicoda3：
``` bash
$ wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ bash Miniconda3-latest-Linux-x86_64.sh
```
And then users can create an isolated environment for MAESTRO and install through the following commands:
``` bash
$ conda config --add channels defaults
$ conda config --add channels bioconda
$ conda config --add channels conda-forge
$ conda create -n MAESTRO maestro -c liulab-dfci
```

**Installing the MAESTRO R package** 

If users already have the processed datasets, like cell by gene or cell by peak matrix generate by Cell Ranger. Users can install the MAESTRO R package alone to perform the analysis from processed datasets.
``` bash
$ R
> library(devtools)
> install_github("liulab-dfci/MAESTRO")
```

**Installing Cell Ranger**

MAESTRO depends on the Cell Ranger and Cell Ranger ATAC for the mapping of the data generated by 10X Genomics. Please install [Cell Ranger](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/installation) and [Cell Ranger ATAC](https://support.10xgenomics.com/single-cell-atac/software/pipelines/latest/installation) before using MAESTRO. If users have already installed Cell Ranger, please specify the path of Cell Ranger in the YAML configuration file.

**Installing RABIT/LISA**       

MAESTRO utilizes RABIT and LISA to evaluate the enrichment of transcription factors based on the marker genes from scRNA-seq clusters. To run this function, the users need first to install [RABIT](http://rabit.dfci.harvard.edu/), download the RABIT index from [Cistrome website](http://cistrome.org/~chenfei/MAESTRO/rabit.tar.gz), and provide the file location of the index to MAESTRO in the YAML configuration file. Alternatively, users can also use LISA to predict the potential transcription factors that regulate the marker genes from scRNA-seq clusters. Please follow the description at [LISA website](https://github.com/qinqian/lisa) to install and use this function.

**Installing giggle**

MAESTRO utilizes giggle to identify enrichment of transcription factor peaks in scATAC-seq cluster-specific peaks. To run this function, users need first to install [giggle](https://github.com/ryanlayer/giggle), download the giggle index from [Cistrome website](http://cistrome.org/~chenfei/MAESTRO/giggle.tar.gz), and provide the file location of the index to MAESTRO in the YAML configuration file.       

## Galleries & Tutorials (click on the image for details)

[<img src="./image/RNA.10x.png" width="280" height="318" />](./example/RNA_infrastructure_10x/RNA_infrastructure_10x.md)
[<img src="./image/ATAC.10x.png" width="280" height="318" />](./example/ATAC_infrastructure_10x/ATAC_infrastructure_10x.md)
[<img src="./image/integration.10x.png" width="280" height="318" />](./example/Integration/Integration.md)
[<img src="./image/RNA.Smartseq2.png" width="280" height="318" />](./example/RNA_infrastructure_smartseq/RNA_infrastructure_smartseq.md)
[<img src="./image/ATAC.microfludics.png" width="280" height="318" />](./example/ATAC_infrastructure_microfludics/ATAC_infrastructure_microfludics.md)
[<img src="./image/integration.large.png" width="280" height="318" />](./example/Integration_large/Integration_large.md)

## Citation

