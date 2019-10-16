#protein check function

def check_protein(dna):
    return False
    protein_set = set(['NC_000852', 'NC_007346', 'NC_008724', 'NC_009899', 'NC_014637', 'NC_020104', 'NC_023423', 'NC_023640', 'NC_023719', 'NC_027867'])
    i = 9
    coding_dna = Seq(dna, IUPAC.unambiguous_dna)
    messenger_rna = coding_dna.transcribe()
    return str(messenger_rna.translate())
    # while i <= len(dna):
    #     if dna[i-9:i] in protein_set:
    #         return dna[i-9:i]
    #     i+=1