# -*- coding: utf-8 -*-
# @Author: Chenfei Wang, Changxin Wan
# @E-mail: Dongqingsun96@gmail.com
# @Date:   2020-02-23 19:48:03
# @Last Modified by:   Dongqing Sun
# @Last Modified time: 2020-03-02 01:55:33


import os, sys
import time
import tables
import h5py
import collections
import numpy as np
import scipy.sparse as sp_sparse
import argparse as ap

from pkg_resources import resource_filename

from MAESTRO.scATAC_utility import *
from MAESTRO.scATAC_H5Process import *


def genescore_parser(subparsers):
    """
    Add main function init-scatac argument parsers.
    """

    workflow = subparsers.add_parser("scatac-genescore", 
        help = "Calculate gene score according to scATAC peak count.")
    group_input = workflow.add_argument_group("Input arguments")
    group_input.add_argument("--format", dest = "format", default = "", 
        choices = ["h5", "mtx", "plain"], 
        help = "Format of the count matrix file.")
    group_input.add_argument("--peakcount", dest = "peakcount", default = "", 
        help = "Location of peak count matrix file. "
        "Peak count matrix with peaks as rows and cells as columns. "
        "If the format is 'h5' or 'plain', users need to specify the name of the count matrix file "
        "and row names should be like 'chromosome_peakstart_peakend', such as 'chr10_100020591_100020841'. "
        "If the format is 'mtx', the 'matrix' should be the name of .mtx formatted matrix file, such as 'matrix.mtx'.")
    group_input.add_argument("--feature", dest = "feature", default = "peaks.bed", 
        help = "Location of feature file (required for the format of 'mtx'). "
        "Features correspond to row indices of count matrix. "
        "The feature file should be the peak bed file with 3 columns. DEFAULT: peaks.bed.")
    group_input.add_argument("--barcode", dest = "barcode", default = "barcodes.tsv", 
        help = "Location of barcode file (required for the format of 'mtx'). "
        "Cell barcodes correspond to column indices of count matrix. DEFAULT: barcodes.tsv. ")
    group_input.add_argument("--genedistance", dest = "genedistance", default = 10000, type = int, 
        help = "Gene score decay distance, could be optional from 1kb (promoter-based regulation) "
        "to 10kb (enhancer-based regulation). DEFAULT: 10000.")
    group_input.add_argument("--species", dest = "species", default = "GRCh38", 
        choices = ["GRCh38", "GRCm38"], type = str, 
        help = "Species (GRCh38 for human and GRCm38 for mouse). DEFAULT: GRCh38.")
    

    group_output = workflow.add_argument_group("Output arguments")
    group_output.add_argument("-d", "--directory", dest = "directory", default = "MAESTRO", 
        help = "Path to the directory where the result file shall be stored. DEFAULT: MAESTRO.")
    group_output.add_argument("--outprefix", dest = "outprefix", default = "10x-genomics", 
        help = "Prefix of output files. DEFAULT: MAESTRO.")


def RP(peaks_info, genes_info, decay):
    """Multiple processing function to calculate regulation potential."""

    Sg = lambda x: 2**(-x)
    gene_distance = 15 * decay
    genes_peaks_score_array = sp_sparse.dok_matrix((len(genes_info), len(peaks_info)), dtype=np.float64)

    w = genes_info + peaks_info

    A = {}

    w.sort()
    for elem in w:
        if elem[2] == 1:
            A[elem[-1]] = [elem[0], elem[1]]
        else:
            dlist = []
            for gene_name in list(A.keys()):
                g = A[gene_name]
                tmp_distance = elem[1] - g[1]
                if (g[0] != elem[0]) or (tmp_distance > gene_distance):
                    dlist.append(gene_name)
                else:
                    genes_peaks_score_array[gene_name, elem[-1]] = Sg(tmp_distance / decay)
            for gene_name in dlist:
                del A[gene_name]

    w.reverse()
    for elem in w:
        if elem[2] == 1:
            A[elem[-1]] = [elem[0], elem[1]]
        else:
            dlist = []
            for gene_name in list(A.keys()):
                g = A[gene_name]
                tmp_distance = g[1] - elem[1]
                if (g[0] != elem[0]) or tmp_distance > gene_distance:
                    dlist.append(gene_name)
                else:
                    genes_peaks_score_array[gene_name, elem[-1]] = Sg(tmp_distance / decay)
            for gene_name in dlist:
                del A[gene_name]

    return(genes_peaks_score_array)


