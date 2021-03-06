% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/RNAAssemblyConvert.R
\docType{methods}
\name{RNAAssemblyConvert}
\alias{RNAAssemblyConvert}
\title{Assembly Conversion}
\usage{
RNAAssemblyConvert(
  countMat,
  from = "GRCh37",
  to = "GRCh38",
  organism = "Human"
)
}
\arguments{
\item{countMat}{Input count matrix, with genes as rows and cells as columns.}

\item{from}{The genome assembly of input genes. For human, "GRCh37" (hg19) and "GRCh38" (hg38) are supported.
For mouse, "NCBIM37" (mm9) and "GRCm38" (mm10) are supported. Default is "GRCh37".}

\item{to}{The genome assembly of output genes. For human, "GRCh37" (hg19) and "GRCh38" (hg38) are supported.
For mouse, "NCBIM37" (mm9) and "GRCm38" (mm10)" are supported. Default is "GRCh38".}

\item{organism}{Ogranism used, currently only support "Human" and "Mouse". Default is "Human".}
}
\value{
A matrix of count with gene names converted.
}
\description{
Convert gene symbol between genome assemblies for count matrix.
}
\author{
Dongqing Sun
}
