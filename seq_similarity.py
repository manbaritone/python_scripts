#!/usr/bin/env python
# 2016-01-14 Chengxin Zhang
'''Generate Sequence Similarity Report for FASTA alignment file'''
import Bio.SeqIO # parse FASTA file
import sys
import numpy
import numpy.matlib

def seq_similarity(infile="seq.fasta",countgap="false"):
    '''Calculate Sequence Similarity matrix from FASTA alignment file'''
    seq_list=[str(e.seq).upper() for e in Bio.SeqIO.parse(infile,"fasta")]
    seq_num=len(seq_list)
    res_num=len(seq_list[0])

    int_array=numpy.array([numpy.array([ord(a) for a in line]) \
        for line in seq_list])

    Code_aa='ARNDCQEGHILKMFPSTWYV-';
    aa_array=dict()
    for aa in Code_aa:
        aa_array[aa]=numpy.zeros([seq_num,res_num])
        for ii in range(seq_num):
            aa_array[aa][ii][numpy.where(int_array[ii]==ord(aa))]=1

    id_matrix=numpy.zeros([seq_num,seq_num])
    for a in Code_aa:
        id_matrix+=aa_array[a].dot(aa_array[a].T)

    res_num_matrix=float(res_num)*numpy.ones([seq_num,seq_num])
    if   countgap.lower()=="true":
        gap_matrix=aa_array['-'].dot(aa_array['-'].T)
        id_matrix=(id_matrix-gap_matrix)/(res_num_matrix-gap_matrix)
    elif countgap.lower()=="false":
        gap_matrix=res_num_matrix-(1-aa_array['-']).dot((1-aa_array['-']).T)  
        id_matrix=(id_matrix-aa_array['-'].dot(aa_array['-'].T)
            )/(res_num_matrix-gap_matrix)
    
    return id_matrix

"""
def seq_similarity_slow(infile="seq.fasta",countgap="false"):
    '''Calculate Sequence Similarity matrix from FASTA alignment file'''
    if countgap==True:
        countgap="true"
    elif countgap==False:
        countgap="false"

    seq_list=[str(e.seq).upper() for e in Bio.SeqIO.parse(infile,"fasta")]
    seq_num=len(seq_list)
    res_num=len(seq_list[0])
    #Code_aa='ARNDCQEGHILKMFPSTWYV-';

    int_array=numpy.array([numpy.array([ord(a) for a in line]) \
        for line in seq_list])
    gap_array=numpy.zeros([seq_num,res_num])
    for ii in range(seq_num):
        gap_array[ii][numpy.where(int_array[ii]==ord('-'))]=1

    id_matrix=numpy.zeros([seq_num,seq_num])
    for i in range(len(seq_list)):
        for j in range(i,len(seq_list)):
            id_matrix[i][j]=numpy.array(int_array[i]==int_array[j]).sum()
            id_matrix[j][i]=id_matrix[i][j]

    res_num_matrix=float(res_num)*numpy.ones([seq_num,seq_num])
    if   countgap.lower()=="true":
        gap_matrix=gap_array.dot(gap_array.T)
        id_matrix=(id_matrix-gap_matrix)/(res_num_matrix-gap_matrix)
    elif countgap.lower()=="false":
        gap_matrix=res_num_matrix-(1-gap_array).dot((1-gap_array).T)  
        id_matrix=(id_matrix-gap_array.dot(gap_array.T)
            )/(res_num_matrix-gap_matrix)
    
    return id_matrix
"""

def check_alignment(infile="seq.fasta"):
    '''Check whether input FASTA is an alignment (all sequences has equal length)'''
    len_list=[len(e.seq) for e in Bio.SeqIO.parse(infile,"fasta")]
    return max(len_list)==min(len_list)

def get_header(infile="seq.fasta"):
    return [e.id for e in Bio.SeqIO.parse(infile,"fasta")]

if __name__=="__main__":
    if len(sys.argv)<2:
        print >>sys.stderr,'''
seq_similarity [options] alignment.fasta
Generate Sequence Similarity Matrix for FASTA alignment file

Options:
    -seqname={none,index,name}   do not label column/row, label columns 
        using sequence "index", or using "header" of sequence

    -outfmt={matrix,list,first}  output format
        "matrix" - all against all, matrix format
        "list"   - all against all, first & second column for sequence index,
                   third column for sequence similarity
        "first"   - all against the first sequence

    -countgap={false,true}       whether counting gaps as residues. e.g.
        >seq1
        AA-TT-    Identity=2/3 if countgap==false, for sequence length==3
        >seq2     Identity=2/5 if countgap==true,  for sequence length==5
        ACAT--
    
    -eliminator={space,tab}      using "tab" or "space" as text eliminator
'''
        exit()
    if not check_alignment(sys.argv[-1]):
        print >>sys.stderr,"ERROR! Unaligned sequences."
        exit()
    
    seqname="none"
    outfmt="matrix"
    countgap="false"
    eliminator="space"
    for arg in sys.argv[1:-1]:
        if arg.startswith("-seqname="):
            seqname=arg[len("-seqname="):]
        elif arg.startswith("-outfmt="):
            outfmt=arg[len("-outfmt="):]
        elif arg.startswith("-countgap="):
            countgap=arg[len("-countgap="):]
        elif arg.startswith("-eliminator="):
            eliminator=arg[len("-eliminator="):]
        else:
            print >>sys.stderr,"ERROR! Unknown argument "+arg

    id_matrix=seq_similarity(sys.argv[-1],countgap)

    if   seqname=="index" in str(sys.argv[1:-1]):
        header=[str(e+1).ljust(10)+' ' for e in range(len(id_matrix))]
    elif seqname=="name" in str(sys.argv[1:-1]):
        header=[e+' ' for e in get_header(sys.argv[-1])] if eliminator=="tab" \
            else [e[:10].ljust(10)+' ' for e in get_header(sys.argv[-1])]
    elif seqname=="none":
        header=['' for e in range(len(id_matrix))]

    txt=''
    if outfmt=="list":
        for i in range(len(id_matrix)-1):
            for j in range(i+1,len(id_matrix)):
                txt+=(header[i]+header[j])+ \
                ('%.7f'%id_matrix[i][j]+'\n' if id_matrix[i][j]!=1 else "1\n")
        if eliminator=="tab":
            txt="Name_1\tName_2\tIdentity\n"+txt
    elif outfmt=="matrix":
        for i,line in enumerate(id_matrix):
            txt+=header[i]+'  '.join(
                [('%.7f'%e if e!=1 else "1        ") for e in line])+'\n'
        if seqname!="none":
            txt='Identity   '+''.join(header)+'\n'+txt
    elif outfmt=="first":
        for line in id_matrix:
            txt+='%.7f\n'%line[0]

    if eliminator=="tab":
        txt='\n'.join(['\t'.join(line.split()) for line in txt.splitlines()])+'\n'
    sys.stdout.write(txt)