def calculate_RP_score(peakmatrix, features, barcodes, gene_bed, decay, score_file):
    """Calculate regulatery potential for each gene based on the single-cell peaks."""

    genes_info = []
    genes_list = []
    for line in open(gene_bed, 'r'):
        line = line.strip().split('\t')
        if not line[0].startswith('#'):
            if line[2] == "+":
                genes_info.append((line[1], int(line[3]), 1, "%s@%s@%s" % (line[5], line[1], line[3])))
            else:
                genes_info.append((line[1], int(line[4]), 1, "%s@%s@%s" % (line[5], line[1], line[4])))
                # gene_info [chrom, tss, 1, gene_unique]
    genes_info = list(set(genes_info))
    for igene in range(len(genes_info)):
        tmp_gene = list(genes_info[igene])
        genes_list.append(tmp_gene[3])
        tmp_gene[3] = igene
        genes_info[igene] = tmp_gene
    genes = list(set([i.split("@")[0] for i in genes_list]))

    peaks_info = []
    cell_peaks = peakmatrix
    peaks_list = features
    cells_list = barcodes
    # cell_peaks = pd.read_csv(peak_file, sep="\t", header=0, index_col=0)
    # cell_peaks[cell_peaks>1] = 1
    # cells_list = list(cell_peaks.columns)
    # peaks_list = [peak for peak in cell_peaks.index if peak.split("_")[1].isdigit()]
    # cell_peaks = sp_sparse.csc_matrix(cell_peaks.loc[peaks_list, :].values)
    for ipeak, peak in enumerate(peaks_list):
        peaks_tmp = peak.decode().rsplit("_",maxsplit=2)
        peaks_info.append([peaks_tmp[0], (int(peaks_tmp[1]) + int(peaks_tmp[2])) / 2.0, 0, ipeak])

    genes_peaks_score_dok = RP(peaks_info, genes_info, decay)
    genes_peaks_score_csr = genes_peaks_score_dok.tocsr()
    genes_cells_score_csr = genes_peaks_score_csr.dot(cell_peaks.tocsr())
    # genes_peaks_score_csc = genes_peaks_score_dok.tocsc()
    # genes_cells_score_csr = genes_peaks_score_csc.dot(cell_peaks).tocsr()
    
    # genes_cells_score_lil = genes_cells_score_csc.tolil()

    score_cells_dict = {}
    score_cells_sum_dict = {}
    # for icell in range(len(cells_list)):
    #     genes_cells_score_lil[:, icell] = np.array(normMinMax(genes_cells_score_lil[:, icell].toarray().ravel().tolist())).reshape((len(genes_list), 1))
    # genes_cells_score_csr = genes_cells_score_lil.tocsr()
    for igene, gene in enumerate(genes_list):
        # score_cells_dict[gene] = list(map(lambda x: x - bgrp_dict[gene], genes_cells_score_csr[igene, :].toarray().ravel().tolist()))
        # score_cells_dict[gene] = genes_cells_score_csr[igene, :].toarray().ravel().tolist()
        score_cells_dict[gene] = igene
        score_cells_sum_dict[gene] = genes_cells_score_csr[igene, :].sum()

    score_cells_dict_dedup = {}
    score_cells_dict_max = {}
    for gene in genes:
        score_cells_dict_max[gene] = float("-inf")

    for gene in genes_list:
        symbol = gene.split("@")[0]
        if score_cells_sum_dict[gene] > score_cells_dict_max[symbol]:
            score_cells_dict_dedup[symbol] = score_cells_dict[gene]
            score_cells_dict_max[symbol] = score_cells_sum_dict[gene]
    gene_symbol = sorted(score_cells_dict_dedup.keys())
    matrix_row = []
    for gene in gene_symbol:
        matrix_row.append(score_cells_dict_dedup[gene])

    score_cells_matrix = genes_cells_score_csr[matrix_row, :]
    # score_cells_matrix = []
    # for gene in gene_symbol:
    #     score_cells_matrix.append(score_cells_dict_dedup[gene])

    write_10X_h5(score_file, score_cells_matrix, gene_symbol, cells_list, genome=gene_bed.split("/")[-1].split("_")[0], datatype="Gene")

    # outf = open(score_file, 'w')
    # outf.write("\t".join(cells_list) + "\n")
    # for symbol in score_cells_dict_dedup.keys():
    #     outf.write(symbol + "\t" + "\t".join(map(str, score_cells_dict_dedup[symbol])) + "\n")
    # outf.close()

def genescore(fileformat, directory, outprefix, peakcount, feature, barcode, genedistance, species):

    try:
        os.makedirs(directory)
    except OSError:
        # either directory exists (then we can ignore) or it will fail in the
        # next step.
        pass
    
    annotation_path = resource_filename('MAESTRO', 'annotations')
    # annotation_path = os.path.join(os.path.dirname(__file__), 'annotations')
    genebed = os.path.join(annotation_path, species + "_ensembl.bed")
    decay = float(genedistance)
    score_file = os.path.join(directory, outprefix + "_gene_score.h5")

    if fileformat == "plain":
        matrix_dict = read_count(peakcount)
        peakmatrix = matrix_dict["matrix"]
        peakmatrix = sp_sparse.csc_matrix(peakmatrix, dtype=numpy.int8)
        features = matrix_dict["features"]
        features = [f.encode() for f in features]
        barcodes = matrix_dict["barcodes"]

    elif fileformat == "h5":
        scatac_count = read_10X_h5(peakcount)
        peakmatrix = scatac_count.matrix
        features = scatac_count.names.tolist()
        barcodes = scatac_count.barcodes.tolist()

    elif fileformat == "mtx":
        matrix_dict = read_10X_mtx(matrix_file = peakcount, feature_file = feature, barcode_file = barcode, datatype = "Peak")
        peakmatrix = matrix_dict["matrix"]
        features = matrix_dict["features"]
        features = [f.encode() for f in features]
        barcodes = matrix_dict["barcodes"]

    calculate_RP_score(peakmatrix, features, barcodes, genebed, decay, score_file)


def main():

    peak_file = sys.argv[1]
    score_file = sys.argv[2]
    decay = float(sys.argv[3])
    gene_bed = sys.argv[4]
    # bgrp_dict = json.load(open(sys.argv[5], "r"))

    start = time.time()
    calculate_RP_score(peak_file, gene_bed, decay, score_file)
    end = time.time()
    print("GeneScore Time:", end - start)

if __name__ == "__main__":
    main()

