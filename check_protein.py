from Bio import Entrez
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

def check_protein(dna):
    files = set(['NC_000852', 'NC_007346', 'NC_008724', 'NC_009899', 'NC_014637', 'NC_020104', 'NC_023423', 'NC_023640', 'NC_023719', 'NC_027867'])
    
    coding_dna = Seq(dna, IUPAC.unambiguous_dna)
    for filename in files:
        for seq_record in SeqIO.parse("fasta/"+filename+".fasta", "fasta"):
            result =  find_match(dna, seq_record.seq)
            if result:
                return result, seq_record.id
            print("checking in file",seq_record.id)
    return False

def find_match(dna, genome):
    i = n = len(dna)
    while i < len(genome):
        if dna == genome[i-n:i]:
            return i-n, i-1
        i+=1
    return False

